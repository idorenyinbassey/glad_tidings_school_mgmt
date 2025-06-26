from django.contrib import admin
from .models import ClassTimetable, ELibraryResource, SchoolCalendarEvent, Announcement

@admin.register(ClassTimetable)
class ClassTimetableAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'day_of_week', 'period', 'subject', 'teacher', 'start_time', 'end_time')
    search_fields = ('class_name', 'subject', 'teacher', 'day_of_week')

@admin.register(ELibraryResource)
class ELibraryResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_at', 'uploaded_by')
    search_fields = ('title', 'author')

@admin.register(SchoolCalendarEvent)
class SchoolCalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_at', 'created_by')
    search_fields = ('title',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'created_by', 'is_active')
    search_fields = ('title',)
