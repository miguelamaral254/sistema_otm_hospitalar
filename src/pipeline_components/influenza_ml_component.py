import os
from pyspark.sql.functions import col, abs
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from shutil import rmtree

def processar_influenza(spark):
    # Caminho do arquivo de dados de influenza
    file_path = "src/data/processed/influenza_hospitalar_processed.parquet"
    df = spark.read.parquet(file_path)

    # Seleciona todas as colunas de influenza, exceto 'UF' e 'Ano'
    team_columns = [col for col in df.columns if col not in ['uf', 'ano']]

    # Converter todas as colunas de influenza para int (substituir valores não numéricos por 0)
    for column in team_columns:
        df = df.withColumn(column, col(column).cast("int"))

    # Usando essas colunas de influenza para criar as features
    assembler = VectorAssembler(
        inputCols=team_columns,
        outputCol="features"
    )
    df = assembler.transform(df)

    # Usar a coluna 'ano' como exemplo para o label (alterar conforme necessário)
    label_col = "ano"  # Usado como exemplo, altere conforme necessário

    # Dividir os dados em treino e teste
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    # Modelo de Regressão Linear
    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    lr_model = lr.fit(train_data)

    # Avaliar o modelo
    avaliar_modelo(lr_model, test_data)

def avaliar_modelo(lr_model, test_data):
    predictions = lr_model.transform(test_data)

    # Avaliação do modelo usando RMSE, MAE e MAPE
    evaluator_rmse = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="mae")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    # Calcular o MAPE corretamente
    mape = predictions.withColumn("error", abs(col("prediction") - col("ano")))
    mape = mape.withColumn("percent_error", (col("error") / col("ano")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    # Gerar o PDF com os resultados
    generate_pdf(rmse, mae, mape_value)

def generate_pdf(rmse, mae, mape):
    pdf_filename = "artifacts/resultados_modelo_influenza.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    
    c.drawString(100, height - 100, "Resultados do Modelo de Previsão de Influenza")

    c.drawString(100, height - 130, f"RMSE: {rmse}")
    c.drawString(100, height - 160, f"MAE: {mae}")
    c.drawString(100, height - 190, f"MAPE: {mape}%")

    c.save()