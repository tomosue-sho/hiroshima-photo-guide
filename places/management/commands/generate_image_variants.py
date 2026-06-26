from django.core.management.base import BaseCommand

from places.models import Area, Location, Photo
from places.image_utils import create_webp_variant, build_variant_filename


class Command(BaseCommand):
    help = "既存のArea/Location/Photo画像からWebP縮小版を生成します"

    def handle(self, *args, **options):
        self.generate_for_areas()
        self.generate_for_locations()
        self.generate_for_photos()

    def generate_for_areas(self):
        self.stdout.write("Area画像の変換を開始します")

        for area in Area.objects.exclude(image=""):
            if not area.image:
                continue

            if area.image_large and area.image_medium and area.image_thumb:
                self.stdout.write(f"Area skip: {area.id} {area.name}")
                continue

            try:
                large = create_webp_variant(
                    area.image,
                    max_width=1800,
                    quality=82
                )
                medium = create_webp_variant(
                    area.image,
                    max_width=1200,
                    quality=78
                )
                thumb = create_webp_variant(
                    area.image,
                    max_width=600,
                    quality=75
                )

                area.image_large.save(
                    build_variant_filename(area.image.name, "large"),
                    large,
                    save=False
                )
                area.image_medium.save(
                    build_variant_filename(area.image.name, "medium"),
                    medium,
                    save=False
                )
                area.image_thumb.save(
                    build_variant_filename(area.image.name, "thumb"),
                    thumb,
                    save=False
                )

                area.save(
                    update_fields=[
                        "image_large",
                        "image_medium",
                        "image_thumb",
                    ]
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Area done: {area.id} {area.name}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Area failed: {area.id} {area.name} / {e}"
                    )
                )

    def generate_for_locations(self):
        self.stdout.write("Location画像の変換を開始します")

        for location in Location.objects.exclude(image=""):
            if not location.image:
                continue

            if location.image_large and location.image_medium and location.image_thumb:
                self.stdout.write(f"Location skip: {location.id} {location.name}")
                continue

            try:
                large = create_webp_variant(
                    location.image,
                    max_width=1800,
                    quality=82
                )
                medium = create_webp_variant(
                    location.image,
                    max_width=1200,
                    quality=78
                )
                thumb = create_webp_variant(
                    location.image,
                    max_width=600,
                    quality=75
                )

                location.image_large.save(
                    build_variant_filename(location.image.name, "large"),
                    large,
                    save=False
                )
                location.image_medium.save(
                    build_variant_filename(location.image.name, "medium"),
                    medium,
                    save=False
                )
                location.image_thumb.save(
                    build_variant_filename(location.image.name, "thumb"),
                    thumb,
                    save=False
                )

                location.save(
                    update_fields=[
                        "image_large",
                        "image_medium",
                        "image_thumb",
                    ]
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Location done: {location.id} {location.name}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Location failed: {location.id} {location.name} / {e}"
                    )
                )

    def generate_for_photos(self):
        self.stdout.write("Photo画像の変換を開始します")

        for photo in Photo.objects.exclude(image=""):
            if not photo.image:
                continue

            if photo.image_large and photo.image_medium and photo.image_thumb:
                self.stdout.write(f"Photo skip: {photo.id}")
                continue

            try:
                large = create_webp_variant(
                    photo.image,
                    max_width=1800,
                    quality=82
                )
                medium = create_webp_variant(
                    photo.image,
                    max_width=1200,
                    quality=78
                )
                thumb = create_webp_variant(
                    photo.image,
                    max_width=600,
                    quality=75
                )

                photo.image_large.save(
                    build_variant_filename(photo.image.name, "large"),
                    large,
                    save=False
                )
                photo.image_medium.save(
                    build_variant_filename(photo.image.name, "medium"),
                    medium,
                    save=False
                )
                photo.image_thumb.save(
                    build_variant_filename(photo.image.name, "thumb"),
                    thumb,
                    save=False
                )

                photo.save(
                    update_fields=[
                        "image_large",
                        "image_medium",
                        "image_thumb",
                    ]
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Photo done: {photo.id}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Photo failed: {photo.id} / {e}"
                    )
                )