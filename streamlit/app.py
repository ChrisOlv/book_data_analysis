import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(layout='wide', initial_sidebar_state='expanded')


df_table = pd.read_parquet('../dataviz/df_book_visuel1_table.parquet')
# filtre du df
# compter le nombre de livres avec pourcentage lu inférieur à 60%

df_abandon = df_table[df_table['% lu'] < 60]
nb_livre_abandon = df_abandon.shape[0]

# uniquement 2024
df_table = df_table[df_table['Date de lecture'].astype(str).str.startswith('2024')]
# uniquement les livres lus à plus de 90 percent
df_table = df_table[df_table['% lu'] > 60]

st.header("nombre de livres par catégorie")
# sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 6))
ax = sns.countplot(y='Catégorie', data=df_table, order=df_table['Catégorie'].value_counts().index)
plt.title('Nombre de livres par catégorie')
plt.xlabel('Nombre de livres')
plt.ylabel('Catégorie')
plt.show()

st.pyplot(ax.figure)


st.header("nombre de livres lus")
# compter le nombre de ligne du df
nb_livre = df_table.shape[0]
st.markdown(f"Nombre de livres lus en 2024 : {nb_livre}")
st.markdown(f"Nombre de livres abandonnés en 2024 : {nb_livre_abandon}")

st.header("Tableau des livres")
st.table(df_table)


st.header("plus longue lecture")
#trouver le titre avec la durée de lecture la plus grande
# df_table[df_table["Temps de lecture total (hh:mm:ss)"] == df_table["Temps de lecture total (hh:mm:ss)"].max()]

# enregistrer dans la variable titre_max_temps_lecture et temps_max_lecture, auteur_max_temps_lecture
titre_max_temps_lecture = df_table[df_table["Temps de lecture total (hh:mm:ss)"] == df_table["Temps de lecture total (hh:mm:ss)"].max()]["Titre"].values[0]
auteur_max_temps_lecture = df_table[df_table["Temps de lecture total (hh:mm:ss)"] == df_table["Temps de lecture total (hh:mm:ss)"].max()]["Auteurs"].values[0]
temps_max_lecture = df_table["Temps de lecture total (hh:mm:ss)"].max()


st.markdown(f"livre le plus long à lire : {titre_max_temps_lecture} {auteur_max_temps_lecture} {temps_max_lecture}")






