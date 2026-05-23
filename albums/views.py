from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .models import Album, Photo, AlbumRole
from .forms import AlbumForm, PhotoUploadForm, PhotoEditForm, AlbumRoleForm
from .mixins import AlbumViewMixin, AlbumEditMixin, AlbumAdminMixin


# ─── Album Views ──────────────────────────────────────────────────────────────

class AlbumListView(ListView):
    """Public + authenticated gallery listing."""
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            qs = Album.objects.filter(
                Q(is_public=True) |
                Q(owner=user) |
                Q(collaborators=user)
            ).distinct()
        else:
            qs = Album.objects.filter(is_public=True)
        return qs.select_related('owner').prefetch_related('photos')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['my_albums'] = Album.objects.filter(owner=self.request.user)
        return ctx


class AlbumDetailView(AlbumViewMixin, DetailView):
    model = Album
    template_name = 'albums/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        album = self.get_album()
        ctx['photos'] = album.photos.select_related('uploaded_by')
        ctx['user_role'] = self.get_user_role(album)
        ctx['can_edit'] = album.can_edit(self.request.user)
        ctx['is_owner'] = self.request.user == album.owner
        ctx['roles'] = AlbumRole.objects.filter(album=album).select_related('user')
        return ctx


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # Owner gets admin role
        AlbumRole.objects.create(
            album=self.object,
            user=self.request.user,
            role=AlbumRole.ROLE_ADMIN,
            granted_by=self.request.user
        )
        messages.success(self.request, f'Album "{self.object.title}" created successfully!')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        return ctx


class AlbumUpdateView(AlbumAdminMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Album updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Edit'
        return ctx


class AlbumDeleteView(AlbumAdminMixin, DeleteView):
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('album-list')

    def form_valid(self, form):
        messages.success(self.request, f'Album "{self.object.title}" deleted.')
        return super().form_valid(form)


# ─── Photo Views ──────────────────────────────────────────────────────────────

class PhotoDetailView(AlbumViewMixin, DetailView):
    model = Photo
    template_name = 'albums/photo_detail.html'
    context_object_name = 'photo'

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['album_pk'])
        return self._album

    def get_object(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'], album=self.get_album())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        album = self.get_album()
        photo = self.get_object()
        photos = list(album.photos.values_list('pk', flat=True))
        idx = photos.index(photo.pk)
        ctx['album'] = album
        ctx['can_edit'] = album.can_edit(self.request.user)
        ctx['prev_photo'] = Photo.objects.get(pk=photos[idx - 1]) if idx > 0 else None
        ctx['next_photo'] = Photo.objects.get(pk=photos[idx + 1]) if idx < len(photos) - 1 else None
        return ctx


class PhotoUploadView(AlbumEditMixin, CreateView):
    model = Photo
    form_class = PhotoUploadForm
    template_name = 'albums/photo_upload.html'

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['album_pk'])
        return self._album

    def form_valid(self, form):
        album = self.get_album()
        form.instance.album = album
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        # Set as cover if album has no cover
        if not album.cover_photo:
            album.cover_photo = self.object
            album.save(update_fields=['cover_photo'])
        messages.success(self.request, 'Photo uploaded successfully!')
        return response

    def get_success_url(self):
        return reverse('album-detail', kwargs={'pk': self.kwargs['album_pk']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.get_album()
        return ctx


class PhotoUpdateView(AlbumEditMixin, UpdateView):
    model = Photo
    form_class = PhotoEditForm
    template_name = 'albums/photo_form.html'

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['album_pk'])
        return self._album

    def get_object(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'], album=self.get_album())

    def form_valid(self, form):
        messages.success(self.request, 'Photo updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.get_album()
        return ctx


class PhotoDeleteView(AlbumEditMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'
    context_object_name = 'photo'

    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['album_pk'])
        return self._album

    def get_object(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'], album=self.get_album())

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.error(request, 'Photo not found or it does not belong to this album.')
            return redirect('album-detail', pk=self.kwargs.get('album_pk'))

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Http404:
            messages.error(request, 'Photo not found or already deleted.')
            return redirect('album-detail', pk=self.kwargs.get('album_pk'))

    def get_success_url(self):
        return reverse('album-detail', kwargs={'pk': self.kwargs['album_pk']})

    def form_valid(self, form):
        album = self.get_album()
        photo = self.get_object()
        # Clear cover if this photo was the cover
        if album.cover_photo == photo:
            next_photo = album.photos.exclude(pk=photo.pk).first()
            album.cover_photo = next_photo
            album.save(update_fields=['cover_photo'])
        messages.success(self.request, 'Photo deleted.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.get_album()
        return ctx


class SetCoverPhotoView(AlbumAdminMixin, View):
    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['album_pk'])
        return self._album

    def post(self, request, album_pk, pk):
        album = self.get_album()
        photo = get_object_or_404(Photo, pk=pk, album=album)
        album.cover_photo = photo
        album.save(update_fields=['cover_photo'])
        messages.success(request, 'Cover photo updated!')
        return redirect('album-detail', pk=album_pk)


# ─── RBAC / Member Management ─────────────────────────────────────────────────

class AlbumMemberAddView(AlbumAdminMixin, View):
    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['pk'])
        return self._album

    def post(self, request, pk):
        album = self.get_album()
        form = AlbumRoleForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']  # cleaned to User instance
            role = form.cleaned_data['role']
            if user == album.owner:
                messages.error(request, "Can't change the owner's role.")
            else:
                AlbumRole.objects.update_or_create(
                    album=album, user=user,
                    defaults={'role': role, 'granted_by': request.user}
                )
                # Keep collaborators M2M in sync
                album.collaborators.add(user)
                messages.success(request, f'{user.username} added as {role}.')
        else:
            messages.error(request, 'Invalid form. Please check the username.')
        return redirect('album-detail', pk=pk)


class AlbumMemberRemoveView(AlbumAdminMixin, View):
    def get_album(self):
        if not hasattr(self, '_album'):
            self._album = get_object_or_404(Album, pk=self.kwargs['pk'])
        return self._album

    def post(self, request, pk, user_pk):
        from django.contrib.auth.models import User
        album = self.get_album()
        user = get_object_or_404(User, pk=user_pk)
        if user == album.owner:
            messages.error(request, "Can't remove the album owner.")
        else:
            AlbumRole.objects.filter(album=album, user=user).delete()
            album.collaborators.remove(user)
            messages.success(request, f'{user.username} removed from album.')
        return redirect('album-detail', pk=pk)
