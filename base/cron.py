from .models import Test, VideoModel
from django.conf import settings
from django.core.files.storage import default_storage
import os
import subprocess
import logging
import uuid


def my_scheduled_job():
    Test.objects.create(name='test1')

    # def convert_to_mp4(input_file, output_file):
    #     input_extension = input_file.split('.')[-1]
    #     if input_extension.lower() != 'mp4' and input_extension.lower() != 'mov':
    #         output_file = 'uploads/videos/' + input_file.split('.')[0] + str(uuid.uuid4()) + '.mp4'
            
    #         if default_storage.exists(output_file):
    #             return output_file
    #         subprocess.run(['ffmpeg', '-i', input_file.temporary_file_path(), '-vf', 'scale=1080:-2', '-b:v', '800k', output_file])
    #         return output_file
    #     else:
    #         new_file = input_file + str(uuid.uuid4())
    #         return new_file
            

    # def generate_thumbnail(input_file):
    #     output_file = os.path.join(settings.MEDIA_ROOT, 'uploads/thumbnails/' + os.path.splitext(os.path.basename(input_file))[0] + '.jpg')
    #     subprocess.run(['ffmpeg', '-ss', '1.5', '-i', input_file, '-vframes', '1', '-vf', 'scale=1080:-2', output_file])
    #     return output_file

    # unprocessed_videos = VideoModel.objects.filter(is_processed = False)

    # for video in unprocessed_videos:
    #     unprocessed_video_path = os.path.basename(str(video.video_upload))
    #     video_path = video.video_upload.path
    #     video_name = str(os.path.splitext(os.path.basename(video_path))[0])

    #     video_path = os.path.join(settings.MEDIA_ROOT, 'uploads/videos/' + unprocessed_video_path)
    #     input_extension = video.video_upload.name.split('.')[-1]
    #     processed_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/videos/' + unprocessed_video_path + str(uuid.uuid4()) + '.mp4')
    #     thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'uploads/thumbnails/' + video_name + '.jpg')
    #     if input_extension.lower() != 'mp4' and input_extension.lower() != 'mov':
    #         convert_to_mp4(video_path, processed_file_path)
    #         generate_thumbnail(processed_file_path)
    #     else:
    #         processed_file_path = video_path
    #         generate_thumbnail(processed_file_path)
            
    #     video.thumbnail_upload = thumbnail_path
    #     video.is_processed = True
    #     video.view_count = 0
    #     video.save()
    #     logging.debug("Finished running the my_scheduled_job function")
        
my_scheduled_job()