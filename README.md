# Bothub

[![Build Status](https://travis-ci.org/push-flow/bothub.svg?branch=master)](https://travis-ci.org/push-flow/bothub) [![Coverage Status](https://coveralls.io/repos/github/push-flow/bothub/badge.svg?branch=master)](https://coveralls.io/github/push-flow/bothub?branch=master) [![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/) [![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/push-flow/bothub/blob/master/LICENSE)

## Development

Use make commands in development envoriment.

Run ```make help``` to show all available make commands.

### Fill database using fake data

Run ```make fill_db_using_fake_data``` to fill database using fake data. This can help you to test [Bothub Webapp](https://github.com/push-flow/bothub-webapp).

#### Fake users infos:

| nickname | email | password | is superuser |
|---|---|---|---|
| admin | admin@bothub.it | admin | yes |
| douglas | douglas@bothub.it | douglas | no |
| user | user@bothub.it | user | no |

## Production

Docker images available in [Bothub's Docker Hub repository](https://hub.docker.com/r/ilha/bothub/).
