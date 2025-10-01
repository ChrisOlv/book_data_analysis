import pandas as pd 
import plotly.express as px
import streamlit as st 
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import random
import numpy as np
import os
import datetime
from pathlib import Path

try:
    from menu import menu_with_redirect
except ImportError as e:
    print("ImportError:", e)

os.chdir(os.path.dirname(__file__))
st.set_page_config(
    page_title="page2",
    page_icon="📖",
    layout="wide", 
    initial_sidebar_state="collapsed", 
) 

# title
# dashboard title
st.title("📚 Book data analysis - zoom")
st.subheader("Comparison view")

df_book_updated_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "df_book_updated.parquet"
df_stat_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "stats_lecture.parquet"
book_paper_path = Path(__file__).parent.parent.parent / "paper_audio" / "paper_audio.xlsx"


for path in [df_book_updated_path, df_stat_path, book_paper_path]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

@st.cache_data
def load_data():
    df_book_updated = pd.read_parquet(df_book_updated_path)
    df_stat = pd.read_parquet(df_stat_path)
    df_book_paper = pd.read_excel(book_paper_path)
    
    # Conversion des dates
    df_book_updated['Date de lecture'] = pd.to_datetime(df_book_updated['Date de lecture'], format="%Y-%m-%dT%H:%M:%S.%fZ")
    df_book_paper['date de lecture'] = pd.to_datetime(df_book_paper['date de lecture'], format='%d/%m/%Y')
    
    return df_book_updated, df_book_paper, df_stat

df_book_updated, df_book_paper, df_stat = load_data()

current_year = 2025
comparison_year = 2024

# VARIABLES
## 1/ compter le nombre de livres entammés 
nb_livre_current_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['Titre'].nunique()
nb_livre_comparison_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['Titre'].nunique()
## 2/ compter le nombre de livres terminés 
nb_livre_current_year_lus = df_book_updated[
    (df_book_updated['Date de lecture'].dt.year == current_year) & 
    (df_book_updated['% lu'] == 100)
]['Titre'].nunique()

nb_livre_comparison_year_lus = df_book_updated[
    (df_book_updated['Date de lecture'].dt.year == comparison_year) & 
    (df_book_updated['% lu'] == 100)
]['Titre'].nunique()
ratio_lu_current = round((nb_livre_current_year_lus / nb_livre_current_year) * 100)
ratio_lu_comparison = round((nb_livre_comparison_year_lus / nb_livre_comparison_year) * 100)

## 3/ compter le nombre d'auteurs et ratio livres / auteurs
nb_auteurs_current_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['Auteurs'].nunique()
nb_auteurs_comparison_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['Auteurs'].nunique()
ratio_auteurs_current_year = round((nb_auteurs_current_year / nb_livre_current_year) * 100)
ratio_auteurs_comparison_year = round(( nb_auteurs_comparison_year/nb_livre_comparison_year)*100)
# dans df_book_updated, compter les auteurs qui apparaissent uniquement dans la current year
nb_auteurs_current_year_only = df_book_updated[
    (df_book_updated['Date de lecture'].dt.year == current_year) &
    (df_book_updated['Auteurs'].isin(df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['Auteurs']) == False)
]['Auteurs'].nunique()
# nombre auteur unique dans la comparison year
nb_auteurs_comparison_year_only = df_book_updated[
    (df_book_updated['Date de lecture'].dt.year == comparison_year) &
    (df_book_updated['Auteurs'].isin(df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['Auteurs']) == False)
]['Auteurs'].nunique()

## 4/ nombre de pages
### nombre de pages total
nb_page_current_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['# pages lues'].sum()
nb_page_comparison_year = df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['# pages lues'].sum()

### nombre de page par livre en moyenne
nb_page_moyen_current_year = round(df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['# pages lues'].mean())
nb_page_moyen_comparison_year = round(df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['# pages lues'].mean())

## 5/ temps de lecture
### somme temps de lecture
temps_lecture_current_year = (df_book_updated[df_book_updated['Date de lecture'].dt.year == current_year]['temps passé sur le livre en minute'].sum())/60
temps_lecture_comparison_year = round((df_book_updated[df_book_updated['Date de lecture'].dt.year == comparison_year]['temps passé sur le livre en minute'].sum())/60)

### temps de lecture par jour # temps de lecture / nombre de jours entre le 1er janvier et aujourd'hui
days_elapsed = (datetime.date.today() - datetime.date(current_year, 1, 1)).days

temp_lecture_par_jour = temps_lecture_current_year / days_elapsed
temps_lecture_par_jour_comparison_year = temps_lecture_comparison_year / 365
### vitesse de lecture


# Création du df
data = {
        comparison_year: [
        f"{nb_livre_comparison_year} livres entammés",
        f"{nb_livre_comparison_year_lus} livres lus<br> {ratio_lu_comparison}%",
        f"{nb_auteurs_comparison_year} auteurs <br>{ratio_auteurs_comparison_year}% auteurs / livres <br>{nb_auteurs_comparison_year_only} auteurs uniques",
        f"{nb_page_comparison_year}p. lues<br>{nb_page_moyen_comparison_year} p./livre",
        f"{temps_lecture_comparison_year}h de lecture<br>soit en moyenne {round(temps_lecture_par_jour_comparison_year*60)} min/jour",

    ],
    " ":["","","VS","",""],
    current_year: [
        f"{nb_livre_current_year} livres entammés",
        f"{nb_livre_current_year_lus} livres lus<br> {ratio_lu_current}%",
        f"{nb_auteurs_current_year} auteurs<br> {ratio_auteurs_current_year} % auteurs / livres<br>{nb_auteurs_current_year_only} nouveaux auteurs",
        f"{nb_page_current_year} pages lues <br>{nb_page_moyen_current_year} pages/livre",
        f"{round(temps_lecture_current_year)}h de lecture <br>soit en moyenne {round(temp_lecture_par_jour*60)} min/jour",

    ]

}

df = pd.DataFrame(data)

# utiliser un df HTML
html_table = df.style.set_table_styles([
    {
        'selector': 'table, th, td',
        'props': [
            ('border', '0px'), 
            ('padding', '10px 100px') 
        ]
    }
]).hide(axis="index").to_html()


# AFFICHAGE DU TABLEAU
st.markdown(html_table, unsafe_allow_html=True)
