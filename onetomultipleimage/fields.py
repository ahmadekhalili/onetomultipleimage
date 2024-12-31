from django import forms
from django.db import models
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

import ast

from drf_extra_fields.fields import Base64ImageField

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


class OneToMultipleImage(serializers.BaseSerializer):
    image = Base64ImageField()  # deserialized version == SimpleUploadedFile(..), serialized == url
    alt = serializers.CharField(max_length=100, allow_blank=True, default='')
    size = serializers.CharField(max_length=10, allow_blank=True, required=False)

    def base_data(self):  # this is 'def data' from BaseSerializer
        if hasattr(self, 'initial_data') and not hasattr(self, '_validated_data'):
            msg = (
                'When a serializer is passed a `data` keyword argument you '
                'must call `.is_valid()` before attempting to access the '
                'serialized `.data` representation.\n'
                'You should either call `.is_valid()` first, '
                'or access `.initial_data` instead.'
            )
            raise AssertionError(msg)

        if not hasattr(self, '_data'):
            if self.instance is not None and not getattr(self, '_errors', None):
                self._data = self.to_representation(self.instance)
            elif hasattr(self, '_validated_data') and not getattr(self, '_errors', None):
                self._data = self.to_representation(self.validated_data)
            else:
                self._data = self.get_initial()

        return self._data

    @property
    def data(self):        # make return list in to_representation without required passing 'many=True'
        rets = self.base_data()
        return [ReturnDict(ret, serializer=self) for ret in rets]

    def __init__(self, instance=None, sizes=None, upload_to=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance   # self.instance overrides to None in super().__init__, so use after super().__init__
        if not self.instance:      # in writing, sizes and upload_to required
            if not sizes and not upload_to:
                raise ValueError("both of 'sizes' and 'upload_to' arguments must be provided")
            self.sizes = sizes
            self.upload_to = upload_to

    def to_representation(self, obj):
        additional_fields = {field_name: field for field_name, field in self.get_fields().items() if field_name not in ['image', 'alt', 'size']}
        rets = []
        if isinstance(obj[0], dict):
            for icon in obj:
                ret = {'image': icon['image'].url, 'alt': icon.get('alt', ''), 'size': icon.get('size', '')}

                for field_name, field in additional_fields.items():  # add additional fields value to ret if provided
                    if icon.get(field_name):
                        if isinstance(field, serializers.SerializerMethodField):
                            method = getattr(self, f'get_{field_name}')
                            if method(instance):  # prevent 'None' value came to db in SerializerMethodField fields
                                ret[field_name] = method(instance)
                        elif isinstance(field, serializers.BaseSerializer):  # field is a serializer like author field
                            field.instance = icon[field_name]
                            ret[field_name] = field.data
                        else:  # field is normal field like CharField, ...
                            ret[field_name] = field.to_representation(icon[field_name])

                rets.append(ret)
        else:
            for icon in obj:
                rets.append(super().to_representation(icon))
        return rets

    def to_internal_value(self, data):
        obj = ImageCreationSizes(data=data, sizes=self.sizes)
        instances = obj.upload(upload_to=self.upload_to)
        return [{'image': instance, 'alt': instance.alt, 'size': instance.size} for instance in instances]

