from celery import shared_task
from moviepy.editor import VideoFileClip, concatenate_videoclips
from .models import Video
from django.conf import settings
import os

@shared_task
def trim_video_task(video_id, start, end):
    video = Video.objects.get(pk=video_id)
    clip = VideoFileClip(video.video_file.path)
    trimmed_clip = clip.subclip(start, end)
    upload_to = video.video_file.field.upload_to
    output_filename = f'trimmed_{os.path.basename(video.video_file.name)}'
    output_path = os.path.join(settings.MEDIA_ROOT, upload_to, output_filename)

    trimmed_clip.write_videofile(output_path)
    trimmed_clip.close()

    trimmed_video = Video(video_file=os.path.join(upload_to, output_filename), is_trimmed=True)
    trimmed_video.save()

    return {'message': 'Video trimmed', 'file': output_filename, 'id': trimmed_video.id}

@shared_task
def merge_videos_task(video_ids):
    clips = [VideoFileClip(Video.objects.get(pk=id).video_file.path) for id in video_ids]
    final_clip = concatenate_videoclips(clips)
    upload_to = Video._meta.get_field('video_file').upload_to
    output_filename = 'merged_video.mp4'
    output_path = os.path.join(settings.MEDIA_ROOT, upload_to, output_filename)

    final_clip.write_videofile(output_path)
    final_clip.close()

    merged_video = Video(video_file=os.path.join(upload_to, output_filename), is_merged=True)
    merged_video.save()

    return {'message': 'Videos merged', 'file': output_filename, 'id': merged_video.id}