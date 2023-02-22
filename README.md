### GPU requirement

35GB or more of GPU memory is needed to deploy all AI services. To test the demo with less available GPU memory, one can disable one or both of backend_stable_v2_1/backend_stable_v1_1 services in the docker compose files.
### Client Vs Server mode

In this context, "sever" refers to the Mini server. In server deployment mode, AI micro service docker images are build and run alongside minio server microservice on the same node. While, in the client deployment mode, only the AI micro services are built as Docker images, and these micro services will connect to a minIO server running on a different node with the IP address of the node that runs the MINIO service is provided as an environmental variable file.


-- We recommend client deployment mode for testing purposes because we provide the IP of a node that runs the MINIO server. 


## Client Deployment.

Client deployment mode assumes that the IP address of a node running the Minio server, where all model weights and configuration files are stored in buckets, is available in the env_client.env file along with other necessary environmental variables.  

Run the following commands in the webdemo directory to deploy web-demo in client mode.

```
sudo docker compose  -f docker-compose-client.yml   --env-file ./env_client.env build
sudo docker compose  -f docker-compose-client.yml   --env-file ./env_client.env up
```

NOTE: -—env-file specifies the location of the environment variable file, env_client.env, which stores the credentials for logging into the database, the MINIO server, and the MINIO server IP.

## Server Deployment.

Step 1: Update STORAGE_PATH in env_server.env file.   STORAGE_PATH refers to the directory in which model/config files are stored.

In server deployment mode,  model weights and configuration files must be uploaded once to MINIO buckets before being deployed multiple times by AI microservices.

Please download these files from [Here](https://eschercloudai-my.sharepoint.com/:f:/g/personal/a_sabet_eschercloud_ai/EiJWs38Yl4FDgyFYrQOhkg4BPoqlLKAhSXlhzBPDgwD18w?e=YLaybW). Then,Set the downloaded directory as the STORAGE_PATH in the env_server.env file.
 e.g., STORAGE PATH = path/storage/

Step 2: Build docker images for AI micro services and MINIO server.

The following commands must be run in order to build and run the docker images before one can deploy web-demo in server mode.

```
sudo docker compose  -f docker-compose-server.yml   --env-file ./env_server.env build
sudo docker compose  -f docker-compose-server.yml   --env-file ./env_server.env up
```

Running the above commands will result in errors because the MINIO server was created in conjunction with AI micro services, but these services cannot connect to the MINIO server without access key and secret key. 


Step 2: Generate access key and secret key and restart docker images. 

Open http://localhost:9000/ in your browser and generate an access_key/secret_key pair  and store them in env_server.env file.
One needs to restart running Docker images in order for them to connect to MINIO server and upload model weights and configuration files. To do this, run the following command in a new terminal window.

```
sudo docker compose -f  docker-compose-server.yml   --env-file ./env_server.env  restart
```


Note: If you want to create a new deployment with a new database password, make sure that the database docker volume from earlier deployments has been deleted. Otherwise, db will attempt to connect to the same database with a different password, which results in an error.