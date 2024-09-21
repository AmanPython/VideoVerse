from rest_framework import status
from rest_framework.response import Response
from .models import Video
from drf_yasg.utils import swagger_auto_schema
from .serializers import VideoSerializer
from moviepy.editor import VideoFileClip, concatenate_videoclips
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from django.http import FileResponse

def download_video(request, pk):
    video = Video.objects.get(pk=pk)
    file_handle = video.video_file.open()
    response = FileResponse(file_handle, content_type='video/mp4')
    response['Content-Disposition'] = 'attachment; filename="%s"' % video.video_file.name
    return response


class DownloadVideoView(views.APIView):
    permission_classes = [IsAuthenticated]
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
        response = FileResponse(file_handle, content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{video.video_file.name}"'
        return response

class VideoListView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        video = Video.objects.get(pk=pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        video = Video.objects.get(pk=pk)
        serializer = VideoSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoUploadView(views.APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=VideoSerializer, responses={201: VideoSerializer})
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TrimVideoView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        start = request.data.get('start')
        end = request.data.get('end')
        video = Video.objects.get(pk=pk)
        clip = VideoFileClip(video.video_file.path)
        trimmed_clip = clip.subclip(start, end)
        output_filename = f'trimmed_{video.video_file.name}'
        # output_path = f'media/videos/{output_filename}'  # Adjust the path as needed
        trimmed_clip.write_videofile(output_filename)

        # Save the trimmed video to the database
        trimmed_video = Video(video_file=output_filename, is_trimmed=True)
        trimmed_video.save()

        return Response({'message': 'Video trimmed', 'file': output_filename, 'id': trimmed_video.id}, status=status.HTTP_200_OK)

class MergeVideosView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        ids = request.data.get('video_ids')
        clips = [VideoFileClip(Video.objects.get(pk=id).video_file.path) for id in ids]
        final_clip = concatenate_videoclips(clips)
        output_filename = 'merged_video.mp4'
        final_clip.write_videofile(output_filename)

        # Save the merged video to the database
        video = Video(video_file=output_filename, is_merged=True)
        video.save()

        return Response({'message': 'Videos merged', 'file': output_filename, 'id': video.id}, status=status.HTTP_200_OK)

class ShareLinkView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        serializer = URLSafeTimedSerializer('SECRET_KEY')
        token = serializer.dumps({'video_id': pk}, salt='share_video')
        return Response({'link': f'http://192.168.29.170:8000/api/videos/download/{pk}/?token={token}'}, status=status.HTTP_200_OK)
