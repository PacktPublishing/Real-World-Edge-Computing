#!/bin/sh

socat TCP4-LISTEN:7772,fork EXEC:./mms_service_model.sh


