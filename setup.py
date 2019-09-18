from setuptools import setup, find_packages


setup(
    name='bothub-engine',
    version='1.19.3',
    description='Bothub Engine',
    packages=find_packages(),
    install_requires=[
        'django==2.1.3',
        'django-environ==0.4.5',
        'djangorestframework==3.9.0',
        'django-filter==2.0.0',
        'django-cors-headers==2.4.0',
        'requests==2.20.1',
        'coreapi==2.3.3',
        'whitenoise==4.1.2',
        'pytz==2018.7',
    ],
    python_requires='>=3.4',
)
