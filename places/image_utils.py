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
            method=6,
        )
        output.seek(0)

        return ContentFile(output.read())

    finally:
        image_field.close()