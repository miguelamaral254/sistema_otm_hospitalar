import os
from pyspark.sql.functions import col, abs
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def processar_leitos_sus_nao_sus(spark):
    file_path = "src/data/processed/leitos_sus_nao_sus_processed.parquet"
    df = spark.read.parquet(file_path)

    team_columns = [col for col in df.columns if col not in ['uf', 'ano']]

    for column in team_columns:
        df = df.withColumn(column, col(column).cast("int"))

    assembler = VectorAssembler(
        inputCols=team_columns,
        outputCol="features"
    )
    df = assembler.transform(df)

    label_col = "ano"

    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    lr_model = lr.fit(train_data)

    avaliar_modelo(lr_model, test_data)

def avaliar_modelo(lr_model, test_data):
    predictions = lr_model.transform(test_data)

    evaluator_rmse = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="mae")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    mape = predictions.withColumn("error", abs(col("prediction") - col("ano")))
    mape = mape.withColumn("percent_error", (col("error") / col("ano")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    generate_pdf(rmse, mae, mape_value)

def generate_pdf(rmse, mae, mape):
    pdf_filename = "artifacts/resultados_modelo_leitos.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    
    c.drawString(100, height - 100, "Resultados do Modelo de Previsão de Leitos SUS e Não SUS")

    c.drawString(100, height - 130, f"RMSE: {rmse}")
    c.drawString(100, height - 160, f"MAE: {mae}")
    c.drawString(100, height - 190, f"MAPE: {mape}%")

    c.save()