# Generated by Django 5.0.5 on 2024-05-08 06:56

import onetomultipleimage.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=onetomultipleimage.models.image_path_selector, verbose_name='image')),
                ('alt', models.CharField(max_length=55, null=True, unique=True, verbose_name='alt')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
        migrations.CreateModel(
            name='ImageSizes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=onetomultipleimage.models.image_path_selector, verbose_name='image')),
                ('alt', models.CharField(max_length=55, unique=True, verbose_name='alt')),
                ('size', models.CharField(max_length=20, verbose_name='size')),
                ('father', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagesizes', to='onetomultipleimage.image', verbose_name='image')),
            ],
            options={
                'verbose_name': 'Image size',
                'verbose_name_plural': 'Images sizes',
            },
        ),
    ]