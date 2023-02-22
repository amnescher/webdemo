### Client Vs Server Version

In this context, "sever" refers to the Mini server. In server deployment mode, AI micro service docker images are therefore created and run alongside minio server microservice on the same node. Nevertheless, in the client deployment mode, only the AI micro services are built as Docker images, and these micro services will connect to the minIO server running on a different node if the IP address of the node that runs the MINIO service is provided in an environmental variable file.


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

# Model weights
Step 1: update path to model/config directory in env_server.env file.

In server deployment mode, model weights and config files need to be uploaded to MINIO buckets once and then can be deployed by AI microservices multipletimes. 
 Please download these files from [Here](https://eschercloudai-my.sharepoint.com/:f:/g/personal/a_sabet_eschercloud_ai/EiJWs38Yl4FDgyFYrQOhkg4BPoqlLKAhSXlhzBPDgwD18w?e=YLaybW), then set STORAGE_PATH in the env_server.env to downloaded directory.
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
