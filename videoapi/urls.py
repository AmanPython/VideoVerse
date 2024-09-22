from django.urls import path
from . import views

urlpatterns = [
    path('videos/', views.VideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', views.VideoListView.as_view(), name='video-detail'),
    path('videos/download/<int:pk>/<str:token>/', views.DownloadVideoView.as_view(), name='video-download'),
    path('videos/stream/<int:pk>/<str:token>/', views.StreamVideoView.as_view(), name='video-stream'),
    path('upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('trim/<int:pk>/', views.TrimVideoView.as_view(), name='trim-video'),
    path('merge/', views.MergeVideosView.as_view(), name='merge-videos'),
    path('share/<int:pk>/', views.ShareLinkView.as_view(), name='share-video'),
]

