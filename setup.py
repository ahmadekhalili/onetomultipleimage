from setuptools import setup, find_packages

setup(
    name='onetomultipleimage',
    version='1.0.8',
    packages=['onetomultipleimage'],
    install_requires=["django", "djangorestframework", "pillow"],
    extras_require={
        'jalali': ['jdatetime']
    },
    author='Ahmad Khalili',
    author_email='ahmadkhalili2020@gmail.com',
    description='convert one image to several sizes in django REST and django models',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ahmadekhalili/onetomultipleimage',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
