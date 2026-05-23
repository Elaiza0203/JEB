from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Album, AlbumRole


class AlbumViewMixin:
    """Mixin that loads album and checks view permission."""

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs.get('album_pk') or self.kwargs.get('pk'))
        return self._album

    def get_user_role(self, album):
        user = self.request.user
        if not user.is_authenticated:
            return None
        if user.is_staff or user == album.owner:
            return AlbumRole.ROLE_ADMIN
        try:
            role_obj = AlbumRole.objects.get(album=album, user=user)
            return role_obj.role
        except AlbumRole.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        album = self.get_album()
        if not album.can_view(request.user):
            raise PermissionDenied("You don't have permission to view this album.")
        return super().dispatch(request, *args, **kwargs)


class AlbumEditMixin(LoginRequiredMixin):
    """Mixin that enforces edit permission (owner, contributor, admin, staff)."""

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs.get('album_pk') or self.kwargs.get('pk'))
        return self._album

    def get_user_role(self, album):
        user = self.request.user
        if not user.is_authenticated:
            return None
        if user.is_staff or user == album.owner:
            return AlbumRole.ROLE_ADMIN
        try:
            role_obj = AlbumRole.objects.get(album=album, user=user)
            return role_obj.role
        except AlbumRole.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        album = self.get_album()
        role = self.get_user_role(album)
        if role not in (AlbumRole.ROLE_CONTRIBUTOR, AlbumRole.ROLE_ADMIN):
            raise PermissionDenied("You need at least Contributor access to perform this action.")
        return super().dispatch(request, *args, **kwargs)


class AlbumAdminMixin(LoginRequiredMixin):
    """Mixin that enforces admin-only access (owner or staff)."""

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs.get('album_pk') or self.kwargs.get('pk'))
        return self._album

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        album = self.get_album()
        if not (request.user == album.owner or request.user.is_staff):
            raise PermissionDenied("Only the album owner or site admins can perform this action.")
        return super().dispatch(request, *args, **kwargs)
