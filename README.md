
# Projeto PySpark - Setup Rápido com Docker, Spark e Java 17

Este guia fornece instruções para configurar rapidamente um ambiente PySpark local usando Docker, Java 17 e Python 3.9.

## Requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:

- **Docker** (instale a versão mais recente a partir do [site oficial](https://www.docker.com/get-started))
- **Java 17** (OpenJDK 17)
- **Python 3.9** (ou versão compatível) com o `pyspark` instalado

## Passo 1: Configurar o Ambiente Java 17

### Verificar a instalação do Java

Para verificar se o Java está instalado corretamente, execute o seguinte comando no terminal:

```bash
java -version
```

Você deve ver uma saída semelhante a:

```
openjdk version "17.0.13" ...
```

Se você não tiver o Java instalado, você pode [baixá-lo aqui](https://adoptopenjdk.net/) ou usar o Homebrew (para MacOS):

```bash
brew install openjdk@17
```

Após instalar, adicione o Java 17 ao seu ambiente com o comando:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v17)
```

## Passo 2: Rodar Spark Local com Docker

### Baixar a Imagem do Spark com Hadoop

Execute o comando abaixo para baixar a imagem oficial do Spark com Hadoop:

```bash
docker pull bitnami/spark:latest
```

### Iniciar o Container Spark Standalone

Execute o comando abaixo para iniciar o container Spark em modo standalone:

```bash
docker run -d --name spark-master -p 7077:7077 -p 8080:8080 bitnami/spark:latest
```

- **7077** é a porta padrão do Spark Master
- **8080** é a porta da UI web do Spark (você pode monitorar o status do Spark acessando [http://localhost:8080](http://localhost:8080))

## Passo 3: Configurar PySpark para Rodar Localmente

### Criar o Ambiente Virtual com Python 3.9

Crie um ambiente virtual com Python 3.9 para garantir compatibilidade com o PySpark:

```bash
python3.9 -m venv venv
source venv/bin/activate
```

### Instalar as Dependências

Dentro do ambiente virtual, instale o `pyspark` e outras dependências necessárias:

```bash
pip install pyspark
```

### Criar o Script de Teste

Crie um arquivo de teste (por exemplo, `teste.py`) e configure o Spark localmente com o seguinte código:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder     .appName("Teste PySpark")     .master("local[*]") \  # Roda localmente utilizando todos os núcleos disponíveis
    .getOrCreate()

df = spark.createDataFrame([
    ("Miguel", 32),
    ("Ana", 28)
], ["nome", "idade"])

df.show()

spark.stop()
```

### Executar o Script PySpark

Agora, você pode rodar o script PySpark para testar sua instalação:

```bash
python teste.py
```

Você verá a saída no terminal com o DataFrame exibido.

## Passo 4: Rodar o Projeto - Executando o Arquivo Starter

### Como Executar o Projeto

Para executar o seu projeto PySpark, basta rodar o script `starter.py`, que inicializa todo o pipeline de processamento de dados:

```bash
python starter.py
```

Esse arquivo `starter.py` vai rodar os processos de machine learning necessários e executar os pipelines conforme configurado no projeto.

## Passo 5 (Opcional): Conectar ao Spark Master no Docker

Se você deseja rodar o PySpark em um cluster Docker:

1. Certifique-se de que o container Spark está rodando.
2. Alterar no script PySpark o parâmetro `.master()` para o IP correto do host Docker:

```python
spark = SparkSession.builder     .appName("Teste PySpark")     .master("spark://localhost:7077") \  # Use o IP do seu Docker se necessário
    .getOrCreate()
```

**Atenção**: No Mac/Linux, o `host.docker.internal` pode não funcionar como esperado. Use o IP local do seu Docker.

## Dicas Rápidas

- Para ajustar o nível de log do Spark, você pode usar:

```python
spark.sparkContext.setLogLevel("ERROR")
```

- Para monitorar o Spark, use a UI web do Spark disponível em [http://localhost:8080](http://localhost:8080).
