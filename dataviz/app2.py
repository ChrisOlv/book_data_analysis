# documentation here https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/

import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta



st.set_page_config(
    page_title="book log analysis",
    page_icon="📖",
    layout="wide", #wide-screen layout
    initial_sidebar_state="collapsed", #expanded sidebar
)


df_book_updated = pd.read_parquet("df_book_updated.parquet")
df_book_streamlit = pd.read_parquet("df_book_streamlit.parquet")
df_stat = pd.read_parquet("stats_lecture.parquet")

# read parquet from a URL and keep it in cache, not working at the moment, #TODO check this issue later
# @st.cache_data
# def get_data1() -> pd.DataFrame:
#     return pd.read_parquet(df_book_updated)

# df_book_updated = get_data1()

# préparation des dataviz

# 0 / nombre de libres par catégorie : 
category_counts = df_book_streamlit['Catégorie'].value_counts().reset_index()
category_counts.columns = ['Catégorie', 'nombre de livre']

# Créer un graphique à barres horizontal
category_counts_sorted = category_counts.sort_values(by='nombre de livre', ascending=True)

fig0 = px.bar(category_counts_sorted,
             x='nombre de livre', 
             y='Catégorie',
             orientation='h',  # 'h' indique un bar chart horizontal
             title='Nombre de livres par catégorie',
             labels={'nombre de livre': 'Nombre de livres', 'Catégorie': 'Catégories'},
             text_auto=True
             
             )
fig0.update_traces(textposition="outside")
fig0.update_layout(xaxis=dict(
        showticklabels=False,  # Masquer les étiquettes de l'axe des x
        zeroline=False,        # Masquer la ligne zéro de l'axe des x
        showline=False,
        title=''               # Masquer le nom de l'axe des x
         # Masquer la ligne de l'axe des x
    )
)
# Afficher le graphique
# graph = fig0.show()

# nombre de livres lus par mois
# Convertir la colonne 'end_date' en type datetime
df_book_updated['end_date'] = pd.to_datetime(df_book_updated['end_date'], errors='coerce')

# Extraire le mois et l'année de 'end_date'
df_book_updated['month'] = df_book_updated['end_date'].dt.strftime('%B')
df_book_updated['month_num'] = df_book_updated['end_date'].dt.month
mois_ordres = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
df_book_updated['month'] = pd.Categorical(df_book_updated['month'], categories=mois_ordres, ordered=True)


# Compter le nombre de livres par mois
books_per_month = df_book_updated.groupby(['month', 'month_num']).size().reset_index(name='nombre de livres')

# Trier par ordre des mois de l'année
books_per_month = books_per_month.sort_values(by='month_num',ascending=True)

# Créer un graphique à barres horizontal
fig1 = px.bar(books_per_month,
              x='nombre de livres', 
              y='month',
              orientation='h',
              title='Nombre de livres lus par mois',
              labels={'nombre de livres': 'Nombre de livres', 'month': 'Mois'},
              text_auto=True
)

fig1.update_traces(textposition="outside",
                   textangle=0
                    
                )
fig1.update_layout(xaxis=dict(
        showticklabels=False,  # Masquer les étiquettes de l'axe des x
        zeroline=False,        # Masquer la ligne zéro de l'axe des x
        showline=False,
        title=''               # Masquer le nom de l'axe des x
         # Masquer la ligne de l'axe des x
    )
)


# 1/ PLUS LONGUE LECTURE
# le temps de lecture max
temps_maxi = df_book_streamlit[df_book_streamlit["temps passé sur le livre en heure"] == df_book_streamlit["temps passé sur le livre en heure"].max()]
# prisme livre
titre_max_temps_lecture = df_book_streamlit[df_book_streamlit["temps passé sur le livre en heure"] == df_book_streamlit["temps passé sur le livre en heure"].max()]["Titre"].values[0]
auteur_max_temps_lecture = df_book_streamlit[df_book_streamlit["temps passé sur le livre en heure"] == df_book_streamlit["temps passé sur le livre en heure"].max()]["Auteurs"].values[0]
temps_max_lecture = df_book_streamlit["temps passé sur le livre en heure"].max()
# print(f"Livre le plus long à lire : {titre_max_temps_lecture} de {auteur_max_temps_lecture} : {temps_max_lecture}")

# # 2/ PLUS RÉGULIER
# # Compter le nombre de lignes où "jours de lecture effectifs (jl)" est égal à "Durée lecture (j)"
# count_regulier = df_book_streamlit[df_book_streamlit["jours de lecture effectifs (jl)"] == df_book_streamlit["Durée lecture (j)"]].shape[0]

# # affiche le dernier, puis l'avant dernier, puis l'avant avant dernier
# df_book_streamlit[df_book_streamlit["jours de lecture effectifs (jl)"] == df_book_streamlit["Durée lecture (j)"]].sort_values(by="Date de lecture", ascending
# =False).head(3)[["Titre", "Durée lecture (j)", "jours de lecture effectifs (jl)", "Date de lecture"]]
# # enregistre les 3 titres dans une liste
# liste_livres = df_book_streamlit[df_book_streamlit["jours de lecture effectifs (jl)"] == df_book_streamlit["Durée lecture (j)"]].sort_values(by="Date de lecture", ascending   =False).head(3)["Titre"].values

# 3/ PLUS RAPIDE
livre_rapide = df_book_updated[df_book_updated["temps passé sur le livre en minute"] > 35]
livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]

titre_livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["Titre"].values[0]
auteur_livre_rapide =livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["Auteurs"].values[0]
vitesse_livre_rapide =livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["pages lues à la minute"].values[0].round(1)

# 4/ PLUS ADDICTIF
livre_addict = df_book_updated[df_book_updated["minutes_lecture_par_jour_de_lecture"] == df_book_updated["minutes_lecture_par_jour_de_lecture"].max()]
titre_livre_addict = livre_addict["Titre"].values[0]
auteur_livre_addict = livre_addict["Auteurs"].values[0]
minutes_livre_addict = livre_addict["minutes_lecture_par_jour_de_lecture"].values[0]

# # 5/ JOURS AVEC LE PLUS DE LECTURE
# # Convertir la colonne 'date lecture' en datetime
# df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'], format='%Y-%m-%d')

# # Joindre df_stat avec df_book_updated pour inclure le nom des livres
# df_stat2 = df_stat.merge(df_book_updated, left_on='id_book', right_on='id', how='left')

# # Agréger les données par 'date lecture'
# agg_data = df_stat2.groupby('date lecture').agg({
#     'Temps de lecture en minute': 'sum',
#     'page': 'nunique',
#     'id_book': 'nunique'
# }).reset_index()

# # Ajouter la liste des id_book et des titres pour chaque date de lecture
# book_ids_titles_by_date = df_stat2.groupby('date lecture').apply(
#     lambda x: ', '.join(sorted(set(f"{row['id_book']} ({row['Titre']})" for _, row in x.iterrows())))
# ).reset_index()

# # Fusionner les deux DataFrames
# merged_data = pd.merge(agg_data, book_ids_titles_by_date, on='date lecture')

# # Renommer pour plus de clarté
# merged_data.columns = ['date lecture', 'Temps de lecture en minute', 'Nombre de pages', 'Nombre de livres', 'Books']

# df_jours_plus_de_lecture = merged_data.sort_values('Temps de lecture en minute', ascending=False).head(3)

# # 6/ PIC DE VITESSE
# # Ajouter les colonnes 'id_book' et 'Titre' avec valeurs uniques pour chaque groupe
# def concatenate_unique_values(series):
#     return ', '.join(sorted(set(map(str, series))))

# books_info = df_stat2.groupby(['date lecture', 'Heure']).apply(
#     lambda x: pd.Series({
#         'id_books': concatenate_unique_values(x['id_book']),
#         'Titres': concatenate_unique_values(x['Titre'])
#     })
# ).reset_index()

# # Fusionner les deux DataFrames
# result = pd.merge(agg_data_pic_vitesse, books_info, on=['date lecture', 'Heure'])

# # Renommer les colonnes pour plus de clarté (si nécessaire)
# result.columns = ['date lecture', 'Heure', 'Nombre de pages', 'Temps passé sur la page en seconde', 'Temps de lecture en minute', 'id_books', 'Titres']


# result["page à la minute"] = (result["Nombre de pages"] / (result["Temps de lecture en minute"] )).round(2) 

# # faire un head de result trié par page à la minute, uniquement quand page supérieur à 60
# df_pic_vitesse = result[result["Nombre de pages"] > 60].sort_values(by='page à la minute', ascending=False).head(5)
# # result.sort_values(by='page', ascending=False).head(10)

# # 7/ plot des heures avec le plus de pages lues
# plot7 = sns.countplot(x='Heure', data=result[result["Nombre de pages"] > 60].sort_values(by='page à la minute', ascending=False).head(100))


# 8/ auteurs et livres : 
# print le nombre de lignes de df_book_updated
nb_livres_lus = df_book_streamlit.shape[0]
# print le nombre d'Auteurs lus de df_book_updated
nb_auteurs_lus = df_book_streamlit["Auteurs"].nunique()

# # page configuration

# title
# dashboard title
st.title("📚 Book data analysis")
st.subheader("Logs analysis from KO e-reader")
st.markdown("""This dashboard presents an analysis of e-book reading data.
            The data comes from the reading logs of an e-reader using Ko-reader.

            """)
with st.sidebar:
    st.header("filters")
    df_book_updated["end_date"] = pd.to_datetime(df_book_updated["end_date"], errors='coerce')
    df_book_updated2 = df_book_updated.dropna(subset=["end_date"])
    unique_years = pd.unique(df_book_updated2["end_date"].dt.year)
    Annee_lecture = st.selectbox("Select a year", unique_years)

    st.markdown("---")
    st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://github.com/ChrisOlv">@chris</a></h6>',
            unsafe_allow_html=True,
        )



# FILTERS

## filter by year





## Apply filters
df_book_updated = df_book_updated[df_book_updated["end_date"] == Annee_lecture]



# KPIs/summary cards
# create 4 columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
text1, text2, text3, text4 = st.columns(4)
table = st.columns(1)
chart1, chart2 = st.columns(2)

# 1/ plus longue lecture 
kpi1.metric(
    label="# Plus longue lecture",
    value=round(temps_max_lecture),
    help=("heures")
    )

text1.markdown(titre_max_temps_lecture+" de "+auteur_max_temps_lecture)

# 2/ plus rapide
kpi2.metric(
    label="# Plus rapide",
    value=vitesse_livre_rapide,
    help=("pages lues à la minute")
    )
text2.markdown(titre_livre_rapide+" de "+auteur_livre_rapide)


# 3/ plus addictif
kpi3.metric(
    label="# Plus addictif",
    value=round(minutes_livre_addict),
    help=("minutes de lecture par jour")
    )
text3.markdown(titre_livre_addict+" de "+auteur_livre_addict)

#4/ auteurs et livres
kpi4.metric(
    label="# Livres lus",
    value=nb_livres_lus
    )
text4.markdown(f"de {nb_auteurs_lus} auteurs différents")


st.markdown("## Visualisation des données")

with chart1:
    st.markdown("### Lecture par catégorie")
    fig = fig0
    st.write(fig)

with chart2:
    st.markdown("### Lecture par mois")
    fig = fig1
    st.write(fig)
# 5/ table

df_print = df_book_streamlit[df_book_streamlit['% lu'] == 100]
auteurs_a_exclure = ["Tamara Rosier", "Michael Joseph"]
df_print = df_print[~df_print['Auteurs'].isin(auteurs_a_exclure)]


st.markdown("Books read during the year :")
st.dataframe(
    df_print[["Titre","Auteurs","Catégorie","Date de lecture","Année publication", "# pages lues","pages lues à la minute","Durée lecture (j)", "jours de lecture effectifs (jl)", "# pages lues/jl","temps passé sur le livre en heure","minutes de lecture/jl" ]],
             hide_index=True,
             height=500,
             )