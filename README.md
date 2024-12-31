# onetomultipleimage

onetomultipleimage is a django package to convert one image to several sizes. You give an image (with sizes), and receive uploaded images with that sizes. It can be used in REST or django model.

## installation

1- run: ``` pip install onetomultipleimage[jalali]```  

To install onetomultipleimage with Jalali date support, add ```[jalali]``` part.  
also put `IMAGES_PATH_TYPE='jalali'` in settings.py, now jalali date path used (instead default gregorian) like:  
__/media/FatherImage/1401/12/13/small.jpg__ instead of: __/media/FatherImage/2023/3/4/small.jpg__

2- to install **onetomultipleimage** models, add 'onetomultipleimage' to `INSTALLED_APPS` of project's settings.py
after makemigrations and migrate, models will be created.


&nbsp;
## Serializer Field: OneToMultipleImage

Receives image in Base64/form-data with list of sizes and generate images with specified sizes.

`OneToMultipleImage` fields:

- **image**:
`Base64ImageField`, accept data in base64 or form-data in writing and retursn uploaded image object. in representing, shows image url.

- **alt**:
`CharField`, stores alt of the image. if not alt value is provided, the program fill it with a 6 digit uuid followed by the image size.

- **size**:
`CharField`, stores size of the image as string. optional.

`OneToMultipleImage` arguments:

- **sizes**:
list of sizes in str. for generate original image use 'default'. required in writing.

- **upload_to**:
path in str for uploads image. required in writing.

- **data**:
it is same `data` pass to serializer in writing, but structure should be:  
{'image': formdata_file/Base64_str, 'alt': 'some_alt'}  
  - `image` key is required. can be formdata file or Base64 str.
  - `alt` is optional and will fill auto if left blank.


**Example 1**:
```python
from onetomultipleimage.fields import OneToMultipleImage
image = request.FILES['image']
serializer = OneToMultipleImage(data={'image': image}, sizes=['120', '240', 'default'], upload_to='posts/')
serializer.is_valid()
serializer.validated_data
```

`.validated_data` here uploaded 3 image with 120px height, 240px height, and default (original) image sizes.   
`validated_data` returns deserialized of 'image', 'alt', 'size' fields:  
```python
[{'image': <Upload object 3d5cb1-120 - (.image .url .alt .size)>, 'alt': '3d5cb1-120', 'size': 120}, {'image': <Upload object 3d5cb1-240 - (.image .url .alt .size)>, 'alt': '3d5cb1-240', 'size': 240}, {'image': <Upload object 3d5cb1-default - (.image .url .alt .size)>, 'alt': '3d5cb1-default', 'size': 'default'}]```

&nbsp;  
**OneToMultipleImage** can use inside a serializer.   
**Example 2**:  
```python
class PostSerializer(serializers.Serializer):
    image = OneToMultipleImage(sizes=['120', '240', 'default'], upload_to='posts/')

data = {'image': {'image': "data:image/jpeg;base64,/9j/..."}}  # image in Base64 (str)
serializer = PostSerializer(data=data)
serializer.is_valid()
serializer.validated_data
```

&nbsp;   
### `OneToMultipleImage` in reading:   

**Example 1**:
```python
from onetomultipleimage.field import OneToMultipleImage
serializer = OneToMultipleImage(data={'image': image}, sizes=['120', '240', 'default'], upload_to='posts/')
serializer.is_valid()
serialized = OneToMultipleImage(serializer.validated_data).data
return Response(serialized)
```

serialized version looks like:
```python
[{'image': '/media/posts/1403/4/25/cd4851b839d0-120.JPEG', 'alt': '584fe1-120', 'size': 120}, 
 {'image': '/media/posts/1403/4/25/cd4851b839d0-240.JPEG', 'alt': '584fe1-240', 'size': 240}, 
 {'image': '/media/posts/1403/4/25/cd4851b839d0-default.JPEG', 'alt': '584fe1-default', 'size': 'default'}]
```

&nbsp;
**Example 2**:
```python
from onetomultipleimage.field import OneToMultipleImage
class PostSerializer(serializers.Serializer):
    image = OneToMultipleImage(sizes=['120', '240', 'default'], upload_to='posts/')

data = {'image': {'image': "data:image/jpeg;base64,/9j/..."}}  # image in Base64 (str)
serializer = PostSerializer(data=data)
serializer.is_valid()
serialized = PostSerializer(serializer.validated_data).data
return Response(serialized)
```

serialized version looks like:
```python
{'image': 
   [{'image': '/media/posts/1403/4/25/31557ad47c9d-120.JPEG', 'alt': 'e76815-120', 'size': 120}, 
    {'image': '/media/posts/1403/4/25/31557ad47c9d-240.JPEG', 'alt': 'e76815-240', 'size': 240}, 
    {'image': '/media/posts/1403/4/25/31557ad47c9d-default.JPEG', 'alt': 'e76815-default', 'size': 'default'}]
}
```


&nbsp;   
## onetomultipleimage model

if you need django model for one-to-multy process, you have to add `onetomultipleimage` to `INSTALLED_APPS`. after migrate, you have two table **__FatherImage__**, **__ImageSizes__**.

### FatherImage model
Store original image. attributes:

- **image**: django **ImageField**. `upload_to` path is: _'FatherImage/year/month/day'_ but can override directly before model initializing.
- **alt**: django **CharField**, represent image's alt, you can leave it blank to auto generating by uuid.uuid4
- **sizes**: custom **ListCharField**, represent lists of sizes you want to create them. (like: ['120', '240'])

&nbsp;  
### ImageSizes
Stores different sizes of original image. attributes:

- **image**: django **ImageField**. `upload_to` path is: _'ImageSizes/year/month/day'_ but can override directly before model initializing.
- **alt**: django **CharField**, represent image's alt, you can leave it blank to auto generating by uuid.uuid4
- **size**: django **CharField**, represent size of image (in str).
- **father**: django **ForeignKey**, reference to **FatherImage**. (FatherImage.imagesizes in reverse relation is accecible)


**Example 1**:  
```
image = FatherImage(image=request.FILES['image'], sizes=['120', '240', '480'])
image.save()
```
now fatherimage and 3 imagesizes with 120, 240, 480 PXs is created. fatherimage.alt and imagesizes.alt auto generated like: 'db949e-default', ''db949z-120', ...


**Example 2**:
```
image = FatherImage(image=request.FILES['image'], alt='sea_food', sizes=['120', '240', '480'])
image.save()
```
after .save, fatherimage and 3 imagesizes with 120, 240, 480 PXs is created. fatherimage.alt is like: 'sea_food-default'

```
image = FatherImage.objects.get(alt='sea_food-default')
image_sizes = image.imagesizes.all()
```
**image_sizes** contain 3 different size of original image. ```image_sizes[0].alt``` is like: 'sea_food-120',  ```image_sizes[1].alt```: 'sea_food-240', ...
