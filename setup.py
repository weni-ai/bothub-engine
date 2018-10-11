from setuptools import setup, find_packages


setup(
    name='bothub-engine',
    version='1.16.1',
    description='Bothub Engine',
    packages=find_packages(),
    install_requires=[
        'python-decouple==3.1',
        'requests==2.19.1',
        'django==2.1.2',
        'djangorestframework==3.7.7',
        'whitenoise==4.1',
        'dj-database-url==0.5.0',
        'django-cors-headers==2.4.0',
        'django-filter==2.0.0',
        'coreapi==2.3.3',
    ],
    python_requires='>=3.6',
)
