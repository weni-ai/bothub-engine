ENV_DIR=./env/
SETTINGS_FILE=settings.ini

help:
	@cat Makefile-help.txt

init_envoriment:
	virtualenv -p python3.6 $(ENV_DIR);
	$(ENV_DIR)bin/pip install --upgrade pip
	make install_requirements

check_envoriment:
	if [ ! -d "$(ENV_DIR)" ]; then make init_envoriment; fi

install_requirements:
	make check_envoriment
	$(ENV_DIR)bin/pip install -r requirements.txt

update_requirements:
	make check_envoriment
	$(ENV_DIR)bin/pip freeze > requirements.txt

lint:
	make check_envoriment
	$(ENV_DIR)bin/flake8

create_development_settings:
	echo "[settings]" > $(SETTINGS_FILE)
	echo "SECRET_KEY=SK" >> $(SETTINGS_FILE)
	echo "DEBUG=True" >> $(SETTINGS_FILE)

check_ready_for_development:
	make check_envoriment
	if [ ! -f "$(SETTINGS_FILE)" ]; then make create_development_settings; fi

test:
	make check_ready_for_development
	./env/bin/coverage run manage.py test && ./env/bin/coverage report -m

runserver:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/python ./manage.py runserver

migrate:
	make check_ready_for_development
	$(ENV_DIR)bin/python ./manage.py migrate

makemigrations:
	make check_ready_for_development
	$(ENV_DIR)bin/python ./manage.py makemigrations

shell:
	make check_ready_for_development
	$(ENV_DIR)bin/python ./manage.py shell

fill_db_using_fake_data:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/python ./manage.py fill_db_using_fake_data