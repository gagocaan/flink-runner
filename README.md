# Apache Beam Flink Runner Example

## Local Kubernetes setup on macOS with minikube and local Docker registry

### Requirements

> This is a variant of [Local Kubernetes setup on macOS with minikube on VirtualBox and local Docker registry](https://gist.github.com/kevin-smets/b91a34cea662d0c523968472a81788f7)

Minikube requires that VT-x/AMD-v virtualization is enabled in BIOS. To check that this is enabled on OSX / macOS run:

```bash
sysctl -a | grep machdep.cpu.features | grep VMX
```

If there's output, you're **good!**

### Prerequisites

* kubectl
* docker (for Mac)
* minikube

```bash
brew update && brew install kubectl && brew install --cask docker && brew install minikube
```

### Verify

```bash
    docker --version            #Docker version 20.10.17, build 100c701
    docker-compose --version    #Docker Compose version v2.6.1
    minikube version            #minikube version: v1.26.0
                                #commit: f4b412861bb746be73053c9f6d2895f12cf78565
    kubectl version --client    #Client Version: version.Info{Major:"1", Minor:"24", GitVersion:"v1.24.1", GitCommit:"3ddd0f45aa91e2f30c70734b175631bec5b5825a", GitTreeState:"clean", BuildDate:"2022-05-24T12:26:19Z", GoVersion:"go1.18.2", Compiler:"gc", Platform:"darwin/amd64"}
    #Kustomize Version: v4.5.4
```

### Start

```bash
minikube start
```

> This can take a while

Once minikube is running you can access the UI

```bash
minikube dashboard
```

> This will automatically open a new browser tab with the minikube UI

### Check k8s

```bash
kubectl get all
```

> You should have nothing running but kubernetes service.

## Environment setup

In this example we will deploy an [Apache Flink](https://flink.apache.org/) service where we can run [Apache Beam](https://beam.apache.org/) jobs in an isolated and controlled environment.

To ensure the service we will need a ConfigMap, a Service and two Deployments.

Now use the yaml configurations for a session environment on the Flink

1. ConfigMap --> [kube/flink-configuration-configmap.yaml](kube/flink-configuration-configmap.yaml): The flink-configuration-configmap.yaml
2. Service --> [kube/jobmanager-service.yaml](kube/jobmanager-service.yaml): Then the job manager service
3. Deployments --> [kube/jobmanager-session-deployment.yaml](kube/jobmanager-session-deployment.yaml): And the job manager session deployment
4. Deployments --> [kube/task-manager-session-deployment.yaml](kube/task-manager-session-deployment.yaml): This is the important part, we need to include the worker pools in the sidecar containers in the pod of the taskmanager shown in task-manager-session-deployment.yaml

The beam-worker-pool in is the addition to the original config

```yaml
- name: beam-worker-pool
  image: apache/beam_python3.10_sdk:2.49.0
  imagePullPolicy: Always
  args: ["--worker_pool"]
  ports:
  - containerPort: 50000
      name: pool
  livenessProbe:
  tcpSocket:
      port: 50000
  initialDelaySeconds: 30
  periodSeconds: 60
```

This ensures that another container is running in the task manager pod and will handle the job server. The job server runs `apache/beam_python3.10_sdk:2.49.0` image that is able to bundle our Apache BEAM pipelines written in python.

Something to note is that the port `50000` is used by the python pipeline options and used to communicate to the job server using the SDK Harness Configuration specified by [BEAM](https://beam.apache.org/documentation/runtime/sdk-harness-config/) which will allow the user code to be dispatched to an external service using the environment_type as `EXTERNAL`.

### Deploy

We have to apply this configurations files to the namespace (default) in the k8s cluster.

```bash
kubectl apply -f kube/
```

### Expose the Flink master

Lastly, we need to expose the Flink master. This is done in Minikube by port forwarding your local environment

```bash
kubectl port-forward <flink_master_container> 8081:8081
```

You can find your `<flink_master_container>` by running a `kubectl get all` and using the Flink master container name.

### Verify

Visit your dashboard at [localhost:8081](localhost:8081)

## Running your pipeline

Just run:

```bash
poetry run python -m main
```

To make sure the write to file at the end of the beam pipeline ran, we can visit the worker pool to find the output_file.txt.

```bash
kubectl exec -it flink-taskmanager-<id> -c beam-worker-pool -- bash
```

```console
root@flink-taskmanager-<id>:/# cat output_file.txt
```
