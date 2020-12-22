package=system_cmd

include pypackage.mk



bump:
	bumpversion patch
	git push --tags
	git push --all

upload:
	rm -f dist/*
	rm -rf src/*.egg-info
	python3 setup.py sdist
	devpi use $(TWINE_REPOSITORY_URL)
	devpi login $(TWINE_USERNAME) --password $(TWINE_PASSWORD)
	devpi upload --verbose dist/*

vulture:


name=systemcmd-python3

test1:
	docker stop $(name) || true
	docker rm $(name) || true

	docker run -it -v "$(shell realpath $(PWD)):/project" -w /project --name $(name) python:3 /bin/bash

test1-install:
	pip install -r requirements.txt
	pip install nose
	python setup.py develop --no-deps
