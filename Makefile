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
	@PIPENV_DONT_LOAD_ENV=1 pipenv run black bothub
	@PIPENV_DONT_LOAD_ENV=1 pipenv run flake8
	@echo "${SUCCESS}✔${NC} The code is following the PEP8"

ifeq (test,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

test: development_mode_guard check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@PIPENV_DONT_LOAD_ENV=1 SECRET_KEY=SK SUPPORTED_LANGUAGES="en|pt" pipenv run coverage run manage.py test $(RUN_ARGS)
	@if [ ! $(RUN_ARGS) ]; then PIPENV_DONT_LOAD_ENV=1 pipenv run coverage report -m; fi;

migrate:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py migrate; \
		else pipenv run python manage.py migrate; fi

start:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@pipenv run python ./manage.py runserver
	
start_celery:
	@make development_mode_guard
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@make collectstatic CHECK_ENVIRONMENT=false
	@pipenv run celery -A bothub worker -l info -B

migrations:
	@make development_mode_guard
	@make check_environment
	@pipenv run python ./manage.py makemigrations
	@make migrate CHECK_ENVIRONMENT=false

collectstatic:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py collectstatic --no-input; \
		else pipenv run python manage.py collectstatic --no-input; fi
		
search_index:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python manage.py search_index --rebuild -f; \
		else pipenv run python manage.py search_index --rebuild -f; fi

createproto:
	@rm -rf ./bothub/protos/*.py
	@python -m grpc_tools.protoc --experimental_allow_proto3_optional --proto_path=./ --python_out=./ --grpc_python_out=./ ./bothub/protos/authentication.proto
	@python -m grpc_tools.protoc --experimental_allow_proto3_optional --proto_path=./ --python_out=./ --grpc_python_out=./ ./bothub/protos/organization.proto
	@python -m grpc_tools.protoc --experimental_allow_proto3_optional --proto_path=./ --python_out=./ --grpc_python_out=./ ./bothub/protos/repository.proto
	@python -m grpc_tools.protoc --experimental_allow_proto3_optional --proto_path=./ --python_out=./ --grpc_python_out=./ ./bothub/protos/project.proto


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
	@pipenv install --dev
	@echo "${SUCCESS}✔${NC} Development requirements installed"

install_production_requirements:
	@echo "${INFO}Installing production requirements...${NC}"
	@pipenv install --system
	@echo "${SUCCESS}✔${NC} Requirements installed"

development_mode_guard:
	@if [ ${IS_PRODUCTION} = true ]; then echo "${DANGER}Just run this command in development mode${NC}"; fi
	@if [ ${IS_PRODUCTION} = true ]; then exit 1; fi


# Checkers

_check_environment:
	@type pipenv || (echo "${DANGER}☓${NC} Install pipenv to continue..." && exit 1)
	@echo "${SUCCESS}✔${NC} pipenv installed"
	@if [ ! -f "${ENVIRONMENT_VARS_FILE}" ] && [ ${IS_PRODUCTION} = false ]; \
		then make create_environment_vars_file; \
	fi
	@make install_requirements
	@echo "${SUCCESS}✔${NC} Environment checked"
