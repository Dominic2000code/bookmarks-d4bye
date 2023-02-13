# Bookmarks

An image bookmarking site

## Getting Started

python version 3.11.0

```bash
git clone https://github.com/Dominic2000code/bookmarks-d4bye.git

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

- use this command to simulate https

```bash
python manage.py runserver_plus --cert-file cert.crt
```

The site will be available at <http://127.0.0.1:8000/>
