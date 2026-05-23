from django.contrib import admin
from .models import Album, Photo, AlbumRole


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'photo_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'owner__username']
    raw_id_fields = ['owner', 'cover_photo']
    filter_horizontal = ['collaborators']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'album', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'album__title']
    raw_id_fields = ['album', 'uploaded_by']


@admin.register(AlbumRole)
class AlbumRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'album', 'role', 'granted_by', 'granted_at']
    list_filter = ['role']
