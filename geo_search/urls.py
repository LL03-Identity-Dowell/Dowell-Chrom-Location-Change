from django.urls import path
from . import views

urlpatterns = [
    path('geo_location/', views.Chromeview.as_view(), name='geolocation'),
    path('get_city/<str:city>/',views.CityInfoView.as_view(),name='get_city'),
    path('',views.homepage_view,name="home"),
]