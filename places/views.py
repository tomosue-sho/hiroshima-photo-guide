from django.shortcuts import render, get_object_or_404
from .models import Location, Area
from django.shortcuts import get_object_or_404

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