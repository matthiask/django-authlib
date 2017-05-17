#!/bin/sh
venv/bin/coverage run --branch --include="*authlib/*" --omit="*tests*" ./manage.py test -v 2 testapp
venv/bin/coverage html
