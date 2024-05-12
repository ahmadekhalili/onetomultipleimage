from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from datetime import datetime

from .methods import ImageCreationSizes
from .fields import ListCharField


def image_path_selector(instance, filename):
    if getattr(settings, 'IMAGES_PATH_TYPE', None) == 'jalali':
        try:
            import jdatetime
            date = jdatetime.datetime.fromgregorian(date=datetime.now()).strftime('%Y %-m %-d').split()
        except ImportError:
            raise ImportError("please install 'jdatetime' package")
    else:
        now = datetime.now()
        date = f"{now.year} {now.month} {now.day}".split()
    return f'{instance.__class__.__name__}/{date[0]}/{date[1]}/{date[2]}/{filename}'


class FatherImage(models.Model):
    image = models.ImageField(_('image'), upload_to=image_path_selector)
    alt = models.CharField(_('alt'), max_length=55, unique=True, null=True)
    sizes = ListCharField(_('sizes'), max_length=255)  # input data like: ['120', '240', '480']
    # imagesizes, reverse relation

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre_image = self.image
        self.pre_alt = self.alt

    def __str__(self):
        return f'{self.alt}'

    def save(self, *args, **kwargs):
        alt = self.alt    # self.alt is None for default
        change = True if self.id else False
        if not change:      # FatherImage creation
            self.alt = ImageCreationSizes.add_size_to_alt('default', alt)
        elif alt != self.pre_alt:         # FatherImage updating, prevent alt overriding like: 'asd32a-default-default'
            self.alt = ImageCreationSizes.add_size_to_alt('default', alt)
        super().save(*args, **kwargs)
        if not change:     # ImageSizes creation
            img = ImageCreationSizes(data={'image': self.image, 'alt': alt}, sizes=self.sizes)
            instances = img.build(model=ImageSizes, upload_to=ImageSizes._meta.get_field('image').upload_to)
            for instance, size in zip(instances, self.sizes):
                instance.father, instance.size = self, size
            ImageSizes.objects.bulk_create(instances)
        else:         # ImageSizes updating
            data = {'alt': alt, 'image': self.image if self.image is not self.pre_image else None}
            img = ImageCreationSizes(data=data, sizes=self.sizes)
            instances = self.imagesizes.all()
            instances = img.update(instances=instances, upload_to=ImageSizes._meta.get_field('image').upload_to)
            if data.get('image'):
                for instance in instances:
                    image_data = instance.image.file
                    instance.image.save(instance.image.name, image_data)   # image field isn't saved with bulk_update
            for instance, size in zip(instances, self.sizes):
                instance.size, instance.father_id = size, self.id
            ImageSizes.objects.bulk_update(instances, [*list(data.keys()), *['size', 'father_id']])


class ImageSizes(models.Model):
    image = models.ImageField(_('image'), upload_to=image_path_selector)
    alt = models.CharField(_('alt'), max_length=55, unique=True, null=True)
    size = models.CharField(_('size'), max_length=20)
    father = models.ForeignKey(FatherImage, related_name='imagesizes', on_delete=models.CASCADE, verbose_name=_('image'))

    class Meta:
        verbose_name = _('Image size')
        verbose_name_plural = _('Images sizes')

    def __str__(self):
        return f'{self.alt}'
