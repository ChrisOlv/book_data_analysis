# version 1.1 pour ajouter la mise à jour incrémentale
# mise à jour incrémentale prête dans le notebook "analys_temporelle.ipynb", à partir de la cellule ### book_table
# y'a plus qu'à !

import time
# Start the timer
start_time = time.time()

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
import shutil
from datetime import datetime



### NEW CODE
# df_book_stale est la table originale et df_book_new est la table mise à jour

print("="*80)
print("let's go !")
print("="*80)

# 1. df_book_new
print("="*80)
print("chargement du fichier sqlite en cours")


# Chemin vers SQLite, depuis le répertoire "update"
database_path = "sqlite/update/statistics.sqlite3"


# Connexion à la base de données SQLite
conn = sqlite3.connect(database_path)

# Liste toutes les tables de la base de données
query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(query, conn)

# Charger une table de la base de données dans un df pandas
book = 'book'
df_book_new = pd.read_sql(f"SELECT * FROM {book};", conn)
page_stat_data = "page_stat_data"
df_page_stat_data = pd.read_sql(f"SELECT * FROM {page_stat_data};", conn)
# print le nombre de ligne de df_book_new
print("Nombre de lignes de df_book_new : ", df_book_new.shape[0])
# print le nombre de ligne de df_page_stat_data
print("Nombre de lignes de df_page_stat_data : ", df_page_stat_data.shape[0])

# fermer de la connexion à la base de données
conn.close()

# enrichissement du fichier source
df_book_new['oeuvre'] = df_book_new[['title', 'authors']].astype(str).agg(' - '.join, axis=1)
df_book_new['id long'] = df_book_new['id'].apply(lambda x: str(x).zfill(5))
# renaming des colonnes
df_book_new = df_book_new.rename(
    columns={'last_open':'Date dernière ouverture',
             "title":"Titre",
             "authors":"Auteurs",
             "series":"Série",
             "language":"Langue",
             "total_read_pages":"total Nbr de pages lues",
             "pages":"page"})
df_book_new['Date dernière ouverture'] = pd.to_datetime(df_book_new['Date dernière ouverture'], unit='s').dt.date
# créer la colonne "auteur courts"
df_book_new['Auteurs courts'] = (
    df_book_new['Auteurs']
    .str.replace(r'[.,]', ' ', regex=True)  # Remplace les points et virgules par des espaces
    .str.split()
    .apply(lambda x: ' '.join([word for word in x if len(word) > 2]))  # Garde les mots de plus de 2 caractères
    .str.split()
    .apply(lambda x: ' '.join(x[:2]))  # Garde les deux premiers mots
)

# ajout  colonne "format" = "ebook"
df_book_new['format'] = "ebook"
# ajout d'une colonne categorie vide 
df_book_new['First published date'] = ''
df_book_new['categorie'] = ''
df_book_new = df_book_new.drop(columns=['highlights', 'md5'])

print("chargement du fichier sqlite terminé")
print("="*80)

# 2. df_book_stale

# check si le fichier "data_sources_from_python/df_book.parquet" existe
# si oui, le charger dans df_book_stale
print("="*80)
print("chargement de la liste des livres existante en cours")

if os.path.exists("data_sources_from_python/df_book.parquet"):
    df_book_stale = pd.read_parquet("data_sources_from_python/df_book.parquet")
    # df_book_stale['oeuvre'] = df_book_stale[['Titre', 'Auteurs']].astype(str).agg(' - '.join, axis=1)
    # check si la colonne "First published date"    existe, sinon la créer
    if 'First published date' not in df_book_stale.columns:
        df_book_stale['First published date'] = ''

    print("liste des livres existante trouvées")
    # Comparer les 'id' pour identifier les nouvelles lignes
    df_increment = df_book_new[~df_book_new['id'].isin(df_book_stale['id'])]

    # Ajouter les nouvelles lignes à df_book_stale
    df_book_stale_concatenated = pd.concat([df_book_stale, df_increment], ignore_index=True)
    
    # Colonnes à mettre à jour
    update_columns = ['notes', 'Date dernière ouverture', 'total_read_time', 'total Nbr de pages lues']

    # Faire la jointure sur 'id' pour obtenir les lignes correspondantes de df_fake
    df_updated = df_book_stale_concatenated.merge(df_book_new[['id'] + update_columns], on='id', how='left', suffixes=('', '_fake'))

    # Remplacer les valeurs existantes par les valeurs de df_fake si elles existent
    for col in update_columns:
        df_updated[col] = df_updated[f'{col}_fake'].combine_first(df_updated[col])

    # Supprimer les colonnes temporaires (celles avec le suffixe "_fake")
    df_updated.drop(columns=[f'{col}_fake' for col in update_columns], inplace=True)

    nb_lignes_stale =  df_book_stale.shape[0]
    nb_lignes_updated = df_book_new.shape[0]

    # print le nombre de livre depuis la derniere mise à jour
    print("Nombre de livres ajoutés depuis la dernière mise à jour : ", nb_lignes_updated - nb_lignes_stale)

else: 
    df_updated = df_book_new
    nb_lignes_updated = df_book_new.shape[0]
    print(nb_lignes_updated,"livres ajoutés")





print("chargement de la liste des livres terminée")
print("="*80)

# GEN AI AJOUT DE LA CATEGORY : 
print("="*80)
print("génération des catégories avec gpt4o en cours ")
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

	
# fonction pour créer une colonne catégorie
def find_category(oeuvre):
    result = chain_category.invoke(oeuvre)
    return result

# print le nombre de ligne de df_updated dont la colonne 'categorie' est ""
nb_books_sans_categories = df_updated[(df_updated['categorie'] == '') | (pd.isna(df_updated['categorie']))].shape[0]

# si df_updated['categorie'] est vide, on applique la fonction find_category


df_updated['categorie'] = df_updated.apply(
    lambda row: find_category(row['oeuvre']) if pd.isna(row['categorie']) or row['categorie'] == '' else row['categorie'],
    axis=1
)


if nb_books_sans_categories == 0:
    print("aucun livre sans catégorie")

elif nb_books_sans_categories > 10:
    print("Nombre de livres sans catégorie : ", nb_books_sans_categories)

    print("10 derniers livres ajouté :",df_updated[['Titre', 'Auteurs', 'categorie']].tail(10))
else:
    print("Nombre de livres sans catégorie : ", nb_books_sans_categories)

    print(df_updated[['Titre', 'Auteurs', 'categorie']].tail(nb_books_sans_categories))

print("génération des catégories avec gpt4o terminée")
print("="*80)
# df_updated = df_updated.drop(columns=['oeuvre'])



# Générer les années de publication
print("="*80)
print("génération des années de publication avec gpt4o en cours ")

prompt_annee_edition = """
en utilisant tes connaissances, trouve la date de première parution de l'oeuvre dans sa version originale. (parfois appelée First published date).
N'ajoute rien d'autre.
Le format doit être AAAA.

question: {oeuvre} 

catégorie:"""
prompt = PromptTemplate.from_template(prompt_annee_edition)

# langchain :
chain_first_published_date = (
    {"oeuvre": RunnablePassthrough()}
    | prompt
    | llm_gpt4o
    | StrOutputParser()
)

	

def first_published_date(oeuvre):
    result = chain_first_published_date.invoke(oeuvre)
    return result


# check si la colonne "First published date"    existe, sinon la créer
if 'First published date' not in df_updated.columns:
    df_updated['First published date'] = ''


nb_books_sans_année = df_updated[(df_updated['First published date'] == '') | (pd.isna(df_updated['First published date']))].shape[0]

df_updated['First published date'] = df_updated.apply(
    lambda row: first_published_date(row['oeuvre']) if pd.isna(row['First published date']) or row['First published date'] == '' else row['First published date'],
    axis=1
)


if nb_books_sans_année == 0:
    print("aucun livre sans année de publication")

elif nb_books_sans_année > 10:
    print("Nombre d'années de publication à générer : ", nb_books_sans_année)

    print("10 derniers livres :",df_updated[['Titre', 'Auteurs', 'First published date']].tail(10))
    
else:
    print("Nombre d'années de publication à générer : ", nb_books_sans_année)

    print(df_updated[['Titre', 'Auteurs', 'First published date']].tail(nb_books_sans_année))

print("génération des années de publication avec gpt4o terminée ")
print("="*80)


# Exporter la tables vers un fichier Parquet
df_updated.to_parquet('data_sources_from_python/df_book.parquet',engine='pyarrow')





print("="*80)
print("récupération des stats lecture en cours")
nb_lignes_stat_updated = df_page_stat_data.shape[0]

if os.path.exists("data_sources_from_python/stats_lecture.parquet"):
    df_stat_stale = pd.read_parquet("data_sources_from_python/stats_lecture.parquet")
    nb_lignes_stat_stale =  df_stat_stale.shape[0]

    # print le nombre de logs depuis la derniere mise à jour
    print("Nombre de sessions de lecture ajoutées depuis la dernière mise à jour : ", nb_lignes_stat_updated - nb_lignes_stat_stale)

else:
    

    print(nb_lignes_stat_updated,"sessions de lecture ajoutées")



# nettoyage et preparation de df_stat 

# changer le nom de la coonne duration pour "Temps passé sur la page en seconde"
df_page_stat_data.rename(columns={"duration":"Temps passé sur la page en seconde"},inplace=True)
# convertir la colonne en date time
df_page_stat_data.rename(columns={"start_time":"heure de début"},inplace=True)

df_page_stat_data['heure de début'] = pd.to_datetime(df_page_stat_data['heure de début'], unit='s')
# créé une colonne "id long" qui reprend la colonne "id_book" en la passant sur 5 chiffres. Les premiers chiffres doivent etre des "0". par exemple "68" devient "00068"
df_page_stat_data['id_long'] = df_page_stat_data['id_book'].apply(lambda x: str(x).zfill(5))
# crée une colonne "Temps de lecture en minute" et "Temps de lecture en heure" qui utilise la colonne "Temps passé sur la page en seconde", divisé par 60 puis encore par 603
df_page_stat_data['Temps de lecture en minute'] = df_page_stat_data['Temps passé sur la page en seconde'] / 60
df_page_stat_data['Temps de lecture en heure'] = df_page_stat_data['Temps de lecture en minute'] / 60
# ajoute une colonne "date lecture" qui reprend la date de la colonne "heure de début"
df_page_stat_data['date lecture'] = df_page_stat_data['heure de début'].dt.date
# ajoute une colonne "Heure de début de lecture" qui reprend l'heure de la colonne "heure de début" 
df_page_stat_data['Heure de début de lecture'] = df_page_stat_data['heure de début'].dt.time
# ajoute les colonnes : Heure,	Heure en décimal, Jour Précédent. basée sur la colonne heure de début 
df_page_stat_data['Heure'] = df_page_stat_data['heure de début'].dt.hour
df_page_stat_data['Heure en décimal'] = df_page_stat_data['Heure'] + df_page_stat_data['heure de début'].dt.minute / 60
df_page_stat_data['Jour Précédent'] = (df_page_stat_data['heure de début'] - pd.Timedelta(days=1)).dt.date
# ajoute une colonne "Est Consécutif" 
df_page_stat_data['Est Consécutif'] = (df_page_stat_data['date lecture'].shift(1) == df_page_stat_data['date lecture']) | (df_page_stat_data['date lecture'].shift(1) == df_page_stat_data['date lecture'] - pd.Timedelta(days=1))
df_page_stat_data['date de fin de lecture'] = df_page_stat_data.groupby('id_book')['date lecture'].transform('max')

# Exporter la tables vers un fichier Parquet
df_page_stat_data.to_parquet('data_sources_from_python/stats_lecture.parquet', engine='pyarrow')



# Afficher les premières lignes du DataFrame
print("dernières stats lecture :")
print(df_page_stat_data.tail(2))
print("récupération des stats lecture terminée")
print("="*80)







print("="*80)
print("archivage fichier sqlite en cours")





# Définir les chemins des dossiers et du fichier
folder_update_path = "sqlite/update"
folder_archive_path = "sqlite/archive"
sqlite_update_path = os.path.join(folder_update_path, "statistics.sqlite3")

# Vérifier si le fichier existe dans le dossier de mise à jour
if os.path.exists(sqlite_update_path):
    # Générer un horodatage dans le format souhaité (exemple : YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construire le nouveau nom de fichier avec l'horodatage
    new_filename = f"statistics_{timestamp}.sqlite3"
    new_filepath = os.path.join(folder_archive_path, new_filename)
    
    # Déplacer et renommer le fichier vers le dossier archive
    shutil.move(sqlite_update_path, new_filepath)
    print(f"Fichier déplacé et renommé en {new_filename}")
    # Compter le nombre de fichiers dans le dossier archive
    num_files = len([name for name in os.listdir(folder_archive_path) if os.path.isfile(os.path.join(folder_archive_path, name))])
    if num_files > 3:
        # Afficher le message avec le nombre de fichiers
        print(f"Il y a {num_files} fichiers de sauvegarde, pense à faire du ménage, tu vas pas garder 2000 sauvegardes, tu payes pas tes bytes ou quoi ?")

    
else:
    print(f"Aucun fichier trouvé à l'emplacement : {sqlite_update_path}")




# End the timer
end_time = time.time()

# Calculate and print the execution time
execution_time = end_time - start_time
print("="*80)

print("update terminée")
print(f"Execution time total : {execution_time} seconds")
print("="*80)