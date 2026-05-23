from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import cloudinary


class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    collaborators = models.ManyToManyField(
        User, related_name='shared_albums', blank=True
    )
    cover_photo = models.ForeignKey(
        'Photo', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='cover_for'
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('album-detail', kwargs={'pk': self.pk})

    def can_edit(self, user):
        """Check if user can edit this album."""
        if not user.is_authenticated:
            return False
        return (
            user == self.owner or
            user in self.collaborators.all() or
            user.is_staff
        )

    def can_view(self, user):
        """Check if user can view this album."""
        if self.is_public:
            return True
        if not user.is_authenticated:
            return False
        return (
            user == self.owner or
            user in self.collaborators.all() or
            user.is_staff
        )

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photoalbum/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    taken_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Photo {self.pk} in {self.album.title}"

    def get_absolute_url(self):
        return reverse('photo-detail', kwargs={'album_pk': self.album.pk, 'pk': self.pk})

    @property
    def image_url(self):
        if self.image:
            if getattr(settings, 'USE_CLOUDINARY', False):
                return cloudinary.CloudinaryImage(str(self.image)).build_url(
                    width=800, crop='limit', quality='auto', fetch_format='auto'
                )
            return self.image.url
        return ''

    @property
    def thumbnail_url(self):
        if self.image:
            if getattr(settings, 'USE_CLOUDINARY', False):
                return cloudinary.CloudinaryImage(str(self.image)).build_url(
                    width=400, height=300, crop='fill', gravity='auto',
                    quality='auto', fetch_format='auto'
                )
            return self.image.url
        return ''


class AlbumRole(models.Model):
    """Fine-grained RBAC: roles within an album."""
    ROLE_VIEWER = 'viewer'
    ROLE_CONTRIBUTOR = 'contributor'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_CONTRIBUTOR, 'Contributor'),
        (ROLE_ADMIN, 'Admin'),
    ]

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='roles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='album_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='granted_roles'
    )

    class Meta:
        unique_together = ('album', 'user')

    def __str__(self):
        return f"{self.user.username} — {self.role} in {self.album.title}"
