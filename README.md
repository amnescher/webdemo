# webdemo

## Weights

Obtain model weights [here](https://eschercloudai-my.sharepoint.com/:f:/g/personal/a_sabet_eschercloud_ai/EiJWs38Yl4FDgyFYrQOhkg4BPoqlLKAhSXlhzBPDgwD18w?e=rsJiUu), unzip the file and copy it into storage directory.

## Storage Directory
This repository assumes the following structure of storage directory:

```
storage
├── config.yaml
├── diff1
│   ├── img2img
│   └── txt2img
├── diff2
│   ├── img2img
│   ├── txt2img 
│   └── upscale
│ 
├── frontend
│   ├── butterfly.jpeg
│   ├── id.png
│   ├── logo.jpeg
│   ├── ocr.jpeg
│   └── vision.png
├── model_weights
│   ├── diff1
│   │   └── model_diff1.ckpt
│   └── diff2
│       ├── model.ckpt
│       └── x4-upscaler-ema.ckpt
└── test_image
```
## Build and run docker images 

In the webdemo directory run following command:

```
sudo docker compose build
sudo docker compose up
```

The names of the services are stored in the config.yaml file in the storage directory, along with a list of the ports that the frontend end uses to send requests to each service. The example that follows shows how to send a request from the front-end service to the donut backend service using the first item (donut[-1]) in the list of the port names associated with the donut service.

```
requests.post(f"http://{port_config.model_ports.donut[-1]}:8503/donut_pars", files=files)
```

## backend.py
Every backend service (stablediffusion1, stablediffusion2, donut) uses a backend.py script to receive API requests, process them with the appropriate AI model, and then respond to the request with the model's outputs. Responses to stablediffusion1 and stablediffusion2 are paths to the directories where the generated images are stored, allowing the front end to read these paths and display the images to the user, while the response to the donut model is a.json file containing the extracted texts from the document image.