# KFServe

KServe is a standard Model Inference Platform on Kubernetes. [Kserve](https://kserve.github.io/website/0.8/) (formely know as KFServing) aims to solve production model serving use cases by providing performant, high abstraction interfaces for common ML frameworks like Tensorflow, XGBoost, ScikitLearn, PyTorch, and ONNX.

Some of the features of KSever include

* Provides high scalability, density packing and intelligent routing using ModelMesh
* Advanced deployments with canary rollout, experiments, ensembles and transformers.
* Simple and Pluggable production serving for production ML serving including prediction, pre/post processing, monitoring and explainability.
* Support modern serverless inference workload with Autoscaling including Scale to Zero on GPU.
* Provides performant, standardized inference protocol across ML frameworks

In this exercise, we will deploy our huggingface transformer model using KServe.

Pre-requisites

* Kind
* Kubectl

If kubernetes version >= 1.24 (`kubectl version`)

Install Kserve, Knative, Istio and Cert-Manager

```bash
kind create cluster --name kserve
kubectl cluster-info --context kind-kserve
bash quick_install.sh
```

## Run

### Locally

Test the sentiment classifier model

```bash
docker build -t sentiment -f project/sentiment/Dockerfile.sentiment project/sentiment/
docker run --rm -it sentiment
```

Run tests using `pytest`

```bash
docker build -t sentiment -f Dockerfile.test .
docker run -p 8000:8000 -it -v $(pwd):/app --entrypoint bash sentiment
pytest --cov
```

### Deploy using KServe

KServe [uses](https://github.com/pytorch/serve/tree/master/kubernetes/kserve) TorchServe to create a inference service. TorchServe provides a utility to package all the pytorch model artifacts into a single [Torchserve Model Archive Files (MAR)](https://github.com/pytorch/serve/blob/master/model-archiver/README.md).

#### Running Torchserve inference service in KServe

Please follow the below steps to deploy Torchserve in KServe Cluster

* Step - 1 : Create the `.mar` file for sentiment hugging face model.

    Converting HuggingFace Transformer model to `SentimentClassification.mar` using torchserve : [torchserve-huggingface-transformers](https://github.com/dudeperf3ct/torchserve-huggingface-transformers)

* Step - 2 : Create a config.properties file and place the contents like below:

    ```bash
    inference_address=http://0.0.0.0:8085
    management_address=http://0.0.0.0:8085
    metrics_address=http://0.0.0.0:8082
    grpc_inference_port=7070
    grpc_management_port=7071
    enable_metrics_api=true
    metrics_format=prometheus
    number_of_netty_threads=4
    job_queue_size=10
    enable_envvars_config=true
    install_py_dep_per_model=true
    model_store=/mnt/models/model-store
    model_snapshot={"name":"startup.cfg","modelCount":1,"models":{"sentiment":{"1.0":{"defaultVersion":true,"marName":"SentimentClassification.mar","minWorkers":1,"maxWorkers":5,"batchSize":1,"maxBatchDelay":10,"responseTimeout":120}}}}
    ```

    Please note that, the port for inference address should be set at `8085` since KServe by default makes use of `8080` for its inference service. When we make an Inference Request, in Torchserve it makes use of port 8080, whereas on the KServe side it makes use of port 8085. The path of the model store should be mentioned as `/mnt/models/model-store` because KServe mounts the model store from that path.

    > The config.properties file includes the flag service_envelope=kfserving to enable the KServe inference protocol. The requests are converted from KServe inference request format to torchserve request format and sent to the inference_address configured via local socket.

* Step - 3 : Upload the v1 folder to your AWS s3 or GCP gs bucket

    The KServe/TorchServe integration expects following model store layout.

    ```bash
    v1
    ├── config
    │   └── config.properties
    └── model-store
        └── SentimentClassification.mar

    2 directories, 2 files
    ```

### Test locally

```bash
# make changes by adding your access key and secret key in `secrets/s3_secrets.yaml` file
kubectl apply -f secrets/s3_secrets.yaml
# change your s3 bucket url in torchserve.yaml file
kubectl apply -f torchserve.yaml
# monitor status of service
kubectl get isvc
# in separate terminal
watch -n0.5 kubectl get pods
# in separate terminal
kubectl logs <pod-name> -f
# once service status is ready in `kubectl get isvc sentiment`
# check if URL is assigned to the inference service, if not try debubbing using mnist.yaml file and see if it succeeds
# in separate terminal do port forwarding
INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')
kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80
# in separate terminal test the endpoint using curl
SERVICE_HOSTNAME=$(kubectl get inferenceservice sentiment -o jsonpath='{.status.url}' | cut -d "/" -f 3)
export INGRESS_HOST=localhost
export INGRESS_PORT=8080
# using curl
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://localhost:8080/v1/models/sentiment:predict -d @./sample_text0.json
# using httpie
http POST http://localhost:8080/v1/models/sentiment:predict Host:${SERVICE_HOSTNAME} < sample_text0.json 
```

After models are deployed onto model servers with KServe, you get all the following serverless features provided by KServe.

* Scale to and from Zero
* Request based Autoscaling on CPU/GPU
* Revision Management
* Optimized Container
* Batching
* Request/Response logging
* Scalable Multi Model Serving
* Traffic management
* Security with AuthN/AuthZ
* Distributed Tracing
* Out-of-the-box metrics
* Ingress/Egress control

### Further Readings

* Autoscaling: One of the main serverless inference features is to automatically scale the replicas of an `InferenceService` matching the incoming workload. KServe by default enables [Knative Pod Autoscaler](https://knative.dev/docs/serving/autoscaling/) which watches traffic flow and scales up and down based on the configured metrics.

    [Autoscaling Example](https://github.com/kserve/kserve/blob/master/docs/samples/v1beta1/torchserve/autoscaling/README.md)

* Canary Rollout : Canary rollout is a deployment strategy when you release a new version of model to a small percent of the production traffic.

    [Canary Deployment](https://github.com/kserve/kserve/blob/master/docs/samples/v1beta1/torchserve/canary/README.md)

* Monitoring : [Expose metrics and setup grafana dashboards](https://github.com/kserve/kserve/blob/master/docs/samples/v1beta1/torchserve/metrics/README.md)

### Exercise

* Deploy and test the endpoint using v2 protocol of the same application.
