from django.shortcuts import render, get_object_or_404
from .models import Location, Area, Location
from django.shortcuts import get_object_or_404
from .models import About
from .models import Gear, Collaborator
from .forms import MessageForm

def about(request):
    return render(request, "places/about.html")

def home(request):

    locations = Location.objects.all()
    areas = Area.objects.all()

    return render(
        request,
        'places/home.html',
        {
            'locations': locations,
            'areas': areas,
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
    photos = location.photos.all()

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