from django.urls import include, path

urlpatterns = [
    path("auth/", include("api.v1.auth.urls")),
    path("projects/", include("api.v1.projects.urls")),
]
