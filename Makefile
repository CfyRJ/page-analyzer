install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

package-uninstall-hc:
	pip uninstall hexlet-code
	rm -r dist

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

start_debug:
	poetry run flask --app page_analyzer.app --debug run --port 8000

lint:
	poetry run flake8 page_analyzer

pytest:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml