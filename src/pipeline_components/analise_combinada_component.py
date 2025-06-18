from pyspark.sql.functions import col, sum as spark_sum, greatest, when, round
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from pyspark.sql import functions as F
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

def calculate_rmse_mae_mape(predictions, label_col='label', prediction_col='prediction'):
    evaluator_rmse = RegressionEvaluator(labelCol=label_col, predictionCol=prediction_col, metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol=label_col, predictionCol=prediction_col, metricName="mae")
    predictions = predictions.withColumn("abs_error", F.abs(F.col(label_col) - F.col(prediction_col)))
    predictions = predictions.withColumn("abs_percentage_error", F.col("abs_error") / F.col(label_col) * 100)
    mape = predictions.agg(F.avg("abs_percentage_error")).collect()[0][0]
    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)
    return rmse, mae, mape

def analyze_capacity_and_influenza(spark):
    df_influenza = spark.read.parquet("src/data/processed/influenza_hospitalar_processed.parquet")
    df_leitos = spark.read.parquet("src/data/processed/leitos_sus_nao_sus_processed.parquet")
    
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_names = {m: nome[:3] for m, nome in zip(months, [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    ])}
    
    internacoes_por_uf = df_influenza.groupBy("uf").agg(
        *[spark_sum(col(month)).alias(month) for month in months],
        spark_sum(sum([col(month) for month in months])).alias("total_internacoes")
    )
    
    leitos_por_uf_sus = df_leitos.groupBy("uf").agg(
        spark_sum("quantidade_sus").alias("leitos_sus")
    )
    
    leitos_por_uf_nao_sus = df_leitos.groupBy("uf").agg(
        spark_sum("quantidade_nao_sus").alias("leitos_nao_sus")
    )
    
    analise_completa_sus = internacoes_por_uf.join(leitos_por_uf_sus, "uf", "inner") \
        .withColumn("leitos_totais_sus", col("leitos_sus")) \
        .withColumn("relacao_pico_leitos_sus", 
                   round(greatest(*[col(month) for month in months]) / col("leitos_totais_sus"), 2)) \
        .withColumn("situacao_sus",
                   when(col("relacao_pico_leitos_sus") > 1, "CRÍTICO")
                   .when(col("relacao_pico_leitos_sus") > 0.7, "ALERTA")
                   .otherwise("OK"))
    
    analise_completa_nao_sus = internacoes_por_uf.join(leitos_por_uf_nao_sus, "uf", "inner") \
        .withColumn("leitos_totais_nao_sus", col("leitos_nao_sus")) \
        .withColumn("relacao_pico_leitos_nao_sus", 
                   round(greatest(*[col(month) for month in months]) / col("leitos_totais_nao_sus"), 2)) \
        .withColumn("situacao_nao_sus",
                   when(col("relacao_pico_leitos_nao_sus") > 1, "CRÍTICO")
                   .when(col("relacao_pico_leitos_nao_sus") > 0.7, "ALERTA")
                   .otherwise("OK"))
    
    assembler_sus = VectorAssembler(inputCols=months, outputCol="features")
    analise_completa_sus = assembler_sus.transform(analise_completa_sus)
    
    assembler_nao_sus = VectorAssembler(inputCols=months, outputCol="features")
    analise_completa_nao_sus = assembler_nao_sus.transform(analise_completa_nao_sus)
    
    lr_sus = LinearRegression(featuresCol="features", labelCol="total_internacoes", predictionCol="predicted_internacoes_sus")
    lr_model_sus = lr_sus.fit(analise_completa_sus)
    analise_completa_sus = lr_model_sus.transform(analise_completa_sus)
    
    lr_nao_sus = LinearRegression(featuresCol="features", labelCol="total_internacoes", predictionCol="predicted_internacoes_nao_sus")
    lr_model_nao_sus = lr_nao_sus.fit(analise_completa_nao_sus)
    analise_completa_nao_sus = lr_model_nao_sus.transform(analise_completa_nao_sus)
    
    rmse_sus, mae_sus, mape_sus = calculate_rmse_mae_mape(analise_completa_sus, label_col='total_internacoes', prediction_col='predicted_internacoes_sus')
    rmse_nao_sus, mae_nao_sus, mape_nao_sus = calculate_rmse_mae_mape(analise_completa_nao_sus, label_col='total_internacoes', prediction_col='predicted_internacoes_nao_sus')

    pdf_data_sus = analise_completa_sus.toPandas()
    pdf_data_nao_sus = analise_completa_nao_sus.toPandas()
    
    uf_stats = []
    
    for _, row in pdf_data_sus.iterrows():
        max_month_val = max([row[month] for month in months])
        max_month = months[[row[month] for month in months].index(max_month_val)]
        uf_stats.append({
            "uf": row["uf"],
            "total_internacoes": row["total_internacoes"],
            "mes_pico": month_names[max_month],
            "internacoes_pico": max_month_val,
            "leitos_sus": row["leitos_sus"],
            "leitos_totais": row["leitos_totais_sus"],
            "relacao_pico_leitos": row["relacao_pico_leitos_sus"],
            "situacao": row["situacao_sus"],
            "rmse": rmse_sus,
            "mae": mae_sus,
            "mape": mape_sus
        })
    
    for _, row in pdf_data_nao_sus.iterrows():
        max_month_val = max([row[month] for month in months])
        max_month = months[[row[month] for month in months].index(max_month_val)]
        uf_stats.append({
            "uf": row["uf"],
            "total_internacoes": row["total_internacoes"],
            "mes_pico": month_names[max_month],
            "internacoes_pico": max_month_val,
            "leitos_nao_sus": row["leitos_nao_sus"],
            "leitos_totais": row["leitos_totais_nao_sus"],
            "relacao_pico_leitos": row["relacao_pico_leitos_nao_sus"],
            "situacao": row["situacao_nao_sus"],
            "rmse": rmse_nao_sus,
            "mae": mae_nao_sus,
            "mape": mape_nao_sus
        })
    
    generate_combined_pdf(uf_stats)

def generate_combined_pdf(uf_stats):
    pdf_filename = "artifacts/resultados_combinados_influenza_leitos_separados.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "Análise Combinada: Internações por Influenza e Capacidade de Leitos (Separados por SUS e Não SUS)")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 80, "Situação por Estado - Leitos SUS:")
    y_position = height - 110
    for uf in sorted(uf_stats, key=lambda x: x["relacao_pico_leitos"], reverse=True):
        if y_position < 100:
            c.showPage()
            y_position = height - 50
        if "leitos_sus" in uf:
            if uf["situacao"] == "CRÍTICO":
                c.setFillColor(colors.red)
            elif uf["situacao"] == "ALERTA":
                c.setFillColor(colors.orange)
            else:
                c.setFillColor(colors.green)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_position, f"{uf['uf']} - Situação: {uf['situacao']}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            c.drawString(100, y_position - 20, f"Leitos Totais: {uf['leitos_totais']}")
            c.drawString(100, y_position - 40, f"Internações no pico ({uf['mes_pico']}): {uf['internacoes_pico']}")
            c.drawString(100, y_position - 60, f"Relação Internações/Leitos: {uf['relacao_pico_leitos']}")
            y_position -= 90

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, "Situação por Estado - Leitos Não SUS:")
    y_position -= 30
    for uf in sorted(uf_stats, key=lambda x: x["relacao_pico_leitos"], reverse=True):
        if y_position < 100:
            c.showPage()
            y_position = height - 50
        if "leitos_nao_sus" in uf:
            if uf["situacao"] == "CRÍTICO":
                c.setFillColor(colors.red)
            elif uf["situacao"] == "ALERTA":
                c.setFillColor(colors.orange)
            else:
                c.setFillColor(colors.green)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_position, f"{uf['uf']} - Situação: {uf['situacao']}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            c.drawString(100, y_position - 20, f"Leitos Totais: {uf['leitos_totais']}")
            c.drawString(100, y_position - 40, f"Internações no pico ({uf['mes_pico']}): {uf['internacoes_pico']}")
            c.drawString(100, y_position - 60, f"Relação Internações/Leitos: {uf['relacao_pico_leitos']}")
            y_position -= 90

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, f"RMSE: {uf_stats[0]['rmse']}")
    c.drawString(100, y_position - 20, f"MAE: {uf_stats[0]['mae']}")
    c.drawString(100, y_position - 40, f"MAPE: {uf_stats[0]['mape']}")
    
    c.save()