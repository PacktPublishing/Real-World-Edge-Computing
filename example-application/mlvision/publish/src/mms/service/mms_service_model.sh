#!/bin/bash

. mms_inc.sh

MMS_ACTION=""
fn_parse_mms_request MMS_ACTION

# Initialize ESS query params and vars
fn_initialize_creds

#Set object type 
OBJECT_TYPE=$MMS_ACTION

#OBJECT_TYPE="mmsmodel"
#ACTION="unchanged"

OBJECT_VALUES=""
OBJECT_META_FILE=objects.meta.$OBJECT_TYPE
HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_META_FILE ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE) 
MESSAGE="OK"

if [ "$HTTP_CODE" == '200' ]; then 
    for OBJECT_ID in $(jq -r .[].objectID $OBJECT_META_FILE);
    do
	OBJECT=$(jq -r ".[] | select(.objectID == \"$OBJECT_ID\")" $OBJECT_META_FILE)
	DELETED=$(echo $OBJECT | jq -r  '.deleted')
	if [ "$DELETED" == "true" ]; then
	    # Handle the case in which MMS is telling us the model file was deleted
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
		MESSAGE="Error:-Object reading"
	    fi

            # Acknowledge that we got the new file, so it won't keep telling us
            HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/received)
            if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then
		MESSAGE="Error:-Object-update-received"
	    fi

	    DESC_META=$(echo "$OBJECT" | jq -r ".description")
	    MODEL_FMWK=$(echo "$DESC_META" | jq -r ".fmwk")
	    MODEL_NET=$(echo "$DESC_META" | jq -r ".net")
	    MODEL_DATASET=$(echo "$DESC_META" | jq -r ".dataset")
	    MODEL_VERSION=$(echo "$DESC_META" | jq -r ".version")
	    MODEL_FORMAT=$(echo "$DESC_META" | jq -r ".format")
	    MODEL_SUB_DIR=$(echo "$DESC_META" | jq -r ".subdir")
	    MODEL_DIR=$APP_BIND_HORIZON_DIR/$MODEL_SUB_DIR
	    if [ -z $OBJECT_VALUES ]; then OBJECT_VALUES="["; else OBJECT_VALUES=${OBJECT_VALUES}","; fi
	    cp $OBJECT_ID "$MODEL_DIR/mmsmodel-$OBJECT_ID"
	    OBJECT_VALUES=${OBJECT_VALUES}"{\"OBJECT_TYPE\":\""$OBJECT_TYPE"\",\"OBJECT_ID\":\""$OBJECT_ID"\",\"MODEL_NET\":\""$MODEL_NET"\",\"MODEL_FMWK\":\""$MODEL_FMWK"\",\"MODEL_VERSION\":\""$MODEL_VERSION"\",\"MODEL_DIR\":\""$MODEL_DIR"\"}"
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

