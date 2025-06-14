

⸻

Projeto PySpark - Setup Rápido com Docker, Spark e Java 17

Requisitos
	•	Docker instalado
	•	Java 17 instalado (OpenJDK 17)
	•	Python 3.11 (ou compatível) com pyspark instalado

⸻

Passo 1: Configurar ambiente Java 17

Verifique o Java instalado:

java -version

Deve mostrar algo como:

openjdk version "17.0.13" ...


⸻

Passo 2: Rodar Spark local com Docker
	1.	Baixe a imagem oficial do Spark com Hadoop:

docker pull bitnami/spark:latest

	2.	Inicie um container Spark standalone:

docker run -d --name spark-master -p 7077:7077 -p 8080:8080 bitnami/spark:latest

	•	7077 é a porta padrão do Spark master
	•	8080 é a porta da UI web do Spark

⸻

Passo 3: Configurar PySpark para rodar localmente

No seu script Python (teste.py), use:

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Teste PySpark") \
    .master("local[*]") \  # roda localmente com todos os núcleos
    .getOrCreate()

df = spark.createDataFrame([
    ("Miguel", 32),
    ("Ana", 28)
], ["nome", "idade"])

df.show()

spark.stop()


⸻

Passo 4: Rodar o script PySpark

Ative seu virtualenv (se usar) e execute:

python teste.py

Você verá o DataFrame sendo exibido no terminal.

⸻

Passo 5 (opcional): Conectar ao Spark master no Docker

Se quiser rodar no cluster Docker:
	•	Garanta que o container Spark está rodando
	•	No script, altere .master() para o IP correto do host Docker, por exemplo:

.master("spark://localhost:7077")

	•	Atenção: host.docker.internal pode não funcionar no Mac/Linux. Use o IP da máquina.

⸻

Dicas rápidas
	•	Defina variável de ambiente para IP local, se necessário:

export SPARK_LOCAL_IP=192.168.x.x

	•	Use a UI web em http://localhost:8080 para monitorar o Spark.

⸻

Apontar pro java 17 no terminal
export JAVA_HOME=$(/usr/libexec/java_home -v17)
