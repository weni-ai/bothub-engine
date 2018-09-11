from setuptools import setup, find_packages


setup(
    name='bothub',
    version='1.15.2',
    description='bothub',
    packages=find_packages(),
    install_requires=[
        'python-decouple',
        'requests',
        'django==2.0.6',
        'djangorestframework==3.7.7',
        'whitenoise',
        'dj-database-url',
        'django-cors-headers',
        'django-filter',
        'coreapi',
    ],
    python_requires='>=3.6',
)
