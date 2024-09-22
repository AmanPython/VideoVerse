from django.http import FileResponse, StreamingHttpResponse
from rest_framework import views, status
from rest_framework.response import Response
from .models import Video
from .serializers import VideoSerializer
from drf_yasg.utils import swagger_auto_schema
from moviepy.editor import VideoFileClip, concatenate_videoclips
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os
from rest_framework.permissions import AllowAny 
from django.conf import settings
from .tasks import trim_video_task, merge_videos_task

class DownloadVideoView(views.APIView):

    def get(self, request, pk, token):
        serializer = URLSafeTimedSerializer('SECRET_KEY')
        try:
            data = serializer.loads(token, salt='share_video', max_age=3600)  # 1 hour validity
            if data['video_id'] != str(pk):
                return Response({'error': 'Invalid access'}, status=status.HTTP_403_FORBIDDEN)
        except (SignatureExpired, BadSignature):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_403_FORBIDDEN)

        video = Video.objects.get(pk=pk)
        file_handle = video.video_file.open()
        response = StreamingHttpResponse(file_handle, content_type='video/mp4')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(video.video_file.name)
        return response

class StreamVideoView(views.APIView):
    permission_classes = [AllowAny] 
    def get(self, request, pk, token):
        serializer = URLSafeTimedSerializer('SECRET_KEY')
        try:
            data = serializer.loads(token, salt='share_video', max_age=3600)  # 1 hour validity
            if data['video_id'] != pk:
                return Response({'error': 'Invalid access'}, status=status.HTTP_403_FORBIDDEN)
        except (SignatureExpired, BadSignature):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_403_FORBIDDEN)

        video = Video.objects.get(pk=pk)
        file_handle = video.video_file.open()
        response = FileResponse(file_handle, content_type='video/mp4')
        response['Content-Disposition'] = f'inline; filename="{video.video_file.name}"'
        return response

class VideoListView(views.APIView):

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=VideoSerializer, responses={204: 'No Content'})
    def delete(self, request, pk):
        video = Video.objects.get(pk=pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=VideoSerializer, responses={200: VideoSerializer})
    def put(self, request, pk):
        video = Video.objects.get(pk=pk)
        serializer = VideoSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoUploadView(views.APIView):
    @swagger_auto_schema(request_body=VideoSerializer, responses={201: VideoSerializer})
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrimVideoView(views.APIView):
    @swagger_auto_schema(request_body=VideoSerializer, responses={202: 'Accepted'})
    def post(self, request, pk):
        start = request.data.get('start')
        end = request.data.get('end')

        if start is None or end is None:
            return Response({'error': 'Start and end times must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start = float(start)
            end = float(end)
        except ValueError:
            return Response({'error': 'Invalid start or end time format.'}, status=status.HTTP_400_BAD_REQUEST)

        task = trim_video_task.delay(pk, start, end)
        return Response({'message': 'Video trim task started', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

class MergeVideosView(views.APIView):
    @swagger_auto_schema(request_body=VideoSerializer, responses={202: 'Accepted'})
    def post(self, request):
        ids = request.data.get('video_ids')
        if not ids:
            return Response({'error': 'Video IDs must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        task = merge_videos_task.delay(ids)
        return Response({'message': 'Video merge task started', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
class ShareLinkView(views.APIView):

    def get(self, request, pk):
        serializer = URLSafeTimedSerializer('SECRET_KEY')
        token = serializer.dumps({'video_id': pk}, salt='share_video')
        return Response({'link': f'http://0.0.0.0:8000/api/videos/stream/{pk}/{token}'}, status=status.HTTP_200_OK)
