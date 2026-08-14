from django.db import models
from fractions import Fraction
from .image_utils import (
    create_webp_variant,
    create_webp_variants_and_exif,
    build_variant_filename,
)
from django.utils import timezone

class Tag(models.Model):
    name = models.CharField(max_length=100)
    name_ja = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.name_ja:
            return f"{self.name} / {self.name_ja}"
        return self.name

class Area(models.Model):
    COLLECTION_CHOICES = [
        ("hiroshima", "Hiroshima"),
        ("japan", "Japan"),
    ]

    collection = models.CharField(
        max_length=20,
        choices=COLLECTION_CHOICES,
        default="hiroshima",
        db_index=True,
    )

    country = models.CharField(
        max_length=100,
        default="Japan",
        db_index=True,
    )

    name = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="areas/",
        blank=True,
        null=True,
    )

    image_large = models.ImageField(
        upload_to="areas/large/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="areas/medium/",
        blank=True,
        null=True,
    )

    image_thumb = models.ImageField(
        upload_to="areas/thumb/",
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="locations",
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="locations",
    )

    name = models.CharField(max_length=200)

    added_at = models.DateTimeField(
        default=timezone.now,
        null=True,
    )

    description = models.TextField(
        verbose_name="Description (English)",
    )

    description_ja = models.TextField(
        blank=True,
        verbose_name="Description (Japanese)",
    )

    address = models.CharField(max_length=300)

    latitude = models.FloatField(
        blank=True,
        null=True,
    )

    longitude = models.FloatField(
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to="locations/",
        blank=True,
        null=True,
    )

    image_large = models.ImageField(
        upload_to="locations/large/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="locations/medium/",
        blank=True,
        null=True,
    )

    image_thumb = models.ImageField(
        upload_to="locations/thumb/",
        blank=True,
        null=True,
    )

    youtube_url = models.URLField(
        blank=True,
        null=True,
    )

    def get_youtube_embed_url(self):
        if not self.youtube_url:
            return None

        url = self.youtube_url.strip()

        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        if "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        if "shorts/" in url:
            video_id = url.split("shorts/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        if "embed" in url:
            return url

        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Photo(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    # Photo Exhibition
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
    )

    exhibition_order = models.PositiveIntegerField(
        default=0,
    )

    image = models.ImageField(upload_to='locations/')

    image_large = models.ImageField(
        upload_to="locations/large/",
        blank=True,
        null=True
    )

    image_medium = models.ImageField(
        upload_to="locations/medium/",
        blank=True,
        null=True
    )

    image_thumb = models.ImageField(
        upload_to="locations/thumb/",
        blank=True,
        null=True
    )

    caption = models.CharField(max_length=200, blank=True)
    camera = models.CharField(max_length=100, blank=True)
    lens = models.CharField(max_length=100, blank=True)
    film = models.CharField(max_length=100, blank=True)
    iso = models.CharField(max_length=50, blank=True)
    aperture = models.CharField(max_length=50, blank=True)
    shutter_speed = models.CharField(max_length=50, blank=True)
    focal_length = models.CharField(max_length=50, blank=True)
    processing_status = models.CharField(
    max_length=20,
    choices=[
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ],
        default="pending",
        db_index=True,
    )

    processing_error = models.TextField(
        blank=True,
        null=True,
    )

    def formatted_aperture(self):
        try:
            return round(float(Fraction(self.aperture)), 1)
        except:
            return self.aperture

    def formatted_focal_length(self):
        try:
            return round(float(Fraction(self.focal_length)))
        except:
            return self.focal_length

    def __str__(self):
        return f"{self.location.name} Photo"

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class About(models.Model):
    title = models.CharField(max_length=200, default="About")
    description = models.TextField()
    image = models.ImageField(upload_to="about/", blank=True, null=True)

    image_large = models.ImageField(upload_to="about/large/", blank=True, null=True)
    image_medium = models.ImageField(upload_to="about/medium/", blank=True, null=True)
    image_thumb = models.ImageField(upload_to="about/thumb/", blank=True, null=True)

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = About.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except About.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_large
            or not self.image_medium
            or not self.image_thumb
        )

        if not should_generate:
            return

        try:
            large = create_webp_variant(self.image, max_width=1800, quality=82)
            medium = create_webp_variant(self.image, max_width=1200, quality=78)
            thumb = create_webp_variant(self.image, max_width=600, quality=75)

            self.image_large.save(
                build_variant_filename(self.image.name, "large"), large, save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"), medium, save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"), thumb, save=False
            )

            super().save(update_fields=["image_large", "image_medium", "image_thumb"])

        except Exception as e:
            print("ABOUT IMAGE VARIANT SKIPPED:", e)

    def __str__(self):
        return self.title

class AboutImage(models.Model):
    about = models.ForeignKey(
        About,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="about/")

    image_large = models.ImageField(upload_to="about/large/", blank=True, null=True)
    image_medium = models.ImageField(upload_to="about/medium/", blank=True, null=True)
    image_thumb = models.ImageField(upload_to="about/thumb/", blank=True, null=True)

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = AboutImage.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except AboutImage.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_large
            or not self.image_medium
            or not self.image_thumb
        )

        if not should_generate:
            return

        try:
            large = create_webp_variant(self.image, max_width=1800, quality=82)
            medium = create_webp_variant(self.image, max_width=1200, quality=78)
            thumb = create_webp_variant(self.image, max_width=600, quality=75)

            self.image_large.save(
                build_variant_filename(self.image.name, "large"), large, save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"), medium, save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"), thumb, save=False
            )

            super().save(update_fields=["image_large", "image_medium", "image_thumb"])

        except Exception as e:
            print("ABOUTIMAGE VARIANT SKIPPED:", e)


class Gear(models.Model):
    GEAR_TYPES = [
        ("camera", "Camera"),
        ("lens", "Lens"),
        ("film", "Film"),
        ("accessory", "Accessory"),
    ]

    name = models.CharField(max_length=200)
    gear_type = models.CharField(max_length=50, choices=GEAR_TYPES, default="camera")
    description = models.TextField()
    image = models.ImageField(upload_to="gear/", blank=True, null=True)

    image_large = models.ImageField(upload_to="gear/large/", blank=True, null=True)
    image_medium = models.ImageField(upload_to="gear/medium/", blank=True, null=True)
    image_thumb = models.ImageField(upload_to="gear/thumb/", blank=True, null=True)

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = Gear.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except Gear.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_large
            or not self.image_medium
            or not self.image_thumb
        )

        if not should_generate:
            return

        try:
            large = create_webp_variant(self.image, max_width=1800, quality=82)
            medium = create_webp_variant(self.image, max_width=1200, quality=78)
            thumb = create_webp_variant(self.image, max_width=600, quality=75)

            self.image_large.save(
                build_variant_filename(self.image.name, "large"), large, save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"), medium, save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"), thumb, save=False
            )

            super().save(update_fields=["image_large", "image_medium", "image_thumb"])

        except Exception as e:
            print("GEAR VARIANT SKIPPED:", e)

    def __str__(self):
        return self.name

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    suggested_location = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.suggested_location or 'Message'}"
    
class Collaborator(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="collaborators/", blank=True, null=True)

    image_large = models.ImageField(upload_to="collaborators/large/", blank=True, null=True)
    image_medium = models.ImageField(upload_to="collaborators/medium/", blank=True, null=True)
    image_thumb = models.ImageField(upload_to="collaborators/thumb/", blank=True, null=True)

    website_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = Collaborator.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except Collaborator.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_large
            or not self.image_medium
            or not self.image_thumb
        )

        if not should_generate:
            return

        try:
            large = create_webp_variant(self.image, max_width=1800, quality=82)
            medium = create_webp_variant(self.image, max_width=1200, quality=78)
            thumb = create_webp_variant(self.image, max_width=600, quality=75)

            self.image_large.save(
                build_variant_filename(self.image.name, "large"), large, save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"), medium, save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"), thumb, save=False
            )

            super().save(update_fields=["image_large", "image_medium", "image_thumb"])

        except Exception as e:
            print("COLLABORATOR VARIANT SKIPPED:", e)

    def __str__(self):
        return self.name
    
class CarpNews(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    summary = models.TextField()

    body = models.TextField()


    image = models.ImageField(
        upload_to="carp/",
        blank=True,
        null=True,
    )


    image_webp = models.ImageField(
        upload_to="carp/webp/",
        blank=True,
        null=True,
    )


    published_at = models.DateTimeField(
        default=timezone.now
    )


    source_url = models.URLField(
        blank=True
    )


    is_published = models.BooleanField(
        default=True
    )


    class Meta:
        ordering = [
            "-published_at"
        ]


    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            old = CarpNews.objects.get(pk=self.pk)
            old_image_name = old.image.name


        super().save(*args, **kwargs)


        if not self.image:
            return


        image_changed = (
            old_image_name != self.image.name
        )


        if image_changed or not self.image_webp:

            try:

                webp = create_webp_variant(
                    self.image,
                    max_width=1600,
                    quality=82
                )


                self.image_webp.save(
                    build_variant_filename(
                        self.image.name,
                        "news"
                    ),
                    webp,
                    save=False
                )


                super().save(
                    update_fields=[
                        "image_webp"
                    ]
                )


            except Exception as e:

                print(
                    "CARP NEWS IMAGE SKIPPED:",
                    e
                )


    def __str__(self):
        return self.title
    
class CarpPageSettings(models.Model):

    hero_image = models.ImageField(
        upload_to="carp/header/",
        blank=True,
        null=True,
    )

    hero_image_webp = models.ImageField(
        upload_to="carp/header/webp/",
        blank=True,
        null=True,
    )

    title = models.CharField(
        max_length=100,
        default="Carp Today"
    )

    subtitle = models.TextField(
        default="Latest Hiroshima Carp news for visitors and baseball fans."
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            old = CarpPageSettings.objects.get(pk=self.pk)
            old_image_name = old.hero_image.name


        super().save(*args, **kwargs)


        if not self.hero_image:
            return


        image_changed = (
            old_image_name != self.hero_image.name
        )


        if image_changed or not self.hero_image_webp:

            try:

                webp = create_webp_variant(
                    self.hero_image,
                    max_width=1600,
                    quality=82
                )


                self.hero_image_webp.save(
                    build_variant_filename(
                        self.hero_image.name,
                        "hero"
                    ),
                    webp,
                    save=False
                )


                super().save(
                    update_fields=[
                        "hero_image_webp"
                    ]
                )


            except Exception as e:

                print(
                    "CARP HERO IMAGE SKIPPED:",
                    e
                )


    def __str__(self):
        return self.title