from django.db import models
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
from fractions import Fraction

class Area(models.Model):
    name = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='areas/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


from django.db import models

class Location(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=300)

    image = models.ImageField(upload_to='locations/', blank=True, null=True)
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

    def __str__(self):
        return self.name

class Photo(models.Model):

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    image = models.ImageField(
        upload_to='locations/'
    )

    caption = models.CharField(
        max_length=200,
        blank=True
    )

    camera = models.CharField(
        max_length=100,
        blank=True
    )

    lens = models.CharField(
        max_length=100,
        blank=True
    )

    film = models.CharField(
        max_length=100,
        blank=True
    )

    iso = models.CharField(
        max_length=50,
        blank=True
    )

    aperture = models.CharField(
        max_length=50,
        blank=True
    )

    shutter_speed = models.CharField(
        max_length=50,
        blank=True
    )

    focal_length = models.CharField(
        max_length=50,
        blank=True
    )

    def formatted_aperture(self):

        try:
            return round(
                float(Fraction(self.aperture)),
                1
            )
        except:
            return self.aperture

    def __str__(self):
        return f"{self.location.name} Photo"

def save(self, *args, **kwargs):

    super().save(*args, **kwargs)

    try:
        with open(self.image.path, "rb") as f:
            tags = exifread.process_file(f)

        # EXIF優先だが、手入力を潰さない
        if not self.lens:
            lens = tags.get("EXIF LensModel")
            if lens:
                self.lens = str(lens)

        if not self.camera:
            camera = tags.get("Image Model")
            if camera:
                self.camera = str(camera)

        if not self.iso:
            iso = tags.get("EXIF ISOSpeedRatings")
            if iso:
                self.iso = str(iso)

        if not self.aperture:
            aperture = tags.get("EXIF FNumber")
            if aperture:
                self.aperture = str(aperture)

        if not self.shutter_speed:
            shutter = tags.get("EXIF ExposureTime")
            if shutter:
                self.shutter_speed = str(shutter)

        if not self.focal_length:
            focal = tags.get("EXIF FocalLength")
            if focal:
                self.focal_length = str(focal)

        super().save(update_fields=[
            "camera",
            "lens",
            "iso",
            "aperture",
            "shutter_speed",
            "focal_length"
        ])

    except Exception as e:
        print("EXIF ERROR:", e)
        
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
        "About",
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="about/")