.PHONY: test1

name=systemcmd-python3

test1:
	docker stop $(name) || true
	docker rm $(name) || true
	docker run -it -v "$(shell realpath $(PWD)):/project" -w /project --name $(name) python:3 /bin/bash
