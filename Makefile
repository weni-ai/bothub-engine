ENVIRONMENT_VARS_FILE := .env
IS_PRODUCTION ?= false
CHECK_ENVIRONMENT := true


# Commands

help:
	@cat Makefile-help.txt
	@exit 0

check_environment:
	@if [ ${CHECK_ENVIRONMENT} = true ]; then make _check_environment; fi

install_requirements:
	@if [ ${IS_PRODUCTION} = true ]; \
		then make install_production_requirements; \
		else make install_development_requirements; fi

lint:
	@make development_mode_guard
	@poetry run black .
	@poetry run flake8 .
	@echo "${SUCCESS}✔${NC} The code is following the PEP8"

ifeq (test,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

test: development_mode_guard check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@SECRET_KEY=SK SUPPORTED_LANGUAGES="en|pt" poetry run coverage run manage.py test $(RUN_ARGS)
	@if [ ! $(RUN_ARGS) ]; then poetry run coverage report -m; fi;

migrate:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py migrate; \
		else poetry run python manage.py migrate; fi

start:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@poetry run python ./manage.py runserver
	
start_celery:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@poetry run celery -A bothub worker -l info -B

migrations:
	@make development_mode_guard
	@make check_environment
	@poetry run python ./manage.py makemigrations
	@make migrate CHECK_ENVIRONMENT=false

collectstatic:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py collectstatic --no-input; \
		else poetry run python manage.py collectstatic --no-input; fi
		
search_index:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py search_index --rebuild -f; \
		else poetry run python manage.py search_index --rebuild -f; fi

# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m

create_environment_vars_file:
	@echo "SECRET_KEY=SK" > "${ENVIRONMENT_VARS_FILE}"
	@echo "DEBUG=true" >> "${ENVIRONMENT_VARS_FILE}"
	@echo "SUPPORTED_LANGUAGES=en|pt" >> "${ENVIRONMENT_VARS_FILE}"
	@echo "${SUCCESS}✔${NC} Settings file created"

install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@poetry install
	@echo "${SUCCESS}✔${NC} Development requirements installed"

install_production_requirements:
	@echo "${INFO}Installing production requirements...${NC}"
	@POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev
	@echo "${SUCCESS}✔${NC} Requirements installed"

development_mode_guard:
	@if [ ${IS_PRODUCTION} = true ]; then echo "${DANGER}Just run this command in development mode${NC}"; fi
	@if [ ${IS_PRODUCTION} = true ]; then exit 1; fi


# Checkers

_check_environment:
	@type poetry || (echo "${DANGER}☓${NC} Install poetry to continue..." && exit 1)
	@echo "${SUCCESS}✔${NC} poetry installed"
	@if [ ! -f "${ENVIRONMENT_VARS_FILE}" ] && [ ${IS_PRODUCTION} = false ]; \
		then make create_environment_vars_file; \
	fi
	@make install_requirements
	@echo "${SUCCESS}✔${NC} Environment checked"
