#!/bin/bash
# service-mms
#

fn_parse_mms_request() {
    read request
    while /bin/true; do
	read header
	[ "$header" == $'\r' ] && break;
    done
    url="${request#GET /}"
    eval "$1='${url% HTTP/*}'"
}

fn_output() {
    BODY="{\"query_http_code\":\"$1\",\"message\":\"$2\",\"mms_action\":\"$3\",\"value\":$4}" 
    HEADERS="Content-Type: text/json; charset=ISO-8859-1"
    HTTP="HTTP/1.1 200 OK\r\n${HEADERS}\r\n\r\n${BODY}\r\n"
    echo -en $HTTP
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

MMS_ACTION=""
fn_parse_mms_request MMS_ACTION

# Initialize ESS query params and vars
fn_initialize_creds

OBJECT_TYPE=$MMS_ACTION
OBJECT_VALUES=""
OBJECT_META_FILE=objects.meta.$OBJECT_TYPE
HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_META_FILE ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE) 
MESSAGE="OK"

#testmms
ACTION="$MMS_ACTION"

if [ "$HTTP_CODE" == '200' ]; then 
    OBJS=("test_mms.json")

    for OBJECT_ID in $OBJS
    do
	OBJECT=$(jq -r ".[] | select(.objectID == \"$OBJECT_ID\")" $OBJECT_META_FILE)
	DELETED=$(echo $OBJECT | jq -r  '.deleted')
	if [ "$DELETED" == "true" ]; then
	    # Handle the case in which MMS is telling us the config file was deleted
            HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/deleted)
            if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then
		MESSAGE="Error:-Object-deletion"
	    fi
	    ACTION="deleted"
	else
	    ACTION="updated"
            # Read the new file from ESS
            HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_ID ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/data)
            if [[ "$HTTP_CODE" != '200' ]]; then
		MESSAGE="Error:-Object-reading"
	    fi

            # Acknowledge that we got the new file, so it won't keep telling us
            HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/received)
            if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then
		MESSAGE="Error:-Object-update-received"
	    fi

	    OBJECT_VALUES="["`cat $OBJECT_ID | jq -c`
	fi
    done
elif [ "$HTTP_CODE" == '404' ]; then 
    MESSAGE="$OBJECT_TYPE-not-found.Publish-at-least-one-object."
else
    MESSAGE="Unknown"
fi

if [ -z $OBJECT_VALUES ]; then OBJECT_VALUES="["; fi
OBJECT_VALUES=${OBJECT_VALUES}"]"

fn_output $HTTP_CODE $MESSAGE $ACTION $OBJECT_VALUES

