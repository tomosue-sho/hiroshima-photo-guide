from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('area/<int:area_id>/', views.area_detail, name='area_detail'),
    path("about/", views.about, name="about"),
    path("map/", views.location_map, name="location_map"),
    path('location/<int:location_id>/photos/', views.location_photos, name='location_photos'),
    path("gear/", views.gear_list, name="gear_list"),
    path("contact/", views.contact, name="contact"),
    path("tags/", views.tag_list, name="tag_list"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag_detail"),
    path("updates/", views.update_list, name="update_list"),
    path("japan/", views.japan, name="japan"),
    path("travel-area/<int:area_id>/", views.travel_area_detail, name="travel_area_detail"),
    path("carp/", views.carp_today, name="carp_today"),
    path("carp/news/<slug:slug>/", views.carp_news_detail, name="carp_news_detail"),
    path("photo-exhibition/", views.photo_exhibition, name="photo_exhibition"),
    path("diary/", views.diary_list, name="diary_list"),
    path("diary/<slug:slug>/", views.diary_detail, name="diary_detail"),
    path("dam-lakes/", views.dam_lake_list, name="dam_lake_list"),
    path("dam-lakes/<slug:slug>/",views.dam_lake_detail,name="dam_lake_detail",),
    path("kagura/", views.kagura_home, name="kagura_home"),
    path( "kagura/performances/<slug:slug>/",views.kagura_performance_detail,name="kagura_performance_detail",),
    path("kagura/journal/",views.kagura_journal_list,name="kagura_journal_list",),
    path("kagura/journal/<slug:slug>/",views.kagura_journal_detail,name="kagura_journal_detail",),
]