from django.urls import path
from . import views

urlpatterns = [
    path('geo_location', views.Chromeview.as_view(), name='geolocation'),
    path('download_results', views.download_csv,name="download"),
    path('get-locations',views.GetLocations.as_view()),
    path('',views.HomepageView.as_view(),name="home"),
]