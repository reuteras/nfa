install: environment install-packages static tmp

all: run

apt-install:
	sudo apt install -y python3.8-venv curl

environment:
	python3.8 -m venv nfa

install-packages:
	. nfa/bin/activate && python3 -m pip install -U pip
	. nfa/bin/activate && python3 -m pip install -U -r requirements.txt
	sed -e 's/^mp.set_start_method("fork")/# mp.set_start_method("fork")/' -i nfa/lib64/python3*/site-packages/nfstream/streamer.py

static:
	mkdir -p static
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css
	cd static && curl -O -s https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js

tmp:
	mkdir -p tmp

run:
	. nfa/bin/activate && uvicorn main:app --port 5001 --host 0.0.0.0

development:
	. nfa/bin/activate && uvicorn main:app --port 5001 --reload

pylint:
	. nfa/bin/activate && pylint main.py

clean:
	rm -rf tmp __pycache__/

distclean: clean
	rm -rf nfa static
