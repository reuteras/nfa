install: environment install-packages static tmp

all: run

apt-install:
	sudo apt install -y python3-venv curl

environment:
	python3 -m venv .venv

install-packages:
	. .venv/bin/activate && python3 -m pip install -U pip
	. .venv/bin/activate && python3 -m pip install -U -r requirements.txt

static:
	mkdir -p static
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js

tmp:
	mkdir -p tmp

run:
	. .venv/bin/activate && uvicorn main:app --port 5001 --host 0.0.0.0

development:
	. .venv/bin/activate && uvicorn main:app --port 5001 --reload

pylint:
	. .venv/bin/activate && pylint main.py

clean:
	rm -rf tmp __pycache__/

distclean: clean
	rm -rf .venv static
