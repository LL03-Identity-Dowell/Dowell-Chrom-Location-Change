from django.urls import path
from . import views

urlpatterns = [
    path('geo_location', views.Chromeview.as_view(), name='geolocation'),
    path('get-countries',views.GetCountries.as_view()),
    path('download_results', views.download_csv,name="download"),
    path('get-locations',views.GetLocations.as_view()),
    path("launch-browser", views.LaunchBrowser.as_view(), name="launch-browser"),
    path('',views.HomepageView.as_view(),name="home"),
]