# vacina_ml_pipeline.py
import os
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col, abs

def processar_vacinas():
    spark = SparkSession.builder \
        .appName("ProcessarDosesVacinasML") \
        .master("local[*]") \
        .getOrCreate()

    # Carregar o arquivo .parquet
    file_path = "src/data/processed/doses_vacinas_processed.parquet"
    df = spark.read.parquet(file_path)

    # Preparar os dados
    assembler = VectorAssembler(
        inputCols=["primeira_dose", "segunda_dose", "dose_unica"], 
        outputCol="features"
    )
    df = assembler.transform(df)
    
    # Dividir os dados em treino e teste
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    # Modelo de regressão linear
    lr = LinearRegression(featuresCol="features", labelCol="total_doses")
    lr_model = lr.fit(train_data)

    # Avaliar o modelo
    avaliar_modelo(lr_model, test_data)

    # Finaliza a sessão Spark
    spark.stop()

def avaliar_modelo(lr_model, test_data):
    # Fazer previsões
    predictions = lr_model.transform(test_data)

    # Avaliar o modelo usando RMSE, MAE, MAPE
    evaluator_rmse = RegressionEvaluator(labelCol="total_doses", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="total_doses", predictionCol="prediction", metricName="mae")
    
    # Calcular RMSE e MAE
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    # Calcular MAPE (Mean Absolute Percentage Error)
    mape = predictions.withColumn("error", abs(col("prediction") - col("total_doses")))
    mape = mape.withColumn("percent_error", (col("error") / col("total_doses")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    # Exibir as métricas
    print(f"RMSE: {rmse}")
    print(f"MAE: {mae}")
    print(f"MAPE: {mape_value}%")

if __name__ == "__main__":
    processar_vacinas()