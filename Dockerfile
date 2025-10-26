# Usar una imagen base de Python
FROM python:3.9

# Crear un directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el script Python y cualquier archivo necesario al contenedor
COPY python-iris.py /app/python-iris.py

# Instalar las dependencias necesarias
RUN pip install mysql-connector-python pandas scikit-learn

# Comando para ejecutar el script al iniciar el contenedor
CMD ["python", "/app/python-iris.py"]
