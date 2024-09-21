from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from videoapi.models import Video
from django.contrib.auth.models import User

class VideoAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.video_content = ContentFile(
            b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42\x00\x00\x00\x08free\x00',
            name='test_video.mp4'
        )
        self.video = Video.objects.create(
            title='Sample Video', video_file=self.video_content, uploaded_at='2022-01-01T00:00:00Z'
        )

    def test_file_size_validation_too_small(self):
        small_content = ContentFile(b'\x00' * 1024, name='too_small.mp4')
        url = reverse('video-upload')
        response = self.client.post(url, {'video_file': small_content}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_size_validation_too_large(self):
        large_content = ContentFile(b'\x00' * 30 * 1024 * 1024, name='too_large.mp4')  # 30MB
        url = reverse('video-upload')
        response = self.client.post(url, {'video_file': large_content}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('videoapi.serializers.VideoFileClip')
    def test_video_trimming_valid(self, mock_video_clip):
        mock_clip = MagicMock()
        mock_video_clip.return_value.__enter__.return_value = mock_clip
        mock_clip.duration = 10  # Simulate a 10-second video
        mock_clip.subclip.return_value = mock_clip
        mock_clip.write_videofile = MagicMock()

        url = reverse('trim-video', kwargs={'pk': self.video.pk})
        data = {'start': 1, 'end': 4}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('videoapi.serializers.VideoFileClip')
    def test_video_trimming_invalid(self, mock_video_clip):
        mock_clip = MagicMock()
        mock_video_clip.return_value.__enter__.return_value = mock_clip
        mock_clip.duration = 10  # Simulate a 10-second video

        url = reverse('trim-video', kwargs={'pk': self.video.pk})
        data = {'start': 10, 'end': 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('videoapi.serializers.VideoFileClip')
    def test_video_merging(self, mock_video_clip):
        mock_clip = MagicMock()
        mock_video_clip.return_value.__enter__.return_value = mock_clip
        mock_clip.duration = 15  # Simulate duration for merge logic
        mock_clip.write_videofile = MagicMock()

        another_video = Video.objects.create(title='Another Sample', video_file=self.video_content)
        url = reverse('merge-videos')
        data = {'video_ids': [self.video.pk, another_video.pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

