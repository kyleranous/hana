from django.urls import (
    path,
    include,
)


urlpatterns = [
    path('', include('swarman.api.v1_0.urls')),
    # path('v1.0/', include('swarman.api.v1_0.urls')),
]
