import subprocess
import sys
import sqlite3
import pandas as pd


# Chemin vers SQLite
database_path = 'sqlite/statistics.sqlite3'

# Connexion à la base de données SQLite
conn = sqlite3.connect(database_path)

# Liste toutes les tables de la base de données
query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(query, conn)
print("Tables in the database:", tables)

# Charger une table de la base de données dans un DataFrame pandas
book = 'book'
page_stat_data = "page_stat_data"
df_book = pd.read_sql(f"SELECT * FROM {book};", conn)
df_page_stat_data = pd.read_sql(f"SELECT * FROM {page_stat_data};", conn)

# Afficher les premières lignes du DataFrame
print("book")
print(df_book.tail())
print(df_book.shape)
print("-------------")

print("df_page_stat_data")
print(df_page_stat_data.tail())
print(df_page_stat_data.shape)
print("-------------")

# Clôture de la connexion à la base de données
conn.close()

# test

# Afficher un message de confirmation
print("Les tables ont été mises à jour !")


# AJOUT DE LA CATEGORY (WIP) : 


from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import find_dotenv, load_dotenv


# load env
load_dotenv()
OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
AZURE_OPENAI_ENDPOINT= os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

llm_gpt4o = AzureChatOpenAI(
    deployment_name="gpt4o",api_key=AZURE_OPENAI_API_KEY,api_version= "2024-02-01",
        temperature=0)


# prompt
template_1 = """
en utilisant tes connaissances, classe l'oeuvre dans une des catégories suivantes : 

fiction/SF
fiction/fantasy
fiction/fantastique

non-fiction/lifestyle
non-fiction/parenting
non-fiction/histoire
non-fiction/santé

si aucune des catégories ne convient, tu peux générer une autre, en gardant la même structure (en commençant par fiction ou non-fiction).
n'ajoute rien d'autre.

exemple : 
harry potter et la chambre des secrets - JK Rowling = fiction/fantastique

question: {oeuvre} 

catégorie:"""
rag_prompt_1 = PromptTemplate.from_template(template_1)

# chain générative
chain_category = (
    {"oeuvre": RunnablePassthrough()}
    | rag_prompt_1
    | llm_gpt4o
    | StrOutputParser()
)


# enrichissement du excel source
df_book['oeuvre'] = df_book[['title', 'authors']].astype(str).agg(' - '.join, axis=1)

# fonction pour créer une colonne avec un résumé de la question. Servira à gagner en lisibilité sur les visuels
def find_category(oeuvre):
    result = chain_category.invoke(oeuvre)
    return result

df_book['categorie'] = df_book['oeuvre'].apply(find_category)
df_book = df_book.drop(columns=['oeuvre', 'md5'])

# Exporter les tables vers des fichiers Parquet
df_book.to_parquet('data_sources_from_python/book_table.parquet')
df_page_stat_data.to_parquet('data_sources_from_python/stats_lecture.parquet')

# Afficher un message de confirmation
print("Les catégories ont été ajoutées")

# Afficher les premières lignes du DataFrame
print("book avec catégories")
print(df_book.tail(10))
print("-------------")