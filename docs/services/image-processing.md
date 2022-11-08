# image_processing

- [Code](../../services/image_processing/README.md)
- Access when deployed locally: <http://localhost:8181/docs>

## Description
This service provides generic image processing features, such as blurring, cropping, resizing etc... This service uses Pillow and opencv. This service was built and tested with python 3.9, therefore we recommend to use the docker version instead of running it natively.

## How to run
### Environment variables
Using both docker or your local python3, the engine will use the following environment variables if defined.

*General variables*

- APP_HOST: address on which the API will listen, default is 127.0.0.1
- APP_PORT: port the API will listen on, default is 8080
- APP_LOG: log level, default is info
- APP_ENGINE: the url to the engine, if provided, the service will announce itself to the engine periodically
- APP_SERVICE: the url of the service itself, needed to announce correct routes to the engine
- APP_NOTIFY_CRON: the frequency in second of the heartbeat announce to the engine, default is 30

### Run natively
#### Install dependencies
Install the requirements using `pip3`

```bash
pip3 install -r requirements.txt
```

* In order to work, opencv may need a few additional libs that you can install with your distribution package manager, check console at run time.
#### Run the tests
To run the tests, the following additional packages must be installed:

```bash
pip3 install pytest pytest-asyncio aiofile
```

Then, the tests can be run with:
```bash
python3 -m pytest --asyncio-mode=auto
```

#### Run
Then, you can run the following command to run it in dev:

```bash
python3 main.py
```

or with custom environment variables:

```bash
APP_HOST=0.0.0.0 APP_PORT=4040 APP_LOG=info APP_... python3 main.py
```

### Run locally using Kubernetes

Refer to the [Get started](../docs/getting-started.md) documentation in order to run this service locally.

### Use
The API documentation is automatically generated by FastAPI using the OpenAPI standard. A user friendly interface provided by Swagger is available under the `/docs` route, where the endpoints of teh service are described.

The following features are available:

- `/blur`: blur one or more areas on the image, takes `image` and `areas` json and returns the processed image as jpeg
- `/crop`: crop one or more areas on the image, takes `image` and `areas` json and returns the cropped image(s) as jpeg
- `/convert`: convert the image into the specified format, takes `image` and `format` json and returns the converted image
- `/analyze`: extract image metadata, takes `image` and returns a dict
- `/greyscale`: convert the image to black and white, takes `image` and returns the processed image as jpeg
- `/resize`: resize the image, takes `image` and `settings` json and returns the resized image as jpeg