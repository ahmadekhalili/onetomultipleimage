# onetomultipleimage

onetomultipleimage is a django package to convert one image to specified sizes. it can be used in REST or django model.

## installation

1- run: ``` pip install onetomultipleimage[jalali]```  

To install onetomultipleimage with Jalali date support, add ```[jalali]``` part.  
`IMAGES_PATH_TYPE='jalali'` in settings.py, now jalali date path used (instead default gregorian) like:  
__/media/FatherImage/1401/12/13/small.jpg__ instead of: __/media/FatherImage/2023/3/4/small.jpg__

2- to install **onetomultipleimage** models, add 'onetomultipleimage' to `INSTALLED_APPS` of project's settings.py
after makemigrations and migrate, models will be created.


&nbsp;

&nbsp;
## Serializer Field: OneToMultipleImage

Receives image in Base64/form-data with list of sizes and generate images with specified sizes.

`OneToMultipleImage` arguments:

- **sizes**:
list of sizes in str. for generate original image use 'default'. required in writing.

- **upload_to**:
path in str for uploads image. required in writing.


**example 1**:
```
from onetomultipleimage.field import OneToMultipleImage
serializer = OneToMultipleImage(sizes=['120', '240', 'default'], data=data['image'])
serializer.is_valid()
s.validated_data
```

`.validated_data` here returns 3 object with 120px height, 240px height, and default (original) image sizes. `validated_data` returns like:  
{'image': [<Upload object 1e2813-120 - (.image .url .alt .size)>, <Upload object 1e2813-240 - (.image .url .alt .size)>, <Upload object 1e2813-default - (.image .url .alt .size)>]}

&nbsp;  
**OneToMultipleImage** can use inside a serializer.  
**example 2**:  
```
class PostSerializer(serializers.Serializer):
    image = OneToMultipleImage(sizes=['120', '240', 'default'])

data = {'image': {'image': "data:image/jpeg;base64,/9j/..."}}
serializer = PostSerializer(data=data)
serializer.is_valid()
s.validated_data
```
same result...

&nbsp;  
&nbsp;  
## onetomultipleimage models

if you need django model for one-to-multy process, you have to add `onetomultipleimage` to `INSTALLED_APPS`. after migrate, you have two table **__FatherImage__**, **__ImageSizes__**.

### FatherImage model
Store original image. attributes:

- image: django image field. upload_to path is: 'FatherImage/year/month/day' but can override directly to any value before model initializing.
- alt: image's alt. you can leave it blank to auto generating by uuid.uuid4
- sizes: lists for specify which sizes you want to create. (list of str elements)

&nbsp;  
### ImageSizes
Stores different sizes of original image. attributes:

- image: django image field. `upload_to` path is: __'ImageSizes/year/month/day'__ but can override directly to any value before model initializing.
- alt: image's alt. take fatherimage.alt or auto generating by uuid.uuid4 + size like: 'db949z-120'
- size: size of image (in str)
- father: django ForeignKey, reference to FatherImage. (FatherImage.imagesizes in reverse relation is accecible)


**example 1**:  
```
image = FatherImage(image=request.FILES['image'], sizes=['120', '240', '480'])
image.save()
```
here is created fatherimage and 3 imagesize with 120, 240, 480 pxs. fatherimage.alt and imagesizes.alt auto generated like: 'db949e-default', ''db949z-120'


**example 2**:
image = FatherImage(image=request.FILES['image'], alt='sea_food', sizes=['120', '240', '480'])
image.save()

after .save, fatherimage and 3 imagesize with 120, 240, 480 pxs is created. fatherimage.alt is like: 'sea_food-default'

```
image = FatherImage.objects.get(alt='sea_food-default')
image_sizes = image.imagesizes.all()
```
**image_sizes** contain 3 different size of original image. ```image_sizes[0].alt``` is like: 'sea_food-120',  ```image_sizes[0].alt```: 'sea_food-240', ...
