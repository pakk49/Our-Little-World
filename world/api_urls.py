from django.urls import path
from . import api
urlpatterns=[
 path("login/",api.login),
 path("logout/",api.logout),
 path("me/",api.me),
 path("memories/",api.memories),
 path("memories/<int:pk>/",api.memory_detail),
 path("notes/",api.notes),
 path("notes/<int:pk>/",api.note_detail),
 path("lessons/",api.lessons),
 path("lessons/<int:pk>/",api.lesson_detail),
 path("photos/<int:pk>/",api.photo),
 path("scan/",api.scan),
 path("scan/confirm/",api.scan_confirm),
]
