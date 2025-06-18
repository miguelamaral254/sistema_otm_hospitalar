import os
from pyspark.sql.functions import col, abs, sum as spark_sum
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def processar_influenza(spark):
    file_path = "src/data/processed/influenza_hospitalar_processed.parquet"
    df = spark.read.parquet(file_path)

    months_columns = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    feature_columns = [col for col in df.columns if col not in ['uf', 'ano']]

    for column in feature_columns:
        df = df.withColumn(column, col(column).cast("int"))

    assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features"
    )
    df = assembler.transform(df)

    label_col = "ano"

    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)

    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    lr_model = lr.fit(train_data)

    avaliar_modelo(lr_model, test_data, df)

def avaliar_modelo(lr_model, test_data, df):
    predictions = lr_model.transform(test_data)

    evaluator_rmse = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="ano", predictionCol="prediction", metricName="mae")
    
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    mape = predictions.withColumn("error", abs(col("prediction") - col("ano")))
    mape = mape.withColumn("percent_error", (col("error") / col("ano")) * 100)
    mape_value = mape.agg({"percent_error": "avg"}).collect()[0][0]

    uf_stats, max_month = analyze_seasonality_and_uf(df)
    generate_pdf(rmse, mae, mape_value, df, uf_stats, max_month)

def analyze_seasonality_and_uf(df):
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_names = {
        "jan": "Janeiro", "feb": "Fevereiro", "mar": "Março", "apr": "Abril",
        "may": "Maio", "jun": "Junho", "jul": "Julho", "aug": "Agosto",
        "sep": "Setembro", "oct": "Outubro", "nov": "Novembro", "dec": "Dezembro"
    }
    
    # Calcula o total de internações por mês para cada UF
    total_per_uf = df.groupBy("uf").agg(
        *[spark_sum(col(month)).alias(month) for month in months],
        spark_sum(sum([col(month) for month in months])).alias("total_internacoes")
    )
    
    # Converte para Pandas para processamento mais fácil
    pdf = total_per_uf.toPandas()
    
    # Encontra o mês com maior número de internações para cada UF
    uf_stats = []
    for _, row in pdf.iterrows():
        max_val = 0
        max_month = ""
        for month in months:
            if row[month] > max_val:
                max_val = row[month]
                max_month = month_names[month]
        
        uf_stats.append({
            "uf": row["uf"],
            "total_internacoes": row["total_internacoes"],
            "mes_maior_internacoes": max_month,
            "valor_maior_mes": max_val
        })
    
    # Calcula o total de internações por mês em todos os estados
    max_month_data = df.select(*[spark_sum(col(month)).alias(month) for month in months]).first()
    
    # Encontra o mês com maior número de internações no geral
    max_month_name = None
    max_month_value = 0
    for month in months:
        value = max_month_data[month]
        if value > max_month_value:
            max_month_value = value
            max_month_name = month_names[month]
    
    return uf_stats, {"month": max_month_name, "value": max_month_value}

def generate_pdf(rmse, mae, mape, df, uf_stats, max_month):
    pdf_filename = "artifacts/resultados_modelo_influenza.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "Resultados do Modelo de Previsão de Internações por Influenza")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 80, "Métricas do Modelo:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 100, f"RMSE: {rmse:.2f}")
    c.drawString(100, height - 120, f"MAE: {mae:.2f}")
    c.drawString(100, height - 140, f"MAPE: {mape:.2f}%")

    # Análise de Sazonalidade
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 170, "Análise de Sazonalidade:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 190, f"Mês com maior número de internações no geral: {max_month['month']} com {max_month['value']} casos")
    
    # Estatísticas por Estado
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 220, "Estatísticas por Estado (Mês com maior número de internações):")
    
    y_position = height - 240
    for uf in sorted(uf_stats, key=lambda x: x["total_internacoes"], reverse=True):
        if y_position < 100:  # Verifica se ainda há espaço na página
            c.showPage()  # Cria nova página
            y_position = height - 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y_position, "Estatísticas por Estado (continuação):")
            y_position -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(100, y_position, f"{uf['uf']}: {uf['total_internacoes']} internações no total")
        c.drawString(300, y_position, f"Mês com pico: {uf['mes_maior_internacoes']} ({uf['valor_maior_mes']} casos)")
        y_position -= 20

    # Colunas usadas
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position - 20, "Colunas usadas e seus tipos:")
    y_position -= 40

    for column in df.columns:
        if y_position < 100:
            c.showPage()
            y_position = height - 50
        column_type = str(df.schema[column].dataType)
        c.setFont("Helvetica", 10)
        c.drawString(100, y_position, f"{column}: {column_type}")
        y_position -= 15

    c.save()