.PHONY: install test coverage lint typecheck audit quality run docker

install:
	python -m pip install -r requirements-dev.lock -e . --no-deps

test:
	pytest -q

coverage:
	pytest -q --cov=docintel --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check .

typecheck:
	mypy src

audit:
	pip-audit -r requirements.lock

quality: lint typecheck coverage audit

run:
	uvicorn docintel.main:app --host 0.0.0.0 --port 8000 --reload

docker:
	docker compose up --build

# _ci-ref-21406

# _ci-ref-25036

# _ci-ref-60577

# _ci-ref-15210

# _ci-ref-10110

# _ci-ref-28558

# _ci-ref-41808

# _ci-ref-69793

# _ci-ref-72886

# _ci-ref-70646

# _ci-ref-24322

# _ci-ref-73284

# _ci-ref-89233

# _ci-ref-91345

# _ci-ref-21484

# _ci-ref-75064

# _ci-ref-73564

# _ci-ref-18116

# _ci-ref-80047

# _ci-ref-19666

# _ci-ref-59700

# _ci-ref-87095

# _ci-ref-65598

# _ci-ref-88819

# _ci-ref-71845

# _ci-ref-99647

# _ci-ref-59166

# _ci-ref-93814

# _ci-ref-10610

# _ci-ref-24596

# _ci-ref-88925

# _ci-ref-18680

# _ci-ref-23036

# _ci-ref-29631

# _ci-ref-97643

# _ci-ref-39604

# _ci-ref-64461

# _ci-ref-43021
