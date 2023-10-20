from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse

def reference_is_live(request):
    return HttpResponse("Reference is live, please visit <a href='https://geopositioning.uxlivinglab.online/api</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('geo_search.urls')),
    path('', reference_is_live),
]
