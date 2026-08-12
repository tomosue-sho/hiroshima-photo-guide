from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def build_variant_filename(original_name: str, suffix: str) -> str:
    """
    元画像名から WebP 用のファイル名を作る。
    例: FP000909.JPG -> FP000909_medium.webp
    """
    stem = Path(original_name).stem
    safe_stem = "".join(
        c if c.isalnum() or c in ("-", "_") else "_"
        for c in stem
    )
    return f"{safe_stem}_{suffix}.webp"


def create_webp_variant(image_field, *, max_width: int, quality: int) -> ContentFile:
    """
    ImageField の画像から WebP 縮小版を作る。
    R2 / S3 ストレージ対応のため .path は使わない。
    """
    image_field.open("rb")

    try:
        img = Image.open(image_field)

        # iPhoneやカメラ画像のEXIF回転を反映
        img = ImageOps.exif_transpose(img)

        # MPOなど複数画像形式の場合、先頭フレームを使う
        try:
            img.seek(0)
        except Exception:
            pass

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        width, height = img.size

        if width > max_width:
            new_height = int(height * max_width / width)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        output = BytesIO()
        img.save(
            output,
            format="WEBP",
            quality=quality,
            method=4,
        )
        output.seek(0)

        return ContentFile(output.read())

    finally:
        image_field.close()
        
def create_webp_variants(image_field):
    """
    元画像を1回だけ読み込み、
    Large / Medium / Thumb のWebPをまとめて生成する。

    戻り値:
        {
            "large": ContentFile,
            "medium": ContentFile,
            "thumb": ContentFile,
        }
    """
    image_field.open("rb")

    try:
        img = Image.open(image_field)

        # EXIFによる画像回転を反映
        img = ImageOps.exif_transpose(img)

        # MPOなど複数画像形式の場合、先頭フレームを使用
        try:
            img.seek(0)
        except Exception:
            pass

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        original_width, original_height = img.size

        variants = {
            "large": (1800, 82),
            "medium": (1200, 78),
            "thumb": (600, 75),
        }

        results = {}

        for name, (max_width, quality) in variants.items():

            # 元画像を直接変更しない
            variant = img.copy()

            width, height = variant.size

            if width > max_width:
                new_height = int(height * max_width / width)

                variant = variant.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            output = BytesIO()

            variant.save(
                output,
                format="WEBP",
                quality=quality,
                method=4,
            )

            output.seek(0)

            results[name] = ContentFile(output.read())

            variant.close()

        return results

    finally:
        image_field.close()

def extract_exif_data(image_field):
    """
    ImageFieldの元画像からEXIF情報を取得する。
    R2 / S3ストレージ対応のため .path は使用しない。

    戻り値:
        {
            "lens": "...",
            "camera": "...",
            "iso": "...",
            "aperture": "...",
            "shutter_speed": "...",
            "focal_length": "...",
        }
    """
    import exifread

    image_field.open("rb")

    try:
        tags = exifread.process_file(
            image_field,
            details=False
        )

        data = {}

        lens = tags.get("EXIF LensModel")
        if lens:
            data["lens"] = str(lens)

        camera = tags.get("Image Model")
        if camera:
            data["camera"] = str(camera)

        iso = tags.get("EXIF ISOSpeedRatings")
        if iso:
            data["iso"] = str(iso)

        aperture = tags.get("EXIF FNumber")
        if aperture:
            data["aperture"] = str(aperture)

        shutter = tags.get("EXIF ExposureTime")
        if shutter:
            data["shutter_speed"] = str(shutter)

        focal = tags.get("EXIF FocalLength")
        if focal:
            data["focal_length"] = str(focal)

        return data

    finally:
        image_field.close()

def create_webp_variants_and_exif(image_field):
    """
    元画像をR2から1回だけ読み込み、
    Large / Medium / ThumbのWebPとEXIF情報をまとめて取得する。

    戻り値:
        {
            "variants": {
                "large": ContentFile,
                "medium": ContentFile,
                "thumb": ContentFile,
            },
            "exif": {
                "lens": "...",
                "camera": "...",
                "iso": "...",
                "aperture": "...",
                "shutter_speed": "...",
                "focal_length": "...",
            }
        }
    """
    import exifread

    image_field.open("rb")

    try:
        # R2から元画像を1回だけ読み込む
        image_data = image_field.read()

    finally:
        image_field.close()

    # ---------------------------------
    # EXIF
    # ---------------------------------

    exif_data = {}

    try:
        exif_tags = exifread.process_file(
            BytesIO(image_data),
            details=False
        )

        lens = exif_tags.get("EXIF LensModel")
        if lens:
            exif_data["lens"] = str(lens)

        camera = exif_tags.get("Image Model")
        if camera:
            exif_data["camera"] = str(camera)

        iso = exif_tags.get("EXIF ISOSpeedRatings")
        if iso:
            exif_data["iso"] = str(iso)

        aperture = exif_tags.get("EXIF FNumber")
        if aperture:
            exif_data["aperture"] = str(aperture)

        shutter = exif_tags.get("EXIF ExposureTime")
        if shutter:
            exif_data["shutter_speed"] = str(shutter)

        focal = exif_tags.get("EXIF FocalLength")
        if focal:
            exif_data["focal_length"] = str(focal)

    except Exception as e:
        print("EXIF SKIPPED:", e)

    # ---------------------------------
    # WebP
    # ---------------------------------

    variants = {}

    try:
        img = Image.open(BytesIO(image_data))

        # EXIFによる画像回転を反映
        img = ImageOps.exif_transpose(img)

        # MPOなど複数画像形式の場合、先頭フレームを使用
        try:
            img.seek(0)
        except Exception:
            pass

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        variant_settings = {
            "large": (1800, 82),
            "medium": (1200, 78),
            "thumb": (600, 75),
        }

        for name, (max_width, quality) in variant_settings.items():

            variant = img.copy()

            width, height = variant.size

            if width > max_width:
                new_height = int(height * max_width / width)

                variant = variant.resize(
                    (max_width, new_height),
                    Image.LANCZOS
                )

            output = BytesIO()

            variant.save(
                output,
                format="WEBP",
                quality=quality,
                method=4,
            )

            output.seek(0)

            variants[name] = ContentFile(
                output.read()
            )

            variant.close()

        img.close()

    except Exception as e:
        print("WEBP VARIANTS SKIPPED:", e)

    return {
        "variants": variants,
        "exif": exif_data,
    }

def process_photo_image(photo):
    """
    Photoの元画像からWebPとEXIFを生成する。

    processing_status:
        pending
        processing
        completed
        failed
    """

    if not photo.image:
        photo.processing_status = "failed"
        photo.processing_error = "Image file does not exist."
        photo.save(
            update_fields=[
                "processing_status",
                "processing_error",
            ]
        )
        return False

    try:
        # -----------------------------
        # 処理開始
        # -----------------------------

        photo.processing_status = "processing"
        photo.processing_error = None

        photo.save(
            update_fields=[
                "processing_status",
                "processing_error",
            ]
        )

        # -----------------------------
        # WebP + EXIF
        # -----------------------------

        result = create_webp_variants_and_exif(
            photo.image
        )

        variants = result["variants"]
        exif_data = result["exif"]

        update_fields = []

        # -----------------------------
        # WebP
        # -----------------------------

        if variants:
            photo.image_large.save(
                build_variant_filename(
                    photo.image.name,
                    "large"
                ),
                variants["large"],
                save=False
            )

            photo.image_medium.save(
                build_variant_filename(
                    photo.image.name,
                    "medium"
                ),
                variants["medium"],
                save=False
            )

            photo.image_thumb.save(
                build_variant_filename(
                    photo.image.name,
                    "thumb"
                ),
                variants["thumb"],
                save=False
            )

            update_fields.extend([
                "image_large",
                "image_medium",
                "image_thumb",
            ])

        # -----------------------------
        # EXIF
        # -----------------------------

        if not photo.lens and exif_data.get("lens"):
            photo.lens = exif_data["lens"]
            update_fields.append("lens")

        if not photo.camera and exif_data.get("camera"):
            photo.camera = exif_data["camera"]
            update_fields.append("camera")

        if not photo.iso and exif_data.get("iso"):
            photo.iso = exif_data["iso"]
            update_fields.append("iso")

        if not photo.aperture and exif_data.get("aperture"):
            photo.aperture = exif_data["aperture"]
            update_fields.append("aperture")

        if not photo.shutter_speed and exif_data.get("shutter_speed"):
            photo.shutter_speed = exif_data["shutter_speed"]
            update_fields.append("shutter_speed")

        if not photo.focal_length and exif_data.get("focal_length"):
            photo.focal_length = exif_data["focal_length"]
            update_fields.append("focal_length")

        # -----------------------------
        # 完了
        # -----------------------------

        photo.processing_status = "completed"
        photo.processing_error = None

        update_fields.extend([
            "processing_status",
            "processing_error",
        ])

        if update_fields:
            photo.save(
                update_fields=list(
                    dict.fromkeys(update_fields)
                )
            )

        return True

    except Exception as e:

        # -----------------------------
        # 失敗
        # -----------------------------

        photo.processing_status = "failed"
        photo.processing_error = str(e)

        photo.save(
            update_fields=[
                "processing_status",
                "processing_error",
            ]
        )

        print(
            "PHOTO IMAGE PROCESSING FAILED:",
            e
        )

        return False