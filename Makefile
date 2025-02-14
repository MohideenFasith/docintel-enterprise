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
