# videoapi/serializers.py
from rest_framework import serializers
from .models import Video
from moviepy.editor import VideoFileClip
import os

class VideoSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Video
        fields = ['id', 'title', 'is_merged', 'video_file', 'uploaded_at', 'file_size', 'is_trimmed']

    def get_file_size(self, obj):
        return obj.video_file.size

    # def validate_video_file(self, value):
    #     # Define the minimum and maximum file size in bytes
    #     min_size = 5 * 1024 * 1024  # 5 MB
    #     max_size = 25 * 1024 * 1024  # 25 MB

    #     # Check file size
    #     if value.size < min_size:
    #         raise serializers.ValidationError("Video size must be at least 5MB")
    #     if value.size > max_size:
    #         raise serializers.ValidationError("Video size must not exceed 25MB")

    #     # Check duration using moviepy
    #     video = VideoFileClip(value.temporary_file_path())
    #     duration = video.duration
    #     video.close()

    #     # Define the minimum and maximum duration in seconds
    #     min_duration = 5
    #     max_duration = 25

    #     if duration < min_duration or duration > max_duration:
    #         raise serializers.ValidationError(f"Video must be between {min_duration} and {max_duration} seconds long")

    #     return value

    def validate(self, attrs):
        # If title is missing or blank, set it to the default value based on the file name
        if not attrs.get('title'):
            video_file = attrs.get('video_file')
            if video_file:
                attrs['title'] = os.path.splitext(video_file.name)[0]
        return attrs
