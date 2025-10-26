import mysql.connector
import pandas as pd
from sklearn.datasets import load_iris
import os

print("🚀 Iniciando carga de datos Iris a MySQL...")

# Cargar el dataset Iris
iris = load_iris()
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_df['target'] = iris.target

print(f"✅ Dataset cargado: {len(iris_df)} filas")

# Conectar a MySQL
try:
    conn = mysql.connector.connect(
        host="mysql-service",
        user="my_app_user",
        password="my_app_pass",
        database="my_app_db"
    )
    print("✅ Conectado a MySQL")
except Exception as e:
    print(f"❌ Error conectando a MySQL: {e}")
    exit(1)

cursor = conn.cursor()

# Crear la tabla
create_table_query = """
CREATE TABLE IF NOT EXISTS iris_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sepal_length FLOAT,
    sepal_width FLOAT,
    petal_length FLOAT,
    petal_width FLOAT,
    target INT
);
"""
cursor.execute(create_table_query)
conn.commit()
print("✅ Tabla 'iris_data' creada o ya existe")

# Limpiar datos anteriores (opcional)
cursor.execute("DELETE FROM iris_data")
conn.commit()
print("🗑️ Datos anteriores eliminados")

# Insertar datos
insert_query = """
INSERT INTO iris_data (sepal_length, sepal_width, petal_length, petal_width, target)
VALUES (%s, %s, %s, %s, %s);
"""
data_to_insert = iris_df.values.tolist()
cursor.executemany(insert_query, data_to_insert)
conn.commit()

print(f"✅ {len(data_to_insert)} filas insertadas en 'iris_data'")

# Verificar
cursor.execute("SELECT COUNT(*) FROM iris_data")
count = cursor.fetchone()[0]
print(f"✅ Verificación: {count} filas en la tabla")

# Cerrar conexión
cursor.close()
conn.close()

print("🎉 Proceso completado exitosamente!")