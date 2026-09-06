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

class JournalArticle(models.Model):
    dam_lake = models.ForeignKey( 
        "DamLake",
        on_delete=models.SET_NULL,
        blank=True, null=True, 
        related_name="journal_articles", 
        verbose_name="ダム湖百選", 
        )
    
    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    date = models.DateField(
        default=timezone.now
    )

    body = models.TextField()

    image = models.ImageField(
        upload_to="journal/",
        blank=True,
        null=True,
    )

    image_large = models.ImageField(
        upload_to="journal/large/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="journal/medium/",
        blank=True,
        null=True,
    )

    image_thumb = models.ImageField(
        upload_to="journal/thumb/",
        blank=True,
        null=True,
    )

    is_published = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-date",
            "-id",
        ]

    def __str__(self):
        return self.title


class JournalImage(models.Model):
    article = models.ForeignKey(
        JournalArticle,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="journal/",
    )

    image_large = models.ImageField(
        upload_to="journal/large/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="journal/medium/",
        blank=True,
        null=True,
    )

    image_thumb = models.ImageField(
        upload_to="journal/thumb/",
        blank=True,
        null=True,
    )

    caption = models.CharField(
        max_length=200,
        blank=True,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "order",
            "id",
        ]

    def __str__(self):
        return f"{self.article.title} - Image {self.id}"

class DiaryPost(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    excerpt = models.TextField(
        blank=True
    )

    body = models.TextField()

    image = models.ImageField(
        upload_to="diary/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="diary/medium/",
        blank=True,
        null=True,
    )

    published_at = models.DateTimeField(
        default=timezone.now
    )

    is_published = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-published_at"]

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = DiaryPost.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except DiaryPost.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "DIARY IMAGE VARIANT SKIPPED:",
                e
            )

    def __str__(self):
        return self.title
    
class DiaryPhoto(models.Model):

    post = models.ForeignKey(
        DiaryPost,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to="diary/photos/",
    )

    image_medium = models.ImageField(
        upload_to="diary/photos/medium/",
        blank=True,
        null=True,
    )

    caption = models.TextField(
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = DiaryPhoto.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except DiaryPhoto.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "DIARY PHOTO IMAGE VARIANT SKIPPED:",
                e,
            )

    def __str__(self):
        return f"{self.post.title} - Photo {self.order}"
    
class DamLake(models.Model):
    """
    Dam Lake 100 Selection
    全国の「ダム湖百選」65湖を管理するモデル
    """

    name = models.CharField(
        max_length=200,
        verbose_name="ダム湖名",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
    )

    dam_name = models.CharField(
        max_length=200,
        verbose_name="ダム名",
    )

    prefecture = models.CharField(
        max_length=100,
        verbose_name="都道府県",
    )

    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="緯度",
    )

    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name="経度",
    )

    # ---------------------------------
    # Visit / Photography status
    # ---------------------------------

    visited = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="訪問済み",
    )

    photographed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="撮影済み",
    )

    visit_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="訪問日",
    )

    # ---------------------------------
    # Content
    # ---------------------------------

    excerpt = models.TextField(
        blank=True,
        verbose_name="概要",
    )

    description = models.TextField(
        blank=True,
        verbose_name="紹介文",
    )

    # ---------------------------------
    # Main image
    # ---------------------------------

    image = models.ImageField(
        upload_to="dam_lakes/",
        blank=True,
        null=True,
        verbose_name="メイン画像",
    )

    image_large = models.ImageField(
        upload_to="dam_lakes/large/",
        blank=True,
        null=True,
    )

    image_medium = models.ImageField(
        upload_to="dam_lakes/medium/",
        blank=True,
        null=True,
    )

    image_thumb = models.ImageField(
        upload_to="dam_lakes/thumb/",
        blank=True,
        null=True,
    )

    # ---------------------------------
    # Display
    # ---------------------------------

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="表示順",
    )

    is_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="公開",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "ダム湖百選"
        verbose_name_plural = "ダム湖百選"

    def __str__(self):
        return f"{self.name} / {self.dam_name}"

    @property
    def has_location(self):
        """
        日本地図に表示できる座標が登録されているか
        """
        return (
            self.latitude is not None
            and self.longitude is not None
        )

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = DamLake.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except DamLake.DoesNotExist:
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

            large = create_webp_variant(
                self.image,
                max_width=1800,
                quality=82,
            )

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            thumb = create_webp_variant(
                self.image,
                max_width=600,
                quality=75,
            )

            self.image_large.save(
                build_variant_filename(
                    self.image.name,
                    "large",
                ),
                large,
                save=False,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            self.image_thumb.save(
                build_variant_filename(
                    self.image.name,
                    "thumb",
                ),
                thumb,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_large",
                    "image_medium",
                    "image_thumb",
                ]
            )

        except Exception as e:

            print(
                "DAM LAKE IMAGE VARIANT SKIPPED:",
                e,
            )
            
            
class DamLakePhoto(models.Model):
    lake = models.ForeignKey(
        DamLake,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="ダム湖",
    )

    # ---------------------------------
    # Original image
    # ---------------------------------

    image = models.ImageField(
        upload_to="dam_lakes/photos/",
        verbose_name="写真",
    )

    # ---------------------------------
    # WebP variants
    # ---------------------------------

    # 既存データとの互換性のため、フィールド自体は残す
    image_large = models.ImageField(
        upload_to="dam_lakes/photos/large/",
        blank=True,
        null=True,
        verbose_name="Large",
    )

    image_medium = models.ImageField(
        upload_to="dam_lakes/photos/medium/",
        blank=True,
        null=True,
        verbose_name="Medium",
    )

    # 既存データとの互換性のため、フィールド自体は残す
    image_thumb = models.ImageField(
        upload_to="dam_lakes/photos/thumb/",
        blank=True,
        null=True,
        verbose_name="Thumb",
    )

    # ---------------------------------
    # Content
    # ---------------------------------

    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="キャプション",
    )

    # ---------------------------------
    # Display
    # ---------------------------------

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="表示順",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "ダム湖写真"
        verbose_name_plural = "ダム湖写真"

    def __str__(self):
        return f"{self.lake.name} - {self.order}"

    # ---------------------------------
    # Save
    # ---------------------------------

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = DamLakePhoto.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except DamLakePhoto.DoesNotExist:
                pass

        # まず元画像を保存
        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        # Mediumだけを生成する
        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            # ---------------------------------
            # Medium
            # ---------------------------------

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            # ---------------------------------
            # Save Medium variant
            # ---------------------------------

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            # MediumだけDBに保存
            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "DAM LAKE PHOTO IMAGE VARIANT SKIPPED:",
                e,
            )

# =========================================
# Hiroshima Kagura
# =========================================

class KaguraPerformance(models.Model):
    """
    Hiroshima Kagura performance / story.

    This represents the story itself, not a specific live performance.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="演目名",
    )

    name_en = models.CharField(
        max_length=150,
        verbose_name="英語名",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
    )

    short_description = models.TextField(
        blank=True,
        verbose_name="簡単な説明",
    )

    story = models.TextField(
        blank=True,
        verbose_name="ストーリー",
    )

    characters = models.TextField(
        blank=True,
        verbose_name="登場人物",
    )

    highlights = models.TextField(
        blank=True,
        verbose_name="見どころ",
    )

    costume_description = models.TextField(
        blank=True,
        verbose_name="衣装・仮面",
    )

    image = models.ImageField(
        upload_to="kagura/",
        blank=True,
        null=True,
        verbose_name="メイン画像",
    )

    image_medium = models.ImageField(
        upload_to="kagura/medium/",
        blank=True,
        null=True,
        verbose_name="Medium",
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="表示順",
    )

    is_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="公開",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "神楽演目"
        verbose_name_plural = "神楽演目"

    def __str__(self):
        return f"{self.name} / {self.name_en}"

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = KaguraPerformance.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except KaguraPerformance.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "KAGURA PERFORMANCE IMAGE SKIPPED:",
                e,
            )


class KaguraPerformancePhoto(models.Model):
    """
    Additional photographs for a Kagura performance.
    Medium image only.
    """

    performance = models.ForeignKey(
        KaguraPerformance,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="演目",
    )

    image = models.ImageField(
        upload_to="kagura/photos/",
        verbose_name="写真",
    )

    image_medium = models.ImageField(
        upload_to="kagura/photos/medium/",
        blank=True,
        null=True,
        verbose_name="Medium",
    )

    caption = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="キャプション",
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="表示順",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "神楽演目写真"
        verbose_name_plural = "神楽演目写真"

    def __str__(self):
        return f"{self.performance.name} - Photo {self.order}"

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = KaguraPerformancePhoto.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except KaguraPerformancePhoto.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "KAGURA PERFORMANCE PHOTO SKIPPED:",
                e,
            )


class KaguraTroupe(models.Model):
    """
    Kagura troupe.
    Initially this can contain only a few troupes.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="神楽団名",
    )

    name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="英語名",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
    )

    description = models.TextField(
        blank=True,
        verbose_name="紹介",
    )

    style = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="スタイル",
    )

    website_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Webサイト",
    )

    is_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="公開",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "神楽団"
        verbose_name_plural = "神楽団"

    def __str__(self):
        return self.name


class KaguraEvent(models.Model):
    """
    A specific Kagura performance at a specific place and date.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="公演名",
    )

    date = models.DateField(
        verbose_name="公演日",
    )

    venue = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="会場",
    )

    venue_address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="会場住所",
    )

    troupe = models.ForeignKey(
        KaguraTroupe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="events",
        verbose_name="神楽団",
    )

    performances = models.ManyToManyField(
        KaguraPerformance,
        blank=True,
        related_name="events",
        verbose_name="演目",
    )

    description = models.TextField(
        blank=True,
        verbose_name="公演について",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "神楽公演"
        verbose_name_plural = "神楽公演"

    def __str__(self):
        return f"{self.title} - {self.date}"


class KaguraJournal(models.Model):
    """
    Personal journal entry about attending a Kagura performance.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="タイトル",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
    )

    event = models.ForeignKey(
        KaguraEvent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="journal_entries",
        verbose_name="神楽公演",
    )

    date = models.DateField(
        default=timezone.now,
        verbose_name="投稿日",
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name="概要",
    )

    body = models.TextField(
        blank=True,
        verbose_name="本文",
    )

    image = models.ImageField(
        upload_to="kagura/journal/",
        blank=True,
        null=True,
        verbose_name="メイン画像",
    )

    image_medium = models.ImageField(
        upload_to="kagura/journal/medium/",
        blank=True,
        null=True,
        verbose_name="Medium",
    )

    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="公開",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "神楽Journal"
        verbose_name_plural = "神楽Journal"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = KaguraJournal.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except KaguraJournal.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "KAGURA JOURNAL IMAGE SKIPPED:",
                e,
            )


class KaguraJournalPhoto(models.Model):

    journal = models.ForeignKey(
        KaguraJournal,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Journal",
    )

    image = models.ImageField(
        upload_to="kagura/journal/photos/",
        verbose_name="写真",
    )

    image_medium = models.ImageField(
        upload_to="kagura/journal/photos/medium/",
        blank=True,
        null=True,
        verbose_name="Medium",
    )

    caption = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="キャプション",
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="表示順",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "神楽Journal写真"
        verbose_name_plural = "神楽Journal写真"

    def __str__(self):
        return f"{self.journal.title} - Photo {self.order}"

    def save(self, *args, **kwargs):

        old_image_name = None

        if self.pk:
            try:
                old = KaguraJournalPhoto.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except KaguraJournalPhoto.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        should_generate = (
            image_changed
            or not self.image_medium
        )

        if not should_generate:
            return

        try:

            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78,
            )

            self.image_medium.save(
                build_variant_filename(
                    self.image.name,
                    "medium",
                ),
                medium,
                save=False,
            )

            super().save(
                update_fields=[
                    "image_medium",
                ]
            )

        except Exception as e:

            print(
                "KAGURA JOURNAL PHOTO IMAGE SKIPPED:",
                e,
            )