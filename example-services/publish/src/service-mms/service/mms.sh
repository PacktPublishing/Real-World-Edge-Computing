#!/bin/sh

socat TCP4-LISTEN:7777,fork EXEC:./service_mms.sh
