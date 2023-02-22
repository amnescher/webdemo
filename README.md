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

Step 1: The following commands must be run in order to build and run the docker images before one can deploy web-demo in server mode.

```
sudo docker compose  -f docker-compose-server.yml   --env-file ./env_server.env build
sudo docker compose  -f docker-compose-server.yml   --env-file ./env_server.env up
```
Runing the above command you will encounter error because the MINIO server was build with alongside AI microservices and these services are not able to connect to MINIO server unless access_key and secert_key are provided. One needs to got to http://localhost:9000/ and generate access_key secret_key and store them in env_server.env file.

Running the above commands will result in errors because the MINIO server was created in conjunction with AI micro services, and these services cannot connect to the MINIO server without access key and secret key. 
Step 2: Generate access key and secret key and restart docker images. 
Open http://localhost:9000/ in your browser and generate an access_key/secret_key pair  and store them in env_server.env file.
One needs to restart running Docker images in order for them to connect to MINIO server and upload model weights and configuration files. To do this, run the following command in a new terminal window.

```
sudo docker compose -f  docker-compose-server.yml   --env-file ./env_server.env  restart
```
