
## Build and run docker images 

In the webdemo directory run following command:

```
sudo docker compose --env-file ./env.env build
sudo docker compose --env-file ./env.env up
```
NOTE: —env-file is the path to the environment variable file where the credentials for connecting to the minIO storage server and the database are stored. 

The names of the micro services are stored in the config.yaml file in the minIO storage bucket, along with a list of the ports that the frontend end uses to send requests to each service. The example that follows shows how to send a request from the front-end service to the donut backend service using the first item (donut[-1]) in the list of the port names associated with the donut service.

```
requests.post(f"http://{port_config.model_ports.donut[-1]}:8503/donut_pars", files=files)
```

## backend.py
Every backend service (stablediffusion1, stablediffusion2, donut, GFPGAN-faceRestoration) uses a backend.py script to receive API requests, process them with the appropriate AI model, and then respond to the request with the model's outputs. Responses to stablediffusion1 and stablediffusion2 are paths to the directories where the generated images are stored, allowing the front end to read these paths and display the images to the user, while the response to the donut model is a.json file containing the extracted texts from the document image.

## db
To keep track of requests for backend services, a database is set up. After receiving a request, a backend stores the request's specifics and execution-related data, such as runtime, in a database.