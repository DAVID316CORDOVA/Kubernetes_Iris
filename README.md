# 🗄️ MySQL + Python Iris Dataset en Kubernetes

Este proyecto despliega MySQL en Kubernetes (Minikube) y carga el dataset Iris usando un Job de Python.

---

## 📁 Estructura del Proyecto

```
mysql-k8s/
├── Dockerfile              # Imagen Docker de Python con dependencias
├── python-iris.py          # Script para cargar datos Iris a MySQL
├── python-job.yaml         # Job de Kubernetes (ejecuta el script)
├── mysql-secret.yaml       # Contraseñas de MySQL (Base64)
├── mysql-pvc.yaml          # Almacenamiento persistente (1GB)
└── mysql-deployment.yaml   # Deployment y Service de MySQL
```

---

## 🎯 ¿Qué hace este proyecto?

1. **Despliega MySQL** en Kubernetes con almacenamiento persistente
2. **Carga el dataset Iris** (150 filas) desde un script Python
3. **Persiste los datos** en un volumen para que no se pierdan

---

## 📋 Prerrequisitos

- Minikube instalado y corriendo
- kubectl configurado (viene con Minikube)

```bash
# Verificar que Minikube está corriendo
minikube status

# Si no está corriendo, iniciarlo
minikube start
```

---

## 🚀 Despliegue Paso a Paso

### **Paso 1: Clonar o crear la carpeta del proyecto**

```bash
mkdir mysql-k8s
cd mysql-k8s
```

Copiar todos los archivos (`.yaml`, `Dockerfile`, `python-iris.py`) en esta carpeta.

---

### **Paso 2: Desplegar MySQL**

#### **2.1. Crear el Secret (contraseñas)**

```bash
kubectl apply -f mysql-secret.yaml
```

**¿Qué hace?**
- Crea un objeto Secret llamado `mysql-secret`
- Guarda 2 contraseñas en Base64:
  - `mysql-root-password`: Contraseña del usuario `root` (`root_pass`)
  - `mysql-password`: Contraseña del usuario `my_app_user` (`my_app_pass`)

**Verificar:**
```bash
kubectl get secrets
```

---

#### **2.2. Crear el PVC (almacenamiento)**

```bash
kubectl apply -f mysql-pvc.yaml
```

**¿Qué hace?**
- Solicita 1GB de almacenamiento persistente
- Crea un "disco virtual" donde MySQL guardará sus datos
- Los datos NO se pierden si el pod se reinicia

**Verificar:**
```bash
kubectl get pvc
```

Deberías ver `STATUS: Bound` (significa que está conectado correctamente).

---

#### **2.3. Desplegar MySQL**

```bash
kubectl apply -f mysql-deployment.yaml
```

**¿Qué hace?**
- Crea un **Deployment** con 1 réplica de MySQL 8.0
- Conecta las contraseñas desde el Secret
- Monta el PVC en `/var/lib/mysql` (donde MySQL guarda datos)
- Crea un **Service** llamado `mysql-service` en el puerto 3306
- Configura probes de salud (liveness y readiness)

**Verificar:**
```bash
kubectl get pods
```

Espera hasta que veas:
```
NAME                               READY   STATUS    RESTARTS   AGE
mysql-deployment-xxxxxxxxxx-xxxxx  1/1     Running   0          30s
```

**Ver logs de MySQL:**
```bash
kubectl logs deployment/mysql-deployment
```

Busca la línea:
```
[Server] /usr/sbin/mysqld: ready for connections
```

---

### **Paso 3: Construir la imagen de Python**

#### **3.1. Configurar Docker para usar Minikube**

```bash
eval $(minikube docker-env)
```

**¿Por qué?**
- Minikube tiene su propio Docker interno
- Este comando configura tu terminal para usar ese Docker
- Las imágenes que construyas estarán disponibles en Kubernetes

---

#### **3.2. Construir la imagen**

```bash
docker build -t python-iris:v1 .
```

**¿Qué hace?**
- Usa Python 3.11 como base
- Instala dependencias: `mysql-connector-python`, `pandas`, `scikit-learn`
- Copia el script `python-iris.py`
- Crea una imagen llamada `python-iris:v1`

**Verificar:**
```bash
docker images | grep python-iris
```

---

### **Paso 4: Ejecutar el Job de Python**

```bash
kubectl apply -f python-job.yaml
```

**¿Qué hace?**
- Crea un **Job** (tarea única) llamado `iris-data-loader`
- Ejecuta el script `python-iris.py` una sola vez
- Se conecta a `mysql-service:3306`
- Crea la tabla `iris_data` si no existe
- Inserta 150 filas del dataset Iris
- Cuando termina, el pod queda en estado `Completed`

**Ver el progreso:**
```bash
kubectl get pods -w
```

Presiona `Ctrl+C` cuando veas:
```
iris-data-loader-xxxxx   0/1   Completed   0   1m
```

**Ver los logs del Job:**
```bash
kubectl logs job/iris-data-loader
```

Deberías ver:
```
🚀 Iniciando carga de datos Iris a MySQL...
✅ Dataset cargado: 150 filas
✅ Conectado a MySQL
✅ Tabla 'iris_data' creada o ya existe
🗑️ Datos anteriores eliminados
✅ 150 filas insertadas en 'iris_data'
✅ Verificación: 150 filas en la tabla
🎉 Proceso completado exitosamente!
```

---

## 🔍 Verificar los Datos en MySQL

### **Opción 1: Desde un pod temporal**

```bash
kubectl run mysql-client --image=mysql:8.0 --rm -it --restart=Never -- mysql -h mysql-service -u my_app_user -pmy_app_pass -D my_app_db
```

Dentro de MySQL:
```sql
-- Ver tablas
SHOW TABLES;

-- Contar filas
SELECT COUNT(*) FROM iris_data;

-- Ver primeros 5 registros
SELECT * FROM iris_data LIMIT 5;

-- Salir
exit
```

---

### **Opción 2: Port-forward para acceder desde tu computadora**

```bash
kubectl port-forward service/mysql-service 3306:3306
```

Deja esta terminal abierta. Luego, desde MySQL Workbench, DBeaver o terminal:

```bash
mysql -h 127.0.0.1 -P 3306 -u my_app_user -pmy_app_pass -D my_app_db
```

---

## 📊 Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                    │
│                                                          │
│  ┌────────────────┐         ┌─────────────────────┐     │
│  │ Secret         │         │ PVC (1GB)           │     │
│  │ mysql-secret   │         │ mysql-pvc           │     │
│  │ - root_pass    │         │ - Almacenamiento    │     │
│  │ - my_app_pass  │         │   persistente       │     │
│  └────────┬───────┘         └──────────┬──────────┘     │
│           │                            │                │
│           ↓                            ↓                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Deployment: mysql-deployment                      │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────┐     │  │
│  │  │ Pod: MySQL 8.0                          │     │  │
│  │  │ - Puerto: 3306                          │     │  │
│  │  │ - Base de datos: my_app_db              │     │  │
│  │  │ - Usuario: my_app_user                  │     │  │
│  │  │ - Volumen: /var/lib/mysql               │     │  │
│  │  └─────────────────────────────────────────┘     │  │
│  └───────────────────────────────────────────────────┘  │
│           ↑                                             │
│           │                                             │
│  ┌────────┴──────────┐                                  │
│  │ Service           │                                  │
│  │ mysql-service     │                                  │
│  │ - ClusterIP       │                                  │
│  │ - Puerto: 3306    │                                  │
│  └────────┬──────────┘                                  │
│           ↑                                             │
│           │                                             │
│  ┌────────┴──────────────────────────────────────┐     │
│  │ Job: iris-data-loader                         │     │
│  │                                               │     │
│  │  ┌─────────────────────────────────────┐     │     │
│  │  │ Pod: python-iris:v1                 │     │     │
│  │  │ - Script: python-iris.py            │     │     │
│  │  │ - Conecta a: mysql-service:3306     │     │     │
│  │  │ - Inserta 150 filas en iris_data    │     │     │
│  │  │ - Estado final: Completed           │     │     │
│  │  └─────────────────────────────────────┘     │     │
│  └───────────────────────────────────────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Descripción de los Archivos

### **1. `mysql-secret.yaml`**

**Propósito:** Almacenar contraseñas de forma segura.

**Contenido:**
- `mysql-root-password`: Contraseña del usuario root (Base64)
- `mysql-password`: Contraseña del usuario `my_app_user` (Base64)

**Tipo:** `Secret` (objeto de Kubernetes para datos sensibles)

**Generar contraseñas en Base64:**
```bash
echo -n "tu_contraseña" | base64
```

---

### **2. `mysql-pvc.yaml`**

**Propósito:** Solicitar almacenamiento persistente.

**Contenido:**
- `storage: 1Gi`: Solicita 1GB de espacio
- `accessModes: ReadWriteOnce`: Solo un pod puede escribir a la vez
- `storageClassName: standard`: Usa la clase de almacenamiento por defecto de Minikube

**Tipo:** `PersistentVolumeClaim` (solicitud de disco)

---

### **3. `mysql-deployment.yaml`**

**Propósito:** Desplegar MySQL y exponerlo internamente.

**Componentes:**

#### **Deployment:**
- **Imagen:** `mysql:8.0` (descargada de Docker Hub)
- **Réplicas:** 1 (solo una instancia)
- **Variables de entorno:**
  - `MYSQL_ROOT_PASSWORD`: Desde el Secret
  - `MYSQL_DATABASE`: `my_app_db`
  - `MYSQL_USER`: `my_app_user`
  - `MYSQL_PASSWORD`: Desde el Secret
- **Volumen:** Monta `mysql-pvc` en `/var/lib/mysql`
- **Recursos:**
  - Requests: 256Mi RAM, 250m CPU
  - Limits: 512Mi RAM, 500m CPU
- **Probes:**
  - `livenessProbe`: Verifica que MySQL está vivo (ping cada 10s)
  - `readinessProbe`: Verifica que MySQL está listo para conexiones

#### **Service:**
- **Tipo:** `ClusterIP` (solo accesible dentro del cluster)
- **Puerto:** 3306
- **Nombre DNS:** `mysql-service`

---

### **4. `Dockerfile`**

**Propósito:** Construir la imagen de Python con dependencias.

**Contenido:**
- Base: `python:3.11-slim`
- Instala librerías del sistema para MySQL
- Instala paquetes Python: `mysql-connector-python`, `pandas`, `scikit-learn`
- Copia el script `python-iris.py`
- Ejecuta el script al arrancar

---

### **5. `python-iris.py`**

**Propósito:** Script que carga el dataset Iris a MySQL.

**Flujo:**
1. Carga el dataset Iris desde `scikit-learn` (150 filas)
2. Se conecta a MySQL en `mysql-service:3306`
3. Crea la tabla `iris_data` si no existe
4. Elimina datos anteriores (opcional)
5. Inserta las 150 filas
6. Verifica la cantidad de filas insertadas

**Columnas de la tabla:**
- `id`: INT AUTO_INCREMENT PRIMARY KEY
- `sepal_length`: FLOAT
- `sepal_width`: FLOAT
- `petal_length`: FLOAT
- `petal_width`: FLOAT
- `target`: INT (0, 1, 2 = especies de iris)

---

### **6. `python-job.yaml`**

**Propósito:** Ejecutar el script Python una sola vez.

**Componentes:**
- **Tipo:** `Job` (tarea única, no se reinicia)
- **Imagen:** `python-iris:v1` (construida localmente)
- **imagePullPolicy:** `Never` (usar imagen local, no descargar)
- **restartPolicy:** `Never` (no reiniciar al terminar)
- **backoffLimit:** 4 (reintentar máximo 4 veces si falla)

**Variables de entorno:**
- `MYSQL_HOST`: `mysql-service`
- `MYSQL_USER`: `my_app_user`
- `MYSQL_PASSWORD`: Desde el Secret
- `MYSQL_DATABASE`: `my_app_db`

---

## 🛠️ Comandos Útiles

### **Ver todos los recursos**
```bash
kubectl get all
```

### **Ver logs de MySQL**
```bash
kubectl logs deployment/mysql-deployment
kubectl logs -f deployment/mysql-deployment  # En tiempo real
```

### **Ver logs del Job**
```bash
kubectl logs job/iris-data-loader
```

### **Describir un pod (para debugging)**
```bash
kubectl describe pod <nombre-del-pod>
```

### **Entrar a un pod de MySQL**
```bash
kubectl exec -it <nombre-del-pod-mysql> -- bash
mysql -u root -proot_pass
```

### **Reiniciar el Job (recargar datos)**
```bash
kubectl delete job iris-data-loader
kubectl apply -f python-job.yaml
```

### **Ver eventos del cluster**
```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

## 🗑️ Limpieza (Eliminar todo)

```bash
# Eliminar el Job
kubectl delete job iris-data-loader

# Eliminar MySQL
kubectl delete -f mysql-deployment.yaml

# Eliminar PVC (esto borra los datos)
kubectl delete -f mysql-pvc.yaml

# Eliminar Secret
kubectl delete -f mysql-secret.yaml

# O eliminar TODO de golpe
kubectl delete all --all
kubectl delete pvc --all
kubectl delete secrets --all
```

---

## 🚨 Solución de Problemas

### **Problema: Pod en estado `ImagePullBackOff`**

**Causa:** No se ejecutó `eval $(minikube docker-env)` antes de construir la imagen.

**Solución:**
```bash
eval $(minikube docker-env)
docker build -t python-iris:v1 .
kubectl delete pod <nombre-del-pod>
```

---

### **Problema: MySQL no arranca**

**Verificar logs:**
```bash
kubectl logs deployment/mysql-deployment
```

**Verificar el PVC:**
```bash
kubectl get pvc
# Debe estar en STATUS: Bound
```

**Verificar el Secret:**
```bash
kubectl get secrets
```

---

### **Problema: El Job falla**

**Ver logs:**
```bash
kubectl logs job/iris-data-loader
```

**Causas comunes:**
- MySQL no está listo (esperar 30s después de desplegar MySQL)
- Contraseña incorrecta en el Secret
- MySQL Service no existe

**Verificar conectividad:**
```bash
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup mysql-service
```

---

## 📚 Conceptos de Kubernetes Usados

| Objeto | Descripción | Archivo |
|--------|-------------|---------|
| **Secret** | Almacena datos sensibles (contraseñas) | `mysql-secret.yaml` |
| **PVC** | Solicita almacenamiento persistente | `mysql-pvc.yaml` |
| **Deployment** | Gestiona pods de larga duración | `mysql-deployment.yaml` |
| **Service** | Expone pods con un nombre DNS fijo | `mysql-deployment.yaml` |
| **Job** | Ejecuta tareas únicas (no se reinician) | `python-job.yaml` |

---

## 🎓 Diferencias con Docker Compose

| Docker Compose | Kubernetes |
|----------------|------------|
| 1 archivo `docker-compose.yml` | Múltiples archivos YAML |
| `docker-compose up` | `kubectl apply -f` |
| `environment:` | `Secret` + `env:` |
| `volumes:` | `PersistentVolumeClaim` |
| `ports:` | `Service` |
| Escala manualmente | Escala automáticamente |

---

## 📖 Recursos Adicionales

- [Documentación de Kubernetes](https://kubernetes.io/docs/)
- [Documentación de Minikube](https://minikube.sigs.k8s.io/docs/)
- [Iris Dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html)

---

## 👨‍💻 Autor

Proyecto de aprendizaje de Kubernetes con MySQL y Python.

---

## 📄 Licencia

MIT License - Libre para uso educativo.
