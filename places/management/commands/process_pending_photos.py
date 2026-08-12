from django.core.management.base import BaseCommand

from places.models import Photo
from places.image_utils import process_photo_image


class Command(BaseCommand):
    help = "Process pending Photo image files."

    def handle(self, *args, **options):

        photos = Photo.objects.filter(
            processing_status="pending"
        ).order_by("id")

        count = photos.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {count} pending photo(s)."
            )
        )

        if count == 0:
            return

        success_count = 0
        failed_count = 0

        for photo in photos:

            self.stdout.write(
                f"Processing Photo ID {photo.id}: "
                f"{photo.image.name}"
            )

            result = process_photo_image(photo)

            if result:
                success_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Photo ID {photo.id} completed."
                    )
                )

            else:
                failed_count += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"Photo ID {photo.id} failed."
                    )
                )

                if photo.processing_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  Error: {photo.processing_error}"
                        )
                    )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. "
                f"Success: {success_count}, "
                f"Failed: {failed_count}"
            )
        )