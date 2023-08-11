# miniwallet

## installation
- clone repo first
- cd to repo folder
- virtualenv .venv
- source .venv/bin/activate
- pip install -r requirement.txt
- python manage.py runserver

## db migrate
- python manage.py api makemigrations
- python manage.py api migrate

## run apps
- python manage.py runserver


## API's
- http://127.0.0.1:8000/api/v1/init
- http://127.0.0.1:8000/api/v1/wallet
- http://127.0.0.1:8000/api/v1/wallet/deposits
- http://127.0.0.1:8000/api/v1/wallet/withdrawals
- http://127.0.0.1:8000/api/v1/wallet/transactions
