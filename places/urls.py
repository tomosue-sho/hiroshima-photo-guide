from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('location/<int:location_id>/',views.location_detail,name='location_detail'),
    path('area/<int:area_id>/',views.area_detail,name='area_detail'),
    path("about/", views.about, name="about"),
    path("map/", views.location_map, name="location_map"),
    path('location/<int:location_id>/photos/',views.location_photos,name='location_photos'),
    path("gear/", views.gear_list, name="gear_list"),
    path("contact/", views.contact, name="contact"),
]