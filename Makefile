.PHONY: run migrate migrations test lint lint-fix install install-dev setup shell db superuser

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

setup:
	pip install -r requirements-dev.txt
	cp .env.example .env
	py manage.py migrate

run:
	py manage.py runserver

migrations:
	py manage.py makemigrations

migrate:
	py manage.py migrate

test:
	pytest

test-coverage:
	pytest --cov=workspace --cov-report=html

lint:
	ruff check .

lint-fix:
	ruff check . --fix

superuser:
	py manage.py createsuperuser

shell:
	py manage.py shell

db:
	py manage.py dbshell