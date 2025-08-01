import uuid
import os
import base64
from datetime import datetime
from django.core.files.base import ContentFile
from django.conf import settings


def item_upload_to(instance, filename):
    """Callback for dynamic image name and upload dir"""
    file_root, file_ext = os.path.splitext(filename)
    date = datetime.now().strftime("%Y%m%d")
    random_name = str(uuid.uuid4()) + file_ext
    class_name = instance.__class__.__name__.lower()
    filename = "%s_%s" % (date, random_name)
    if class_name == 'relatedimage':
        return '/'.join([settings.GS_NAMESPACE, class_name, instance.content_type.name, filename])
    return '/'.join([settings.GS_NAMESPACE, class_name, filename])


def generate_file_from_data(filename, data):
    if 'data:' in data and ';base64,' in data:
        header, data = data.split(';base64,')
        decoded_file = base64.b64decode(data)
        return ContentFile(decoded_file, name=filename)
    return ContentFile(None, name=filename)
