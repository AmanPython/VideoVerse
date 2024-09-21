# videoapi/serializers.py
from rest_framework import serializers
from .models import Video
from moviepy.editor import VideoFileClip

class VideoSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'is_merged','video_file', 'uploaded_at', 'file_size','is_trimmed']

    def get_file_size(self, obj):
        return obj.video_file.size


    def validate_video_file(self, value):
        # Define the minimum and maximum file size in bytes
        min_size = 5 * 1024 * 1024  # 5 MB
        max_size = 25 * 1024 * 1024  # 25 MB

        # Check file size
        if value.size < min_size:
            raise serializers.ValidationError("Video size must be at least 5MB")
        if value.size > max_size:
            raise serializers.ValidationError("Video size must not exceed 25MB")

        # Check duration using moviepy
        video = VideoFileClip(value.temporary_file_path())
        duration = video.duration
        video.close()

        # Define the minimum and maximum duration in seconds
        min_duration = 5
        max_duration = 25

        if duration < min_duration or duration > max_duration:
            raise serializers.ValidationError(f"Video must be between {min_duration} and {max_duration} seconds long")

        return value
