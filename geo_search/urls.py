from django.urls import path
from . import views

urlpatterns = [
    path('geo_location/', views.Chromeview.as_view(), name='geolocation'),
]