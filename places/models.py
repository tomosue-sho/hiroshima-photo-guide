from django.db import models
from fractions import Fraction
from .image_utils import create_webp_variant, build_variant_filename


class Area(models.Model):
    name = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='areas/',
        blank=True,
        null=True
    )

    image_large = models.ImageField(
        upload_to="areas/large/",
        blank=True,
        null=True
    )
    image_medium = models.ImageField(
        upload_to="areas/medium/",
        blank=True,
        null=True
    )
    image_thumb = models.ImageField(
        upload_to="areas/thumb/",
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = Area.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except Area.DoesNotExist:
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
                quality=82
            )
            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78
            )
            thumb = create_webp_variant(
                self.image,
                max_width=600,
                quality=75
            )

            self.image_large.save(
                build_variant_filename(self.image.name, "large"),
                large,
                save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"),
                medium,
                save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"),
                thumb,
                save=False
            )

            super().save(
                update_fields=[
                    "image_large",
                    "image_medium",
                    "image_thumb",
                ]
            )

        except Exception as e:
            print("AREA IMAGE VARIANT SKIPPED:", e)

    def __str__(self):
        return self.name

class Location(models.Model):
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="locations"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=300)
    
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    image = models.ImageField(upload_to='locations/', blank=True, null=True)

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

    youtube_url = models.URLField(blank=True, null=True)

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
        old_image_name = None

        if self.pk:
            try:
                old = Location.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except Location.DoesNotExist:
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
                quality=82
            )
            medium = create_webp_variant(
                self.image,
                max_width=1200,
                quality=78
            )
            thumb = create_webp_variant(
                self.image,
                max_width=600,
                quality=75
            )

            self.image_large.save(
                build_variant_filename(self.image.name, "large"),
                large,
                save=False
            )
            self.image_medium.save(
                build_variant_filename(self.image.name, "medium"),
                medium,
                save=False
            )
            self.image_thumb.save(
                build_variant_filename(self.image.name, "thumb"),
                thumb,
                save=False
            )

            super().save(
                update_fields=[
                    "image_large",
                    "image_medium",
                    "image_thumb",
                ]
            )

        except Exception as e:
            print("LOCATION IMAGE VARIANT SKIPPED:", e)

    def __str__(self):
        return self.name


class Photo(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='photos'
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

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old = Photo.objects.get(pk=self.pk)
                old_image_name = old.image.name
            except Photo.DoesNotExist:
                pass

        # まず元画像をR2へ保存
        super().save(*args, **kwargs)

        if not self.image:
            return

        image_changed = old_image_name != self.image.name

        update_fields = []

        # 縮小版WebPを生成
        should_generate_variants = (
            image_changed
            or not self.image_large
            or not self.image_medium
            or not self.image_thumb
        )

        if should_generate_variants:
            try:
                large = create_webp_variant(
                    self.image,
                    max_width=1800,
                    quality=82
                )
                medium = create_webp_variant(
                    self.image,
                    max_width=1200,
                    quality=78
                )
                thumb = create_webp_variant(
                    self.image,
                    max_width=600,
                    quality=75
                )

                self.image_large.save(
                    build_variant_filename(self.image.name, "large"),
                    large,
                    save=False
                )
                self.image_medium.save(
                    build_variant_filename(self.image.name, "medium"),
                    medium,
                    save=False
                )
                self.image_thumb.save(
                    build_variant_filename(self.image.name, "thumb"),
                    thumb,
                    save=False
                )

                update_fields.extend([
                    "image_large",
                    "image_medium",
                    "image_thumb",
                ])

            except Exception as e:
                print("PHOTO IMAGE VARIANT SKIPPED:", e)

        # EXIF読み取り
        try:
            import exifread

            self.image.open("rb")
            tags = exifread.process_file(self.image, details=False)
            self.image.close()

            if not self.lens:
                lens = tags.get("EXIF LensModel")
                if lens:
                    self.lens = str(lens)
                    update_fields.append("lens")

            if not self.camera:
                camera = tags.get("Image Model")
                if camera:
                    self.camera = str(camera)
                    update_fields.append("camera")

            if not self.iso:
                iso = tags.get("EXIF ISOSpeedRatings")
                if iso:
                    self.iso = str(iso)
                    update_fields.append("iso")

            if not self.aperture:
                aperture = tags.get("EXIF FNumber")
                if aperture:
                    self.aperture = str(aperture)
                    update_fields.append("aperture")

            if not self.shutter_speed:
                shutter = tags.get("EXIF ExposureTime")
                if shutter:
                    self.shutter_speed = str(shutter)
                    update_fields.append("shutter_speed")

            if not self.focal_length:
                focal = tags.get("EXIF FocalLength")
                if focal:
                    self.focal_length = str(focal)
                    update_fields.append("focal_length")

        except Exception as e:
            print("EXIF SKIPPED:", e)

        if update_fields:
            update_fields = list(dict.fromkeys(update_fields))
            super().save(update_fields=update_fields)


class About(models.Model):
    title = models.CharField(max_length=200, default="About")
    description = models.TextField()

    image = models.ImageField(
        upload_to="about/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class AboutImage(models.Model):
    about = models.ForeignKey(
        About,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="about/")
    

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
    website_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name