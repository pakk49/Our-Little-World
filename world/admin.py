from django.contrib import admin
from .models import Memory,Photo,Note,Lesson
class PhotoInline(admin.TabularInline):
    model=Photo
    extra=0
@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display=["title","date","author"]
    inlines=[PhotoInline]
admin.site.register(Note)
admin.site.register(Lesson)
