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

        video = Video.objects.get(pk=pk)
        clip = VideoFileClip(video.video_file.path)
        trimmed_clip = clip.subclip(start, end)
        upload_to = video.video_file.field.upload_to
        output_filename = f'trimmed_{os.path.basename(video.video_file.name)}'
        output_path = os.path.join(settings.MEDIA_ROOT, upload_to, output_filename)

        trimmed_clip.write_videofile(output_path)
        trimmed_clip.close()

        trimmed_video = Video(video_file=os.path.join(upload_to, output_filename), is_trimmed=True)
        trimmed_video.save()

        return Response({'message': 'Video trimmed', 'file': output_filename, 'id': trimmed_video.id}, status=status.HTTP_200_OK)


class MergeVideosView(views.APIView):

    def post(self, request):
        ids = request.data.get('video_ids')
        clips = [VideoFileClip(Video.objects.get(pk=id).video_file.path) for id in ids]
        final_clip = concatenate_videoclips(clips)
        upload_to = Video._meta.get_field('video_file').upload_to
        output_filename = 'merged_video.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, upload_to, output_filename)

        final_clip.write_videofile(output_path)
        final_clip.close()

        merged_video = Video(video_file=os.path.join(upload_to, output_filename), is_merged=True)
        merged_video.save()

        return Response({'message': 'Videos merged', 'file': output_filename, 'id': merged_video.id}, status=status.HTTP_200_OK)

class ShareLinkView(views.APIView):

    def get(self, request, pk):
        serializer = URLSafeTimedSerializer('SECRET_KEY')
        token = serializer.dumps({'video_id': pk}, salt='share_video')
        return Response({'link': f'http://0.0.0.0:8000/api/videos/stream/{pk}/{token}'}, status=status.HTTP_200_OK)
