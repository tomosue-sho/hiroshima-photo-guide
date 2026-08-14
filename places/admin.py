from django.contrib import admin
from .models import Area, Location, Photo, Tag
from .models import About, AboutImage, Collaborator
from .models import Gear, Message
from .models import CarpNews, CarpPageSettings
from .image_utils import process_photo_image

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0

    def save_formset(self, request, form, formset, change):
        instances = formset.save()

        for instance in instances:
            if instance.image:
                instance.processing_status = "pending"
                instance.processing_error = None

                instance.save(
                    update_fields=[
                        "processing_status",
                        "processing_error",
                    ]
                )

                process_photo_image(instance)
                
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "area",
        "get_collection",
        "latitude",
        "longitude",
    )

    search_fields = (
        "name",
        "area__name",
    )

    list_filter = (
        "area__collection",
        "area",
        "tags",
    )

    filter_horizontal = (
        "tags",
    )

    inlines = [
        PhotoInline,
    ]

    @admin.display(
        description="Collection",
        ordering="area__collection",
    )
    def get_collection(self, obj):
        return obj.area.get_collection_display()
    
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "is_featured",
        "exhibition_order",
        "camera",
        "lens",
        "iso",
        "aperture",
        "processing_status",
    )

    list_filter = (
        "is_featured",
        "processing_status",
    )

    list_editable = (
        "is_featured",
        "exhibition_order",
    )

    search_fields = (
        "location__name",
        "camera",
        "lens",
    )

    def save_model(self, request, obj, form, change):
        """
        Photo保存後、Pendingなら自動的に画像処理を実行する。
        """

        if obj.image:
            obj.processing_status = "pending"
            obj.processing_error = None

        super().save_model(request, obj, form, change)

        if obj.image and obj.processing_status == "pending":
            process_photo_image(obj)

@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    list_display = ("name", "gear_type")
    list_filter = ("gear_type",)
    search_fields = ("name", "description")
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "suggested_location", "is_read", "created_at")
    list_filter = ("is_read", "country", "created_at")
    search_fields = ("name", "email", "country", "suggested_location", "message")
    readonly_fields = ("created_at",)
    
@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "is_visible", "created_at")
    list_filter = ("is_visible", "created_at")
    search_fields = ("name", "role", "description")
    
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ja", "slug")
    search_fields = ("name", "name_ja", "slug")
    prepopulated_fields = {"slug": ("name",)}
    
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "collection")
    list_filter = ("collection", "country")
    search_fields = ("name", "country")
    
@admin.register(CarpNews)
class CarpNewsAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "published_at",
        "is_published",
    )

    list_filter = (
        "is_published",
    )

    search_fields = (
        "title",
        "summary",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    ordering = (
        "-published_at",
    )
    
@admin.register(CarpPageSettings)
class CarpPageSettingsAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "updated_at",
    ]