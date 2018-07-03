ENVIRONMENT_VARS_FILE := .env
IS_PRODUCTION ?= false
CHECK_ENVIRONMENT := true


# Commands

help:
	@cat Makefile-help.txt
	@exit 0

check_environment:
	@if [[ ${CHECK_ENVIRONMENT} = true ]]; then make _check_environment; fi

install_requirements:
	@if [[ ${IS_PRODUCTION} = true ]]; \
		then make install_production_requirements; \
		else make install_development_requirements; fi

lint:
	@make development_mode_guard
	@make check_environment
	@pipenv run flake8
	@echo "${SUCCESS}✔${NC} The code is following the PEP8"

test:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@SUPPORTED_LANGUAGES="en pt" pipenv run python manage.py test && pipenv run coverage report -m

migrate:
	@make check_environment
	@if [[ ${IS_PRODUCTION} = true ]]; \
		then python manage.py migrate; \
		else pipenv run python manage.py migrate; fi

start:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@pipenv run python ./manage.py runserver

migrations:
	@make development_mode_guard
	@make check_environment
	@pipenv run python ./manage.py makemigrations
	@make migrate CHECK_ENVIRONMENT=false

collectstatic:
	@make check_environment
	@if [[ ${IS_PRODUCTION} = true ]]; \
		then python manage.py collectstatic --no-input; \
		else pipenv run python manage.py collectstatic --no-input; fi


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
	@echo "SUPPORTED_LANGUAGES=en de es pt fr it nl" >> "${ENVIRONMENT_VARS_FILE}"
	@echo "${SUCCESS}✔${NC} Settings file created"

install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@pipenv install --dev &> /dev/null
	@echo "${SUCCESS}✔${NC} Development requirements installed"

install_production_requirements:
	@echo "${INFO}Installing production requirements...${NC}"
	@pipenv install --system
	@echo "${SUCCESS}✔${NC} Requirements installed"

development_mode_guard:
	@if [[ ${IS_PRODUCTION} = true ]]; then echo "${DANGER}Just run this command in development mode${NC}"; fi
	@if [[ ${IS_PRODUCTION} = true ]]; then exit 1; fi


# Checkers

_check_environment:
	@type pipenv &> /dev/null || (echo "${DANGER}☓${NC} Install pipenv to continue..." && exit 1)
	@echo "${SUCCESS}✔${NC} pipenv installed"
	@if [[ ! -f "${ENVIRONMENT_VARS_FILE}" && ${IS_PRODUCTION} = false ]]; then make create_environment_vars_file; fi
	@make install_requirements
	@echo "${SUCCESS}✔${NC} Environment checked"