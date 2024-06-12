# example-services

Steps to build, push, publish and deploy service on an Edge device node

## Service peer
1. [Setup ENVIRONMENT variables](#1-setup-environment-variables)
2. [Publish Open Horizon service](#2-publish-open-horizon-service)
3. [Publish Open Horizon pattern](#3-publish-open-horizon-pattern)
4. [Register edge device node with a pattern](#4-register-edge-device-node-with-a-pattern)

### 1. Setup ENVIRONMENT variables
#### 1.1 Create ENVIRONMENT variables file
Create a file `~/project/rwec/ENV_RWEC` with the following content. 
Replace the content within `<>` with your values. 
Following setup assumes that you are using `Docker Hub`. 
If you are using any other container image registry then use the values accordingly, 

```
# Arbitrary text to organize the Open Horizon (OH) resources such as
# image, service, pattern names etc.
# You may choose to change these as you need. 
export EDGE_OWNER=rwec.edge
export EDGE_DEPLOY=example.service

# Container registry (CR) values
export DOCKER_BASE=<your-docker-namespace>
export CR_HOST=docker.io
export CR_USERNAME=<your-docker-namespace>
export CR_DOCKER_APIKEY=<your-docker-api-key>

# OH org and user credential 
export HZN_ORG_ID=myorg
export HZN_EXCHANGE_USER_AUTH=<aio-username>:<aio-api-key>
```
#### 1.2 Setup ENVIRONMENT variables in the shell 
```
source ~/project/rwec/ENV_RWEC
```

### 2. Publish Open Horizon service  
#### 2.1 Change to example-services directory
```
cd example-services
```
#### 2.2 Change to `service2` directory
```
cd publish/src/service-required
```
#### 2.6 Publish service
```
make publish-service
```
#### 2.7 Verify published service
```
hzn exchange service list
```
### 3. Publish Open Horizon pattern 
#### 3.1 Publish pattern
```
make publish-pattern 
```
#### 3.2 Verify published pattern
```
hzn exchange pattern list 
```
### 4. Register edge device node with a pattern 
#### 4.1 Register edge device node 
```
make register
```
#### 4.2 Verify node registration and agreement formation
```
hzn node list 
hzn agreement list
```
#### 4.3 Test and verify deployed application
```
make test-app-service
```
#### 4.4 Unregister the edge device node 
```
make unregister
```



