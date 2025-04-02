# Import libs
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import random
import numpy as np
import os
try:
    from menu import menu_with_redirect
except ImportError as e:
    print("ImportError:", e)

os.chdir(os.path.dirname(__file__))
st.set_page_config(
    page_title="page2",
    page_icon="📖",
    layout="wide", #wide-screen layout
    initial_sidebar_state="collapsed", #expanded sidebar
) 

# title
# dashboard title
st.title("📚 Book data analysis - zoom")
st.subheader("Comparison view")
st.markdown("""Comparison view

            """)



@st.cache_data
def load_data():
    df_book_updated = pd.read_parquet("../../data_sources_from_python/df_book_updated.parquet")
    df_stat = pd.read_parquet("../../data_sources_from_python/stats_lecture.parquet")
    df_book_paper = pd.read_excel("../../paper_audio/paper_audio.xlsx")
    
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


# Création du df
data = {
    current_year: [
        f"{nb_livre_current_year} livres entammés",
        f"{nb_livre_current_year_lus} livres lus",
        f"{nb_auteurs_current_year} auteurs<br> {ratio_auteurs_current_year} % auteurs / livres<br>{nb_auteurs_current_year_only} nouveaux auteurs",
        'D',
        'E',
        'F'
    ],
    comparison_year: [
        f"{nb_livre_comparison_year} livres entammés",
        f"{nb_livre_comparison_year_lus} livres lus",
        f"{nb_auteurs_comparison_year}<br>{ratio_auteurs_comparison_year}%<br>{nb_auteurs_comparison_year_only} auteurs uniques",
        4,
        5,
        6
    ]
}

df = pd.DataFrame(data)

# utiliser un df HTML
html_table = df.style.set_table_styles([
    {
        'selector': 'table, th, td',
        'props': [
            ('border', '0px'),  # Supprime les bordures
            ('padding', '4px 10px')  # Ajoute un peu de padding pour la lisibilité
        ]
    }
]).hide(axis="index").to_html()


# AFFICHAGE DU TABLEAU
st.markdown(html_table, unsafe_allow_html=True)
