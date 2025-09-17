# Planetarium API

#### API service for planetarium management written on Django REST Framework (DRF)

## Installing using GitHub:


* git clone the-link-from-your-forked-repo
* python -m venv venv
* venv\Scripts\activate (on Windows)
* source venv/bin/activate (on macOS)
* pip install -r requirements.txt
* set POSTGRES_HOST=<your db hostname>
* set POSTGRES_PASSWORD=<your db password>
* set POSTGRES_USER=<your username>
* set POSTGRES_PORT=<your db port>
* set POSTGRES_DB=<your db name>
* python manage.py migrate
* python manage.py runserver

## Run with Docker

#### Docker should be installed:

* docker-compose build
* docker-compose up

## Getting access

* Create user via /api/user/register/
* Get access token via /api/user/token/

## Features

* JWT authentication (via djangorestframework_simplejwt)
* Admin panel /admin/
* OpenAPI / Swagger documentation /api/doc/swagger/
* Managing reservations and tickets
* Creating astronomy shows with themes
* Creating planetarium domes (halls)
* Adding show sessions
* Uploading images for shows: /api/planetarium/shows/<id>/upload-image/
* Filtering shows by title or theme
* Filtering show sessions by date, dome, or show
* Custom mixins for permissions (BaseViewSetMethodMixin)
* (Allows read-only access for authenticated users and full access for admins)