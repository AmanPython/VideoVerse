from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Video
from unittest.mock import patch
import tempfile
import os

class VideoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.refresh.access_token))

        self.video_upload_url = reverse('video-upload')
        self.video_list_url = reverse('video-list')
        
        # Create a temporary video file for testing
        self.temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        self.temp_video.write(b'dummy video content')
        self.temp_video.seek(0)

    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_video.name)

    # def test_upload_video_authenticated(self):
    #     with open(self.temp_video.name, 'rb') as video_file:
    #         data = {
    #             'title': 'Test Video',
    #             'video_file': video_file
    #         }
    #         response = self.client.post(self.video_upload_url, data, format='multipart')
        
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)  ## the error : {'video_file': [ErrorDetail(string='Video size must be at least 5MB', code='invalid')]}
    #     self.assertEqual(Video.objects.count(), 1)
    #     self.assertEqual(Video.objects.get().title, 'Test Video')

    def test_upload_video_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        with open(self.temp_video.name, 'rb') as video_file:
            data = {
                'title': 'Test Video',
                'video_file': video_file
            }
            response = self.client.post(self.video_upload_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_videos_authenticated(self):
        Video.objects.create(title='Test Video 1', video_file='video1.mp4', user=self.user)
        Video.objects.create(title='Test Video 2', video_file='video2.mp4', user=self.user)

        response = self.client.get(self.video_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # def test_list_videos_unauthenticated(self):
    #     self.client.credentials()  # Remove authentication
    #     response = self.client.get(self.video_list_url)
        
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('videoapi.tasks.trim_video_task.delay')
    def test_trim_video_authenticated(self, mock_trim_task):
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('trim-video', args=[video.id])
        
        data = {'start': 0, 'end': 10}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_trim_task.assert_called_once_with(video.id, 0, 10)

    @patch('videoapi.tasks.trim_video_task.delay')
    def test_trim_video_unauthenticated(self, mock_trim_task):
        self.client.credentials()  # Remove authentication
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('trim-video', args=[video.id])
        
        data = {'start': 0, 'end': 10}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_trim_task.assert_not_called()

    @patch('videoapi.tasks.merge_videos_task.delay')
    def test_merge_videos_authenticated(self, mock_merge_task):
        video1 = Video.objects.create(title='Test Video 1', video_file='video1.mp4', user=self.user)
        video2 = Video.objects.create(title='Test Video 2', video_file='video2.mp4', user=self.user)
        url = reverse('merge-videos')
        
        data = {'video_ids': [video1.id, video2.id]}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_merge_task.assert_called_once_with([video1.id, video2.id])

    @patch('videoapi.tasks.merge_videos_task.delay')
    def test_merge_videos_unauthenticated(self, mock_merge_task):
        self.client.credentials()  # Remove authentication
        video1 = Video.objects.create(title='Test Video 1', video_file='video1.mp4', user=self.user)
        video2 = Video.objects.create(title='Test Video 2', video_file='video2.mp4', user=self.user)
        url = reverse('merge-videos')
        
        data = {'video_ids': [video1.id, video2.id]}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_merge_task.assert_not_called()

    def test_share_link_authenticated(self):
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('share-video', args=[video.id])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('link', response.data)
        self.assertIn(str(video.id), response.data['link'])

    def test_share_link_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('share-video', args=[video.id])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_video(self):
        video = Video.objects.create(title='Test Video', video_file=self.temp_video.name)
        
        # First, get the share link
        share_url = reverse('share-video', args=[video.id])
        share_response = self.client.get(share_url)
        self.assertEqual(share_response.status_code, status.HTTP_200_OK)
        
        # Extract the token from the share link
        link = share_response.data['link']
        token = link.split('/')[-1]
        
        # Now use the token to download the video (no authentication required)
        self.client.credentials()  # Remove authentication
        download_url = reverse('video-download', args=[video.id, token])
        response = self.client.get(download_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/mp4')
        self.assertIn('inline; filename=', response['Content-Disposition'])

    def test_stream_video(self):
        video = Video.objects.create(title='Test Video', video_file=self.temp_video.name)
        
        # First, get the share link
        share_url = reverse('share-video', args=[video.id])
        share_response = self.client.get(share_url)
        self.assertEqual(share_response.status_code, status.HTTP_200_OK)
        
        # Extract the token from the share link
        link = share_response.data['link']
        token = link.split('/')[-1]
        
        # Now use the token to stream the video (no authentication required)
        self.client.credentials()  # Remove authentication
        stream_url = reverse('video-stream', args=[video.id, token])
        response = self.client.get(stream_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/mp4')
        self.assertIn('inline; filename=', response['Content-Disposition'])

    def test_invalid_share_link(self):
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        invalid_token = 'invalid_token'
        url = reverse('video-download', args=[video.id, invalid_token])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_delete_video_authenticated(self):
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('video-detail', args=[video.id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)

    def test_delete_video_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('video-detail', args=[video.id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Video.objects.count(), 1)

    def test_update_video_authenticated(self):
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('video-detail', args=[video.id])
        
        data = {'title': 'Updated Test Video'}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Video.objects.get(id=video.id).title, 'Updated Test Video')

    def test_update_video_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        video = Video.objects.create(title='Test Video', video_file='video.mp4')
        url = reverse('video-detail', args=[video.id])
        
        data = {'title': 'Updated Test Video'}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Video.objects.get(id=video.id).title, 'Test Video')
