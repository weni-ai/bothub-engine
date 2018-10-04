from setuptools import setup, find_packages


setup(
    name='bothub-engine',
    version='1.16.0',
    description='Bothub Engine',
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
