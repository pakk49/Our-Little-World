from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from world.views import private_image
urlpatterns=[
 path("admin/",admin.site.urls),
 path("login/",auth_views.LoginView.as_view(template_name="world/login.html"),name="login"),
 path("logout/",auth_views.LogoutView.as_view(),name="logout"),
 path("private-image/<int:pk>/",private_image,name="private_image"),
 path("api/",include("world.api_urls")),
 path("",include("world.urls")),
]
