# Django
from django.urls import path

# local Django
from . import views


app_name = "core" 

urlpatterns = [
    path(
        "", 
        views.homepage, name="homepage"),
    path(
        "register/", 
        views.register_request, 
        name="register"),
    path(
        "login/", 
        views.login_request, 
        name="login"),
    path(
        "logout/", 
        views.logout_request, 
        name="logout"),
    path(
        "update/", 
        views.update_profile, 
        name="update"),
    path(
        "update_profile_success/", 
        views.update_profile_success, 
        name="update_profile_success"),
    # path("upload/", views.image_upload_view, name="upload")
    path(
        "upload/", 
        views.post, 
        name="upload"),
    # path(
    #     "download/",
    #     views.download_file,
    #     name="download"),
    path(
        "removebackground/", 
        views.remove_background_image, 
        name="removebackground"),
    path(
        "generatecircle/<int:x>/<int:y>/",
        views.generate_circle,
        name="generatecircle"),
    path(
        "segmentregions/",
        views.segment_regions,
        name="segmentregions",
    ),
]
