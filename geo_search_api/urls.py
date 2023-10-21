from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse

def reference_is_live(request):
    return HttpResponse("Reference is live, please visit link : https://geopositioning.uxlivinglab.online/api")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('geo_search.urls')),
    path('', reference_is_live),
<<<<<<< HEAD
]
=======
]
>>>>>>> be92749c57e4c79c748ce6e3e2777b96e51e40fc
