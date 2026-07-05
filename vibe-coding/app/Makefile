SHELL := /bin/bash

# Find NVM script path
NVM_SH := $(shell [ -s "$$NVM_DIR/nvm.sh" ] && echo "$$NVM_DIR/nvm.sh" || echo "$$HOME/.nvm/nvm.sh")

lint:
	npm run lint

format:
	npm run format

dev-app:
	. $(NVM_SH) && nvm use 20 && npm run dev

dev-server:
	. $(NVM_SH) && nvm use 20 && npm run server

build:
	. $(NVM_SH) && nvm use 20 && npm run build
