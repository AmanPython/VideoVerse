from django.urls import path
from .views import VideoListView, VideoUploadView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoListView.as_view(), name='video-detail'),
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
]
