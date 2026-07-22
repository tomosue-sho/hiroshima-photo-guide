from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .forms import MessageForm
from .models import (
    About,
    Area,
    Collaborator,
    Gear,
    Location,
    Tag,
)


def home(request):
    locations = (
        Location.objects
        .filter(area__collection="hiroshima")
        .select_related("area")
    )

    areas = (
        Area.objects
        .filter(collection="hiroshima")
        .order_by("name")
    )

    latest_locations = (
        Location.objects
        .filter(
            area__collection="hiroshima",
            added_at__isnull=False,
        )
        .select_related("area")
        .order_by("-added_at", "-id")[:3]
    )

    return render(
        request,
        "places/home.html",
        {
            "locations": locations,
            "areas": areas,
            "latest_locations": latest_locations,
        }
    )


def location_detail(request, location_id):
    location = get_object_or_404(
        Location.objects.select_related("area"),
        id=location_id,
    )

    return render(
        request,
        "places/detail.html",
        {
            "location": location,
        }
    )


def area_detail(request, area_id):
    # 広島版のArea詳細ページなので、
    # JapanのAreaはここでは取得させない
    area = get_object_or_404(
        Area,
        id=area_id,
        collection="hiroshima",
    )

    locations = (
        Location.objects
        .filter(
            area=area,
            area__collection="hiroshima",
        )
        .select_related("area")
        .order_by("name")
    )

    return render(
        request,
        "places/area.html",
        {
            "area": area,
            "locations": locations,
        }
    )


def about(request):
    about = About.objects.first()

    collaborators = Collaborator.objects.filter(
        is_visible=True
    )

    return render(
        request,
        "places/about.html",
        {
            "about": about,
            "collaborators": collaborators,
        }
    )


def location_map(request):
    locations = (
        Location.objects
        .filter(
            area__collection="hiroshima",
            latitude__isnull=False,
            longitude__isnull=False,
        )
        .select_related("area")
    )

    return render(
        request,
        "places/map.html",
        {
            "locations": locations,
        }
    )


def location_photos(request, location_id):
    location = get_object_or_404(
        Location.objects.select_related("area"),
        id=location_id,
    )

    photos = location.photos.all().order_by("id")

    return render(
        request,
        "places/location_photos.html",
        {
            "location": location,
            "photos": photos,
        }
    )


def gear_list(request):
    gears = Gear.objects.all()

    return render(
        request,
        "places/gear.html",
        {
            "gears": gears,
        }
    )


def contact(request):
    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            form.save()
            return render(
                request,
                "places/contact_success.html",
            )
    else:
        form = MessageForm()

    return render(
        request,
        "places/contact.html",
        {
            "form": form,
        }
    )


def tag_list(request):
    tags = Tag.objects.all()

    return render(
        request,
        "places/tag_list.html",
        {
            "tags": tags,
        }
    )


def tag_detail(request, slug):
    tag = get_object_or_404(
        Tag,
        slug=slug,
    )

    # 現在のタグページは広島版として扱う
    locations = (
        tag.locations
        .filter(area__collection="hiroshima")
        .select_related("area")
    )

    map_locations = locations.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    )

    return render(
        request,
        "places/tag_detail.html",
        {
            "tag": tag,
            "locations": locations,
            "map_locations": map_locations,
        }
    )


def update_list(request):
    new_locations = (
        Location.objects
        .filter(
            area__collection="hiroshima",
            added_at__isnull=False,
        )
        .select_related("area")
        .order_by("-added_at", "-id")
    )

    return render(
        request,
        "places/update_list.html",
        {
            "new_locations": new_locations,
        }
    )


def japan(request):
    # 全国版の一覧に表示するLocation
    # 緯度・経度が未入力でも一覧には表示する
    japan_locations = (
        Location.objects
        .filter(area__collection="japan")
        .select_related("area")
        .order_by("area__name", "name")
    )

    # 地図には緯度・経度のあるLocationだけを使用
    japan_map_locations = japan_locations.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    )

    japan_markers = []

    for location in japan_map_locations:
        japan_markers.append({
            "name": location.name,
            "area": location.area.name,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "url": reverse(
                "location_detail",
                args=[location.id],
            ),
        })

    japan_areas = (
        Area.objects
        .filter(collection="japan")
        .order_by("country", "name")
    )

    return render(
        request,
        "places/japan.html",
        {
            "japan_locations": japan_locations,
            "japan_markers": japan_markers,
            "japan_areas": japan_areas,
        }
    )