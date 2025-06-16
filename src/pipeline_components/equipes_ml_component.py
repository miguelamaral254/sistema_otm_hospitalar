from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col, abs
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def processar_equipes(spark):
    # Caminho do arquivo das equipes
    file_path = "src/data/processed/equipes_saude_processed.parquet"
    df = spark.read.parquet(file_path)

    # Seleciona todas as colunas de equipes, exceto 'UF' e 'Ano'
    team_columns = [col for col in df.columns if col not in ['uf', 'ano']]

    # Converter todas as colunas de equipes para int (substituir valores não numéricos por 0)
    for column in team_columns:
        df = df.withColumn(column, col(column).cast("int"))

    # Usando essas colunas de equipes para criar as features
    assembler = VectorAssembler(
        inputCols=team_columns, 
        outputCol="features"
    )
    df = assembler.transform(df)

    # A coluna de 'ano' será usada como exemplo, mas pode ser trocada por qualquer outra coluna que você deseja analisar
    label_col = "ano"  # Alterar para uma coluna relevante conforme necessário

    # Dividir os dados em treino e teste
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    # Modelo de Regressão Linear
    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    lr_model = lr.fit(train_data)

    # Avaliar o modelo
    avaliar_modelo(lr_model, test_data)

def avaliar_modelo(lr_model, test_data):
    predictions = lr_model.transform(test_data)

    # Avaliação usando RMSE, MAE e MAPE
    evaluator_rmse = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="mae")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    mape = predictions.withColumn("error", abs(col("prediction") - col("ano")))
    mape = mape.withColumn("percent_error", (col("error") / col("ano")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    # Gerar o PDF com os resultados
    generate_pdf(rmse, mae, mape_value)

def generate_pdf(rmse, mae, mape):
    pdf_filename = "artifacts/resultados_modelo_equipes.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    
    c.drawString(100, height - 100, "Resultados do Modelo de Previsão das Equipes de Saúde")

    c.drawString(100, height - 130, f"RMSE: {rmse}")
    c.drawString(100, height - 160, f"MAE: {mae}")
    c.drawString(100, height - 190, f"MAPE: {mape}%")

    c.save()