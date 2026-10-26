from django.urls import path
from . import views as v
urlpatterns=[
 path("",v.home,name="home"),
 path("memories/",v.memories,name="memories"),
 path("memories/new/",v.memory_edit,name="memory_new"),
 path("memories/<int:pk>/",v.memory_edit,name="memory_edit"),
 path("memories/<int:pk>/delete/",v.memory_delete,name="memory_delete"),
 path("notes/",v.notes,name="notes"),
 path("notes/new/",v.note_edit,name="note_new"),
 path("notes/<int:pk>/",v.note_edit,name="note_edit"),
 path("notes/<int:pk>/delete/",v.note_delete,name="note_delete"),
 path("schedule/",v.schedule,name="schedule"),
 path("schedule/new/",v.lesson_edit,name="lesson_new"),
 path("schedule/<int:pk>/",v.lesson_edit,name="lesson_edit"),
 path("schedule/<int:pk>/delete/",v.lesson_delete,name="lesson_delete"),
 path("scan/",v.scan,name="scan"),
 path("scan/confirm/",v.scan_confirm,name="scan_confirm"),
 path("us/",v.us,name="us"),
]
