install:
	python -m pip install -e .[dev]

test:
	pytest -q

run:
	uvicorn docintel.main:app --reload

check:
	python -m compileall -q src tests
	pytest -q
