#!/bin/bash

fn_parse_mms_request() {
    read request
    while /bin/true; do
	read header
	[ "$header" == $'\r' ] && break;
    done
    url="${request#GET /}"
    eval "$1='${url% HTTP/*}'"
}

fn_initialize_creds() {
    USER=$(cat ${HZN_ESS_AUTH} | jq -r ".id")
    PW=$(cat ${HZN_ESS_AUTH} | jq -r ".token")
    AUTH="-u ${USER}:${PW}"
    CERT="--cacert ${HZN_ESS_CERT}"
    SOCKET="--unix-socket ${HZN_ESS_API_ADDRESS}"
    BASEURL='https://localhost/api/v1/objects'
    ACTION="unchanged"
}

#HTTP_CODE $1 MESSAGE $2 ACTION $3 OBJECT_VALUES $4
fn_output() {
    BODY="{\"query_http_code\":\"$1\",\"message\":\"$2\",\"mms_action\":\"$3\",\"value\":$4}" 
    HEADERS="Content-Type: text/json; charset=ISO-8859-1"
    HTTP="HTTP/1.1 200 OK\r\n${HEADERS}\r\n\r\n${BODY}\r\n"
    echo -en $HTTP
}
