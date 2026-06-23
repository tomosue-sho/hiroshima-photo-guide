from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Location


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "about",
            "gear_list",
            "location_map",
        ]

    def location(self, item):
        return reverse(item)


class LocationSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return Location.objects.all()

    def location(self, obj):
        return reverse(
            "location_detail",
            args=[obj.id]
        )