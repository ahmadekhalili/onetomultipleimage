from django import forms
from django.db import models
from rest_framework import serializers

import ast

from .methods import ImageCreationSizes


class ListCharField(models.CharField):
    description = "A CharField that stores a list of strings as a comma-separated string."

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return value.split(',')

    def get_prep_value(self, value):
        if isinstance(value, list):
            return ','.join(str(item) for item in value)
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        return value.split(',')


class ListCharFormField(forms.CharField):
    def to_python(self, value):
        # Ensures the value is converted to a list, whether coming from a form or directly from Python code
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return value

    def clean(self, value):
        if isinstance(value, str):
            lis = ast.literal_eval(value)
            value = ','.join(lis)
        return value


class OneToMultipleImage(serializers.Serializer):
    def __init__(self, instance=None, sizes=None, upload_to=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance   # self.instance overrides to None in super().__init__, so use after super().__init__
        if not self.instance:      # in writing, sizes and upload_to required
            if not sizes and not upload_to:
                raise ValueError("both of 'sizes' and 'upload_to' arguments must be provided")
            self.sizes = sizes
            self.upload_to = upload_to

    def to_representation(self, value):
        if isinstance(value, list):
            result = {}
            for image_icon in value:
                size = image_icon.size
                result[size] = {'image': image_icon.url, 'alt': getattr(image_icon, 'alt', '')}
            return result
        else:
            return {'image': value.url, 'alt': getattr(value, 'alt', '')}

    def to_internal_value(self, data):
        obj = ImageCreationSizes(data=data, sizes=self.sizes)
        instances = obj.upload(upload_to=self.upload_to)
        return instances
