from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import io
import os
import uuid
import itertools
from datetime import datetime
from PIL import Image as PilImage


class ImageCreationSizes:
    # in this class we receive image binary/base64 and save it to disk with specified sizes. if a model specified,
    # that models field will be filled instead, for example: image1.image = size1, image2.image = size2, ...
    def __init__(self, data, sizes, name=None):
        # data is like: {'image': InMemoryUploadFIle(..)} (keys are instance fields)
        # sizes like:
        self.base_path = str(settings.BASE_DIR)  # is like: /home/akh/eCommerce-web-api/ictsun
        self.data = data.copy()  # we don't want change outside variables has been passed to our class.
        self.sizes = sizes
        self.name = name if name else uuid.uuid4().hex[:12]
        self.uuid_alt = False
        # when data is like: {'alt': None, ...}, data['alt'] must be removed and replaced with uuid
        try:
            alt = self.data.pop('alt')
            if not alt:
                self.uuid_alt = True       # in updating, if alt not provided by user, don't update instance.alt
                alt = uuid.uuid4().hex[:6]
        except:
            alt = uuid.uuid4().hex[:6]
        self.alt = alt

    @staticmethod
    def add_size_to_alt(size, text=None):
        # text == pre alt
        pre_alt = text if text else uuid.uuid4().hex[:6]
        return f'{pre_alt}-{size}'

    def get_file_stream(self):
        file = self.files['file'].read() if self.files.get('file') else self.files['image_icon_set-0-image'].read()
        return io.BytesIO(file)

    def get_path(self, middle_path=None):
        # get path like: '/media/posts_images/icons/' returns like: '/media/posts_images/icons/1402/3/15/'
        if not middle_path:
            middle_path = 'posts_images/icons/'
        middle_path = '/media/' + middle_path
        if getattr(settings, 'IMAGES_PATH_TYPE', None) == 'jalali':
            try:
                import jdatetime
                date = jdatetime.datetime.fromgregorian(date=datetime.now()).strftime('%Y %-m %-d').split()
            except ImportError:
                raise ImportError("please install 'jdatetime' package")
        else:
            now = datetime.now()
            date = f"{now.year} {now.month} {now.day}".split()     # %Y %-m %-d format doesn't work in windows
        return f'{middle_path}/{date[0]}/{date[1]}/{date[2]}/'

    def _save(self, opened_image, full_name, format, instance, att_name, upload_to=None):
        if isinstance(opened_image, PilImage.Image):
            if instance:           # save image by image field (need write to disk)
                buffer = io.BytesIO()
                opened_image.save(buffer, format=format)
                setattr(instance, att_name, SimpleUploadedFile(full_name, buffer.getvalue()))
                # field.upload_to must change to our path, also '/media/' must remove from path otherwise raise error
                if upload_to:
                    if callable(upload_to):    # if upload_to is function
                        getattr(instance, att_name).field.upload_to = upload_to
                    else:                      # if is string
                        getattr(instance, att_name).field.upload_to = upload_to.replace('/media/', '', 1)
                return None
            else:                  # save image (write to disk) by pillow.save()
                opened_image.save(self.base_path + upload_to + full_name)
                return SimpleUploadedFile(full_name, open(self.base_path + upload_to + full_name, 'rb').read())

    def build(self, model, att_name='image', opened_image=None, upload_to=None):
        instances = [model(alt=f'{self.alt}-{size}', **self.data) for size in self.sizes]
        return self.save(opened_image=opened_image, upload_to=upload_to, instances=instances, att_name=att_name)

    def update(self, instances, att_name='image', opened_image=None, upload_to=None):
        instances = list(instances)[:len(self.sizes)]
        for size, instance in zip(self.sizes, instances):
            # if we have alt in our instance and user don't want update it, so don't change alt.
            instance.alt = f'{self.alt}-{size}' if not self.uuid_alt or not instance.alt else instance.alt
            [setattr(instance, key, self.data[key]) for key in self.data]
        return self.save(opened_image=opened_image, upload_to=upload_to, instances=instances, att_name=att_name)

    def upload(self, upload_to, opened_image=None):
        # upload icons without using any models. returned value is simple python objects. each obj has 4 attr. like:
        # image=<SimpleUploadedFile image.jpg>, url=/media/../qwer43asd2e4-720.JPG, alt=, size=720
        return self.save(opened_image=opened_image, upload_to=upload_to)

    def save(self, opened_image=None, upload_to=None, instances=None, att_name='image'):
        '''
        - opened_image can be binary (multipart form-data) or base64.
        - upload_to is like: posts_images/icons/ will be convert to: /media/posts_images/icons/
        - model is django model class. if you specify model, image will be saved to disk by model field,
        (instance.att_name.save()) instead of PilImage.save()
        - instances uses when associating with django models (build and update methods)
        1- returned value: {model_instance1, model_instance2, ...}
        2- returned value: {<Upload object 1 - (.image .url .size)>, <Upload object 2 - (.image .url .size)>}
        '''
        if not upload_to and not instances:  # specify 'upload_to' or take from instances (django's image field)
            raise ValueError("'instances' and 'upload_to' can't be None at the same time")

        class Upload:
            def __init__(self, image, url, alt, size, **kwargs):
                kwargs['image'], kwargs['url'], kwargs['alt'], kwargs['size'] = image, url, alt, size
                [setattr(self, key, kwargs[key]) for key in kwargs]

            def __repr__(self):
                return '<Upload object {} - (.image .url .alt .size)>'.format(self.alt)  # self.alt contain size too

        if not instances:
            instances = []

        try:         # binary file (multipart form-data)
            stream = io.BytesIO(self.data['image'].read())
        except:      # base64 file
            try:
                import base64
                stream = io.BytesIO(base64.b64decode(self.data['image'].split(';base64,')[1]))
            except:       # when no image provided (like when update 'alt' field only)
                return instances
        opened_image = PilImage.open(stream) if not opened_image else opened_image

        if not callable(upload_to) and upload_to:  # upload_to is str
            if upload_to[-1] == '/':
                upload_to = upload_to[:-1]
            upload_to = self.get_path(upload_to)
            if not os.path.exists(self.base_path + upload_to):
                os.makedirs(self.base_path + upload_to)

        iter_instances, objects = itertools.cycle(instances) if instances else None, []
        if isinstance(opened_image, PilImage.Image):
            format = opened_image.format              # opened_image.format is like: "JPG"
            height, width = opened_image.size                 # opened_image.size is like: (1080, 1920)
            aspect_ratio = height / width
            for height in self.sizes:
                if height.isdigit():
                    height = int(height)
                    resized = opened_image.resize((height, int(height / aspect_ratio)))
                else:
                    resized = opened_image  # for 'default' size
                full_name = f'{self.name}-{height}' + f'.{format}'
                instance = next(iter_instances) if iter_instances else None
                upload_image = self._save(resized, full_name, format, instance, att_name, upload_to=upload_to)
                # url is like: /media/posts_images/1402/3/20/qwer43asd2e4-720.JPG
                if not instances:
                    objects += [Upload(image=upload_image, url=upload_to+full_name, alt=f'{self.alt}-{height}', size=height)]
            return instances or objects

        elif isinstance(opened_image, io.BufferedReader):      # open image by built-in function open()
            pass
        else:
            raise Exception('opened_image is not object of PilImage or python built in .open()')
