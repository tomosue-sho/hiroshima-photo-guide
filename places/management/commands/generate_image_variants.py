from django.core.management.base import BaseCommand

from places.models import Area, Location
from places.image_utils import (
    create_webp_variants,
    build_variant_filename,
)


class Command(BaseCommand):
    help = "既存のArea/Location画像からWebP縮小版を生成します"

    def handle(self, *args, **options):
        self.generate_for_areas()
        self.generate_for_locations()

    def generate_for_areas(self):
        self.stdout.write("Area画像の変換を開始します")

        areas = Area.objects.exclude(image="")

        for area in areas:

            if not area.image:
                continue

            if (
                area.image_large
                and area.image_medium
                and area.image_thumb
            ):
                self.stdout.write(
                    f"Area skip: {area.id} {area.name}"
                )
                continue

            try:
                variants = create_webp_variants(
                    area.image
                )

                area.image_large.save(
                    build_variant_filename(
                        area.image.name,
                        "large",
                    ),
                    variants["large"],
                    save=False,
                )

                area.image_medium.save(
                    build_variant_filename(
                        area.image.name,
                        "medium",
                    ),
                    variants["medium"],
                    save=False,
                )

                area.image_thumb.save(
                    build_variant_filename(
                        area.image.name,
                        "thumb",
                    ),
                    variants["thumb"],
                    save=False,
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
                        f"Area failed: "
                        f"{area.id} {area.name} / {e}"
                    )
                )

    def generate_for_locations(self):
        self.stdout.write("Location画像の変換を開始します")

        locations = Location.objects.exclude(image="")

        for location in locations:

            if not location.image:
                continue

            if (
                location.image_large
                and location.image_medium
                and location.image_thumb
            ):
                self.stdout.write(
                    f"Location skip: "
                    f"{location.id} {location.name}"
                )
                continue

            try:
                variants = create_webp_variants(
                    location.image
                )

                location.image_large.save(
                    build_variant_filename(
                        location.image.name,
                        "large",
                    ),
                    variants["large"],
                    save=False,
                )

                location.image_medium.save(
                    build_variant_filename(
                        location.image.name,
                        "medium",
                    ),
                    variants["medium"],
                    save=False,
                )

                location.image_thumb.save(
                    build_variant_filename(
                        location.image.name,
                        "thumb",
                    ),
                    variants["thumb"],
                    save=False,
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
                        f"Location done: "
                        f"{location.id} {location.name}"
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Location failed: "
                        f"{location.id} {location.name} / {e}"
                    )
                )