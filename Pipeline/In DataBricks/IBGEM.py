# Databricks notebook source
import json
import requests
from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC **Lendo os dados do Mongo DB**

# COMMAND ----------

# DBTITLE 0,Lendo os dados do Mongo DB
uri = "mongodb+srv://estudante_igti:SRwkJTDz2nA28ME9@unicluster.ixhvw.mongodb.net/ibge.pnadc20203?retryWrites=true&w=majority"
 
ibge_mongo = spark.read.format("mongo")\
                  .option("uri", uri)\
                  .load()

# COMMAND ----------

ibge_mongo.printSchema()
# ibge_mongo.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC **Definindo as funções suportes que irão parsear o json object e transforma-lo em dataframe**

# COMMAND ----------

def convert_single_object_per_line(json_list):
    json_string = ""
    for line in json_list:
        json_string += json.dumps(line) + "\n"
    return json_string
 
def parse_dataframe(json_data):
    r = convert_single_object_per_line(json_data)
    mylist = []
    for line in r.splitlines():
        mylist.append(line)
    rdd = sc.parallelize(mylist)    
    df = spark.read.json(rdd)
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC **Criando o dataframe a partir da API**

# COMMAND ----------

url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/31/mesorregioes'
r =  requests.get(url)
j = r.json()
ibge_api = parse_dataframe(j)

# COMMAND ----------

ibge_api.printSchema()
ibge_api.show(truncate=False)

# COMMAND ----------

ibge_mongo.write.parquet("/FileStore/ibge-mongo", mode="overwrite")
ibge_api.write.parquet("/FileStore/ibge-api", mode="overwrite")

# COMMAND ----------

ibge_mongo = spark.read.parquet("/FileStore/ibge-mongo")\
                  .filter((col("sexo")=="Mulher")&(col("idade")>=20)&(col("idade")<=40))

# COMMAND ----------

ibge_api = spark.read.parquet("/FileStore/ibge-api")

# COMMAND ----------

ibge_mongo.first()

# COMMAND ----------

# MAGIC %md
# MAGIC **What is the average income of the women between 20 and 40 years old in your database?**

# COMMAND ----------

display(ibge_mongo.agg({"renda": "avg"}).select(format_number('avg(renda)', 2).alias('Average income')).collect())


# COMMAND ----------

# MAGIC %md
# MAGIC **What is the average income of the women between 20 and 40 years in 'Distrito Federal'?**

# COMMAND ----------

display(ibge_mongo.filter("uf = 'Distrito Federal'").agg({"renda": "avg"}).select(format_number('avg(renda)', 2).alias('Average income in DF')).collect())

# COMMAND ----------


