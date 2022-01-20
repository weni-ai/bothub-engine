<p align="center">
  <img src="https://i.imgur.com/PKrSNGY.png" alt="BLACK LIVES MATTER" />

  <h3 align="center">BLACK LIVES MATTER</h3>

  <p align="center">
    <a href="https://blacklivesmatter.com/" target="_blank">Black Lives Matter</a>
    ·
    <a href="https://act.unicefusa.org/blm" target="_blank">Supporting the cause</a>
    ·
  </p>
</p>
    
<br />
<p align="center">
    <img src="https://user-images.githubusercontent.com/5360835/65427083-1af35900-de01-11e9-86ef-59f1eee79a68.png" width="230" height="70" alt="Bothub" />
</p>


# Bothub

[![Build Status](https://travis-ci.com/Ilhasoft/bothub-engine.svg?branch=master)](https://travis-ci.com/Ilhasoft/bothub-engine)
[![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-engine/badge.svg?branch=master)](https://coveralls.io/github/bothub-it/bothub-engine?branch=master)
[![Code Climate](https://codeclimate.com/github/bothub-it/bothub-engine/badges/gpa.svg)](https://codeclimate.com/github/bothub-it/bothub-engine)
[![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/bothub-it/bothub-engine/blob/master/LICENSE)



# Setting up for development

* Download the project code

        $ git clone https://github.com/Ilhasoft/bothub-engine.git

* Prepare the virtual environment and install dependencies:

        $ make install_requirements
        $ make check_environment

* Start the containers for the other dependencies(Postgresql, Elasticsearch and Redis):

        $ docker-compose up -d database es bothub-engine-celery-redis

* Create the .env file following the [Enviroment Variables section](https://github.com/Ilhasoft/bothub-engine#environment-variables)

* Run the migrations and create and populate the indices at elasticsearch

        $ make migrate
        $ make search_index

* Collect the static files into ```STATIC_ROOT```

        $ make collectstatic

* Run tests

        $ make test

* run django in a separated terminal

        $ make start

* run celery in a separated terminal

        $ make start_celery

* run lint after making updates in the code

        $ make lint

* (optional) Add initial data into the database
        
        $ pipenv run python ./manage.py fill_db_using_fake_data

* If you did not follow the previous step, create a superuser to access the django admin interface

        $ pipenv run python ./manage.py createsuperuser

The API will be running at ```http://localhost:8000``` and the admin interface can be accessed at ```http://localhost:8000/admin```


