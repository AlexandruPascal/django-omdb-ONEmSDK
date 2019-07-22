#IMDB
Imdb-based service written in Django/Python using ONEmSDK.

### Quickstart

1. `git clone git@github.com:AlexandruPascal/django-omdb-ONEmSDK.git`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`
5. `ngrok http 8000`

Works with Python3.7. Preferably to work in a virtual environment, use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) to create a virtual environment.

### Usage

Register the app on the ONEm developer portal (https://developer-portal-poc.onem.zone/);
Set the callback URL to the forwarding address obtained from ngrok's output;
Go to https://poc.onem.zone/ and send the registered name with # in front

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
