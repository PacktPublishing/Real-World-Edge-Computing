# Example Application
Steps to buld, push, publish and deploy service on an Edge device node for MLVISION example application
## MLVISION
1. Setup ENVIRONMENT variables
2. Build and publish ML Vision application
3. Setup TFLite ML model
4. Register the edge device node
5. Verify containers
6. View outout in browser
7. Publish mms model
### 1. Setup ENVIRONMENT variables
#### 1.1 Create ENVIRONMENT variables file
Create a file `~/project/rwec/ENV_RWEC_MLVISION` with the following content. Replace the content within <> with values applicable as per your environment. Following setup assumes that you are using Docker Hub. If you are using any other container image registry then use the values accordingly,
```
# Arbitrary text to organize the Open Horizon (OH) resources such as
# image, service, pattern names etc.
# You may choose to change these as you need. 
export EDGE_OWNER=rwec.edge
export EDGE_DEPLOY=example.mlvision

# Container registry (CR) values
export DOCKER_BASE=<docker-id>
export CR_HOST=docker.io
export CR_USERNAME=<your-docker-namespace>
export CR_DOCKER_APIKEY=<your-docker-api-key>

# OH org and user credential 
export HZN_ORG_ID=myorg
export HZN_EXCHANGE_USER_AUTH=<user:api-key>

# Example MLVISION tflite specific
export APP_BIND_HORIZON_DIR=/var/local/horizon
export APP_MODEL_FMWK=tflite
export APP_MODEL_DIR=$APP_BIND_HORIZON_DIR/ml/model/tflite
export APP_MI_MODEL=tflite-model-1.0.0-mms.zip
export APP_CAMERAS=all
export APP_VIDEO_FILES=/var/local/horizon/sample/video/sample-video.mp4
export APP_RTSPS="-"
export APP_VIEW_COLUMNS=2
export DEVICE_ID=<edge-node-device-id>
export DEVICE_NAME=<edge-node-device-name>
export DEVICE_IP_ADDRESS=<edge-node-ip-address>
export SHOW_OVERLAY=true
export PUBLISH_STREAM=true
export MIN_CONFIDENCE_THRESHOLD=0.6
```
#### 1.2 Source ENVIRONMENT variables
```
source ~/project/rwec/ENV_RWEC_MLVISION 
```
### 2. Build and publish ML Vision application
#### 2.1 Change to `mlvision/publish` directory
```
cd mlvision/publish
```
#### 2.2 Build abd publish
```
make
```
### 3. Setup TFLite ML model
#### 3.1 Locate the ML models 
This `.zip` files are based on original TensorFlow Lite model. Renamed for convenience.
```
cd ../register
tflite-model-1.0.0-mms.zip
tflite-model-1.0.1-mms.zip
```
### 3.2 Setup initial model directory
Create a 777 directory at /var/local/horizon
```
mkdir -p /var/local/horizon/ml/model/tflite/
sudo chmod 777 /var/local/horizon
```
Copy initial model at `/var/local/horizon/ml/model/tflite` 
```
cp tflite-model-1.0.0-mms.zip /var/local/horizon/ml/model/tflite/.
```
### 4. Register the edge device node
```
envsubst < user_input.json | hzn register --policy=node_policy.json -f-
```
### 5. Verify containers
Vefify that `http`, `infer` and `mms` containers are running
```
docker ps
```
### 6. View output in browser
```
http:<ip-addres-of-node>:5000
```
### 7. Publish mms model
```
envsubst < tflite-model-101-publish-definition.json | hzn mms object publish -v -m- -f tflite-model-1.0.1-mms.zip
envsubst < tflite-model-100-publish-definition.json | hzn mms object publish -v -m- -f tflite-model-1.0.0-mms.zip
```

