# django rest framework getstream Notification

Example of using django rest framework with getstream.io. Based off of the drf
snippet tutorial. We add a notifications stream for users when a snippet is
published by them (This notification stream is contrived but illustrates how
to use drf and getstream together).

## Running
* `virtualenv env`
* `source env/bin/activate`
* `pip install -r requirements.txt`
* `python manage.py migrate`
* `export STREAM_API_KEY=my_api_key`
* `export STREAM_API_SECRET=my_api_secret_key`
* `python manage.py createsuperuser`
* `python manage.py runserver`

## Usage

open localhost:8000/notifications/ to see the currently logged in user's notifcations

## TODO

* make GET /notificaitons/ return an array of notifications for recently created Snippets.
