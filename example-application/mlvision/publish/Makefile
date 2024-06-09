#
# Makefile: mlvision : A tensorflow lite and OpenCV based machine inferencing in a videostream for object classification
#

# Checks required environment variables
-include env.check.mk

export ARCH ?= $(shell hzn architecture)

all: publish-http publish-mms publish-infer deploy-policy

publish-http:
	make -C src/http build
	make -C src/http push
	make -C src/http publish-service

publish-mms:
	make -C src/mms build
	make -C src/mms push
	make -C src/mms publish-service

publish-infer:
	make -C src/infer build
	make -C src/infer push
	make -C src/infer publish-service

deploy-policy:
	make -C src/mms deploy-policy
	make -C src/infer deploy-policy

