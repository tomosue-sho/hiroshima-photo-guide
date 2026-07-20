from django.shortcuts import render
from .models import Location, Area
from django.shortcuts import get_object_or_404
from .models import About
from .models import Gear, Collaborator, Tag
from .forms import MessageForm

def home(request):
    locations = Location.objects.all()
    areas = Area.objects.all()

    latest_locations = (
        Location.objects
        .filter(added_at__isnull=False)
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
        Location,
        id=location_id
    )

    return render(
        request,
        'places/detail.html',
        {
            'location': location
        }
    )
    
def area_detail(request, area_id):

    area = get_object_or_404(
        Area,
        id=area_id
    )

    locations = Location.objects.filter(
        area=area
    )

    return render(
        request,
        'places/area.html',
        {
            'area': area,
            'locations': locations
        }
    )

def about(request):
    about = About.objects.first()
    collaborators = Collaborator.objects.filter(is_visible=True)

    return render(
        request,
        "places/about.html",
        {
            "about": about,
            "collaborators": collaborators,
        }
    )
    
def location_map(request):
    locations = Location.objects.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    )

    return render(request, 'places/map.html', {
        'locations': locations
    })

def location_photos(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    photos = location.photos.all().order_by("id")

    return render(request, 'places/location_photos.html', {
        'location': location,
        'photos': photos
    })
    
def gear_list(request):
    gears = Gear.objects.all()
    return render(request, "places/gear.html", {
        "gears": gears
    })
    
def contact(request):
    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            form.save()
            return render(request, "places/contact_success.html")

    else:
        form = MessageForm()

    return render(request, "places/contact.html", {"form": form})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, "places/tag_list.html", {"tags": tags})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    locations = tag.locations.all()
    map_locations = locations.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

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
        .filter(added_at__isnull=False)
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