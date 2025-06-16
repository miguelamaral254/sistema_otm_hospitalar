import os
from pyspark.sql.functions import col, abs
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def processar_dados_populacao(spark):
    file_path = "src/data/processed/populacao_estados_nordeste_2024.parquet"
    df = spark.read.parquet(file_path)

    # Converte as colunas necessárias para o tipo correto
    df = df.withColumn("populacao", col("populacao").cast("int")) \
           .withColumn("ano", col("ano").cast("int"))

    # Usando apenas a coluna de população como feature
    feature_columns = ["populacao"]
    
    assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features"
    )
    df = assembler.transform(df)

    label_col = "populacao"

    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    lr_model = lr.fit(train_data)

    avaliar_modelo(lr_model, test_data, df)

def avaliar_modelo(lr_model, test_data, df):
    predictions = lr_model.transform(test_data)

    evaluator_rmse = RegressionEvaluator(labelCol="populacao", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="populacao", predictionCol="prediction", metricName="mae")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    mape = predictions.withColumn("error", abs(col("prediction") - col("populacao")))
    mape = mape.withColumn("percent_error", (col("error") / col("populacao")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    generate_pdf(rmse, mae, mape_value, df)

def generate_pdf(rmse, mae, mape, df):
    pdf_filename = "artifacts/resultados_modelo_populacao.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    
    c.drawString(100, height - 100, "Resultados do Modelo de Previsão de População do Nordeste")

    c.drawString(100, height - 130, f"RMSE: {rmse}")
    c.drawString(100, height - 160, f"MAE: {mae}")
    c.drawString(100, height - 190, f"MAPE: {mape}%")

    c.drawString(100, height - 220, "Colunas usadas e seus tipos:")

    y_position = height - 250
    for column in df.columns:
        column_type = str(df.schema[column].dataType)
        c.drawString(100, y_position, f"{column}: {column_type}")
        y_position -= 20

    c.save()