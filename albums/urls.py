from django.urls import path
from . import views

urlpatterns = [
    # Albums
    path('', views.AlbumListView.as_view(), name='album-list'),
    path('create/', views.AlbumCreateView.as_view(), name='album-create'),
    path('<int:pk>/', views.AlbumDetailView.as_view(), name='album-detail'),
    path('<int:pk>/edit/', views.AlbumUpdateView.as_view(), name='album-update'),
    path('<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album-delete'),

    # Member management (RBAC)
    path('<int:pk>/members/add/', views.AlbumMemberAddView.as_view(), name='album-member-add'),
    path('<int:pk>/members/<int:user_pk>/remove/', views.AlbumMemberRemoveView.as_view(), name='album-member-remove'),

    # Photos
    path('<int:album_pk>/photos/upload/', views.PhotoUploadView.as_view(), name='photo-upload'),
    path('<int:album_pk>/photos/<int:pk>/', views.PhotoDetailView.as_view(), name='photo-detail'),
    path('<int:album_pk>/photos/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo-update'),
    path('<int:album_pk>/photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo-delete'),
    path('<int:album_pk>/photos/<int:pk>/set-cover/', views.SetCoverPhotoView.as_view(), name='photo-set-cover'),
]
