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
print(df_book.head())
print("-------------")

print("df_page_stat_data")
print(df_page_stat_data.head())
print("-------------")

# Clôture de la connexion à la base de données
conn.close()

# Exporter les tables vers des fichiers Parquet
df_book.to_parquet('data_sources_from_python/book_table.parquet')
df_page_stat_data.to_parquet('data_sources_from_python/stats_lecture.parquet')

# Afficher un message de confirmation
print("Les tables ont été mises à jour !")