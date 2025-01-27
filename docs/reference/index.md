# Reference

## [Engine](engine.md) and [Webapp](webapp.md)

| Service                                           | Code                                                      | URL when run locally with minikube    | URL when deployed on Fribourg's Kubernetes            |
| ------------------------------------------------- | --------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------- |
| [Engine](./engine.md){ style="color: inherit;" }  | <https://github.com/csia-pme/csia-pme/tree/main/engine>   | <http://localhost:8080/docs>          | <https://engine-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [Webapp](./webapp.md){ style="color: inherit;" }  | <https://github.com/csia-pme/csia-pme/tree/main/webapp>   | <http://localhost:8181/docs>          | <https://webapp-csia-pme.kube.isc.heia-fr.ch/docs>    |

## [Authentication](./auth.md)

## [Services](./service.md)

| Service                                                                   | Code                                                                          | URL when run locally with minikube    | URL when deployed on Fribourg's Kubernetes                    |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------- |
| [ae-ano-detection](./ae-ano-detection.md){ style="color: inherit;" }      | <https://github.com/csia-pme/csia-pme/tree/main/services/ae-ano-detection>    | <http://localhost:8282/docs>          | <https://ae-ano-detection-csia-pme.kube.isc.heia-fr.ch/docs>  |
| [average-shade](./average-shade.md){ style="color: inherit;" }            | <https://github.com/csia-pme/csia-pme/tree/main/services/average-shade>       | <http://localhost:8383/docs>          | <https://average-shade-csia-pme.kube.isc.heia-fr.ch/docs>     |
| [digit-recognition](./digit-recognition.md){ style="color: inherit;" }    | <https://github.com/csia-pme/csia-pme/tree/main/services/digit-recognition>   | <http://localhost:8484/docs>          | <https://digit-recognition-csia-pme.kube.isc.heia-fr.ch/docs> |
| [face-analyzer](./face-analyzer.md){ style="color: inherit;" }            | <https://github.com/csia-pme/csia-pme/tree/main/services/face-analyzer>       | <http://localhost:8585/docs>          | <https://face-analyzer-csia-pme.kube.isc.heia-fr.ch/docs>     |
| [face-detection](./face-detection.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/face-detection>      | <http://localhost:8686/docs>          | <https://face-detection-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-analyzer](./image-analyzer.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-analyzer>      | <http://localhost:8787/docs>          | <https://image-analyzer-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-blur](./image-blur.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-blur>      | <http://localhost:8888/docs>          | <https://image-blur-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-convert](./image-convert.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-convert>      | <http://localhost:8989/docs>          | <https://image-convert-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-crop](./image-crop.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-crop>      | <http://localhost:9090/docs>          | <https://image-crop-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-greyscale](./image-greyscale.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-greyscale>      | <http://localhost:9191/docs>          | <https://image-greyscale-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-resize](./image-resize.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-resize>      | <http://localhost:9292/docs>          | <https://image-resize-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-rotate](./image-rotate.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-rotate>      | <http://localhost:9393/docs>          | <https://image-rotate-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [image-sam](./image-sam.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/image-sam>      | <http://localhost:9494/docs>          | <https://image-sam-csia-pme.kube.isc.heia-fr.ch/docs>    |

## [Pipelines](./pipeline.md)

| Pipeline                                                                  | Chained services                                                              |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Face Blur                                                                 | Face detection, Image blur                                                    |
