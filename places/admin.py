from django.contrib import admin
from .models import Area, Location, Photo
from .models import About, AboutImage


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