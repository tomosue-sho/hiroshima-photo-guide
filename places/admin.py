from django.contrib import admin
from .models import Area, Location, Photo
from .models import About, AboutImage, Collaborator
from .models import Gear, Message

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'latitude', 'longitude')
    search_fields = ('name',)
    list_filter = ('area',)
    inlines = [PhotoInline]

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "location",
        "camera",
        "lens",
        "iso",
        "aperture"
    )

    search_fields = (
        'location__name',
        'camera',
        'lens'
    )

admin.site.register(About)
admin.site.register(AboutImage)

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