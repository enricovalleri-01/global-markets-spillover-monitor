# Rebuild everything from the raw files in data/raw:
#
#   make setup   create the virtual environment and install the packages
#   make         build the database, run the estimates, draw the figure, run the tests
#   make clean   delete the database (it is rebuilt by the next "make")
#
# "make download" fetches the raw files again from the sources. It is not part
# of "make" on purpose: new data would change the results, so I run it only
# when I want to update the sample.

PYTHON = .venv/bin/python

.PHONY: all setup download database estimates figure test clean

all: figure test

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt

download:
	$(PYTHON) -m src.ingest.download

database:
	$(PYTHON) -m src.transform.build_database

estimates: database
	$(PYTHON) -m src.models.local_projections

figure: estimates
	$(PYTHON) -m src.models.plot_baseline
	$(PYTHON) -m src.models.plot_robustness

test: database
	$(PYTHON) -m pytest -q

clean:
	rm -rf data/processed
