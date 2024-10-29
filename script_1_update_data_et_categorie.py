import subprocess
import sys
import sqlite3
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import find_dotenv, load_dotenv


# ETAPE 1/3
# Charger les tables de la base de données SQLite


# Chemin vers SQLite
database_path = 'sqlite/statistics.sqlite3'

# Connexion à la base de données SQLite
conn = sqlite3.connect(database_path)

# Liste toutes les tables de la base de données
query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(query, conn)
print("Tables in the database:", tables)

# Charger une table de la base de données dans un df pandas
book = 'book'
page_stat_data = "page_stat_data"
df_book = pd.read_sql(f"SELECT * FROM {book};", conn)
df_page_stat_data = pd.read_sql(f"SELECT * FROM {page_stat_data};", conn)

# Afficher les dernières lignes des df
print("book")
print(df_book.tail())
print(df_book.shape)
print("-"*50)

print("df_page_stat_data")
print(df_page_stat_data.tail())
print(df_page_stat_data.shape)
print("-"*50)

# fermer de la connexion à la base de données
conn.close()

print("="*80)
print("Etape 1/3 : Les tables ont été chargées !")
print("="*80)

# ETAPE 2/3
# AJOUT DE LA CATEGORY : 

# load env
load_dotenv()
OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
AZURE_OPENAI_ENDPOINT= os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

llm_gpt4o = AzureChatOpenAI(deployment_name="gpt4o",api_key=AZURE_OPENAI_API_KEY,api_version= "2024-02-01",temperature=0)

prompt = """
en utilisant tes connaissances, classe l'oeuvre dans une des catégories suivantes : 

fiction/SF
fiction/fantasy
fiction/fantastique

non-fiction/lifestyle
non-fiction/parenting
non-fiction/histoire
non-fiction/santé

si aucune des catégories ne convient, tu peux en générer une autre, en gardant la même structure (en commençant toujours par fiction ou non-fiction).
n'ajoute rien d'autre.

exemples : 
harry potter et la chambre des secrets - JK Rowling = fiction/fantastique
Blackwater 1 - La crue - Michael McDowell = fiction/fantastique

question: {oeuvre} 

catégorie:"""
rag_prompt_1 = PromptTemplate.from_template(prompt)

# langchain :
chain_category = (
    {"oeuvre": RunnablePassthrough()}
    | rag_prompt_1
    | llm_gpt4o
    | StrOutputParser()
)

# ETAPE 2/3 suite
# nettoyage et préparation de df_book

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

# Afficher un message de confirmation
print("="*80)
print("Etape 2/3 : Les catégories ont été ajoutées !")

# Afficher les premières lignes du DataFrame
print("book avec catégories :")
print(df_book[['title', 'authors', 'categorie']].tail(5))
print("="*80)

# nettoyage et preparation de df_stat 

# changer le nom de la coonne duration pour "Temps passé sur la page en seconde"
df_page_stat_data.rename(columns={"duration":"Temps passé sur la page en seconde"},inplace=True)
# convertir la colonne en date time
df_page_stat_data['start_time'] = pd.to_datetime(df_page_stat_data['start_time'], unit='s')
# créé une colonne "id long" qui reprend la colonne "id_book" en la passant sur 5 chiffres. Les premiers chiffres doivent etre des "0". par exemple "68" devient "00068"
df_page_stat_data['id_long'] = df_page_stat_data['id_book'].apply(lambda x: str(x).zfill(5))
# crée une colonne "Temps de lecture en minute" et "Temps de lecture en heure" qui utilise la colonne "Temps passé sur la page en seconde", divisé par 60 puis encore par 603
df_page_stat_data['Temps de lecture en minute'] = df_page_stat_data['Temps passé sur la page en seconde'] / 60
df_page_stat_data['Temps de lecture en heure'] = df_page_stat_data['Temps de lecture en minute'] / 60
# ajoute une colonne "date lecture" qui reprend la date de la colonne "start_time"
df_page_stat_data['date lecture'] = df_page_stat_data['start_time'].dt.date
# ajoute une colonne "Heure de début de lecture" qui reprend l'heure de la colonne "start_time" 
df_page_stat_data['Heure de début de lecture'] = df_page_stat_data['start_time'].dt.time
# ajoute les colonnes : Heure,	Heure en décimal, Jour Précédent. basée sur la colonne start_time 
df_page_stat_data['Heure'] = df_page_stat_data['start_time'].dt.hour
df_page_stat_data['Heure en décimal'] = df_page_stat_data['Heure'] + df_page_stat_data['start_time'].dt.minute / 60
df_page_stat_data['Jour Précédent'] = (df_page_stat_data['start_time'] - pd.Timedelta(days=1)).dt.date
# ajoute une colonne "Est Consécutif" 
df_page_stat_data['Est Consécutif'] = (df_page_stat_data['date lecture'].shift(1) == df_page_stat_data['date lecture']) | (df_page_stat_data['date lecture'].shift(1) == df_page_stat_data['date lecture'] - pd.Timedelta(days=1))


# Afficher un message de confirmation
print("="*80)
print("Etape 3/3 : Les stats data ont été nettoyées !")
df_page_stat_data.to_parquet('data_sources_from_python/stats_lecture.parquet')

# Afficher les premières lignes du DataFrame
print("stats data :")
print(df_page_stat_data.tail(10))
print("="*80)