import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if data == "":
            raise serializers.ValidationError("Добавьте изображение.")
        if isinstance(data, str) and data.startswith("data:image"):
            header, image_data = data.split(";base64,", 1)
            extension = header.split("/")[-1]
            decoded = base64.b64decode(image_data)
            detected = imghdr.what(None, decoded)
            extension = detected or extension
            data = ContentFile(
                decoded,
                name=f"{uuid.uuid4().hex}.{extension}",
            )
        return super().to_internal_value(data)
