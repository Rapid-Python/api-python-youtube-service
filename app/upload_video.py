import boto3
from extensions import (
    os
)
import mimetypes


class Video:
    def __init__(self):
        self.provider = os.getenv('video_provider')
        if self.provider == 'aws':
            self.provider_client = boto3.client(service_name=os.getenv('aws_storage_name'), region_name=os.getenv('aws_region_name'),
                                     aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))

    def upload_video(self, file_path, file_name):
        if self.provider == 'aws':
            file_mime_type, _ = mimetypes.guess_type(file_name)
            self.provider_client.upload_file(file_path, os.getenv('aws_bucket'), file_name, ExtraArgs={'ContentType': file_mime_type})

    def generate_url(self, file_name):
        return self.provider_client.generate_presigned_url('get_object',
                                                           Params={'Bucket': os.getenv('aws_bucket'), 'Key': file_name},
                                                           ExpiresIn=10)