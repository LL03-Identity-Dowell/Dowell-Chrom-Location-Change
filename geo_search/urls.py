from django.urls import path
from . import views

urlpatterns = [
    path('geo_location', views.Chromeview.as_view(), name='geolocation'),
    path('get-countries',views.GetCountries.as_view()),
    path('download-results', views.DownloadCSV.as_view(),name="download"),
    path('get-locations',views.GetLocations.as_view()),
    path("launch-browser", views.LaunchBrowser.as_view(), name="launch-browser"),
    path("geo-position", views.GeoPosition.as_view(), name="geo_position"),
    path('',views.HomepageView.as_view(),name="home"),
]