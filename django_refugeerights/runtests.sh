#!/bin/sh

export DJANGO_SETTINGS_MODULE="django_refugeerights.testsettings"
cd django_refugeerights
./manage.py test "$@"
