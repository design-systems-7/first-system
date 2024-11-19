Стартуем 

```shell
minikube start
```

Применяем
```shell
kubectl apply -f configmaps/ &&
kubectl apply -f deployments/ &&
kubectl apply -f services/
```

```shell
kubectl get pods
```

```sh
kubectl delete deployments --all &&
kubectl delete services --all &&
kubectl delete configmaps --all
```