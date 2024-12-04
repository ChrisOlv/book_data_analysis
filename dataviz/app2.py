# documentation here https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/

import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import random



st.set_page_config(
    page_title="book log analysis",
    page_icon="📖",
    layout="wide", #wide-screen layout
    initial_sidebar_state="collapsed", #expanded sidebar
)

uploaded_file = st.file_uploader("Upload your SQLite3 file", type=["sqlite3", "db"], key="summary_file_uploader")

df_book_updated = pd.read_parquet("../data_sources_from_python/df_book_updated.parquet")
# df_book_streamlit = pd.read_parquet("df_book_streamlit.parquet")
df_stat = pd.read_parquet("../data_sources_from_python/stats_lecture.parquet")
# préparer df_book_updated pour le filtre : 
df_book_updated['Date de lecture'] = pd.to_datetime(df_book_updated['Date de lecture'], format="%Y-%m-%dT%H:%M:%S.%fZ")

# title
# dashboard title
st.title("📚 Book data analysis")
st.subheader("Logs analysis from KO e-reader")
st.markdown("""This dashboard presents an analysis of e-book reading data.
            The data comes from the reading logs of an e-reader using Ko-reader.

            """)
with st.sidebar: # sidebar
    st.header("Chart parameters ⚙️")
    filter_annee = st.sidebar.multiselect('Year', ['2023', '2024'], default=['2024']) # filter by year
    livre_termine = st.radio(    "reading status",    key="visibility",    options=["read", "unfinished", "read + unfinished"],)
    filter_auteur = st.sidebar.multiselect('Author', df_book_updated['Auteurs'].unique())
    filter_title = st.sidebar.multiselect('Title', df_book_updated['Titre'].unique())
    filter_category1 = st.sidebar.multiselect('Category', df_book_updated['category1'].unique())
    filter_category2 = st.sidebar.multiselect('Subcategory', df_book_updated['category2'].unique())


    st.markdown("---")
    st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://github.com/ChrisOlv">@chris</a></h6>',
            unsafe_allow_html=True,
        )
    

# on applique les filtres ici : 
# filtre année :
if filter_annee == []:
    df_book_updated = df_book_updated
else:
    df_book_updated = df_book_updated[df_book_updated['Date de lecture'].dt.year.astype(str).isin(filter_annee)]

# filtre livre terminé ou non
if livre_termine == "read":
    df_book_updated = df_book_updated[df_book_updated['% lu'] == 100]
elif livre_termine == "unfinished":
    df_book_updated = df_book_updated[df_book_updated['% lu'] != 100]
else:
    df_book_updated = df_book_updated

# filtre auteur : 
if filter_auteur == []:
    df_book_updated = df_book_updated
else:
    df_book_updated = df_book_updated[df_book_updated['Auteurs'].isin(filter_auteur)]

# filtre title : 
if filter_title == []:
    df_book_updated = df_book_updated
else:
    df_book_updated = df_book_updated[df_book_updated['Titre'].isin(filter_title)]

# filtre category1 :
if filter_category1 == []:
    df_book_updated = df_book_updated
else:
    df_book_updated = df_book_updated[df_book_updated['category1'].isin(filter_category1)]
# filtre category2 :
if filter_category2 == []:
    df_book_updated = df_book_updated
else:
    df_book_updated = df_book_updated[df_book_updated['category2'].isin(filter_category2)]

# préparation des dataviz

# 0 / nombre de libres par catégorie : 
category_counts = df_book_updated['Catégorie'].value_counts().reset_index()
category_counts.columns = ['Catégorie', 'nombre de livre']

# Créer un graphique à barres horizontal
category_counts_sorted = category_counts.sort_values(by='nombre de livre', ascending=True)

fig0 = px.bar(category_counts_sorted,
             x='nombre de livre', 
             y='Catégorie',
             orientation='h',  # 'h' indique un bar chart horizontal
             title='Number of books by category',
             labels={'nombre de livre': 'Number of books', 'Catégorie': 'Category'},
             text_auto=True
             
             )
fig0.update_traces(textposition="inside")
fig0.update_layout(xaxis=dict(
        showticklabels=False,  # Masquer les étiquettes de l'axe des x
        zeroline=False,        # Masquer la ligne zéro de l'axe des x
        showline=False,
        title=''               # Masquer le nom de l'axe des x
         # Masquer la ligne de l'axe des x
    )
)

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
              title='Number of books read per month',
              labels={'nombre de livres': 'Nombre de livres', 'month': 'Month'},
              text='nombre de livres',
              text_auto=True
)


fig1.update_traces(textposition="inside",
                #    textfont=dict(size=12),   # Réduire la taille de la police si nécessaire
    # cliponaxis=False,
                   textangle=0
                    
                )
fig1.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=mois_ordres),  # S'assurer que les mois sont bien triés
    xaxis=dict(
        showticklabels=False,  # Masquer les étiquettes de l'axe des x
        zeroline=False,        # Masquer la ligne zéro de l'axe des x
        showline=False,
        title=''),               # Masquer le nom de l'axe des x
        bargap=0.1,  # Ajouter de l'espace entre les barres
    )

# temps de lecture par mois
# compter le temps en minute par mois
time_per_month = df_book_updated.groupby(['month', 'month_num'])['temps passé sur le livre en heure'].sum().reset_index(name='Temps de lecture en heure').round(0)
books_per_month = books_per_month.sort_values(by='month_num',ascending=True)
# Créer un graphique à barres horizontal
fig2 = px.bar(time_per_month,
              x='Temps de lecture en heure', 
              y='month',
              orientation='h',
              title='Time of reading in hours',
              labels={'Temps de lecture en heure': 'Hours of reading', 'month': 'Month'},
              text='Temps de lecture en heure',
              text_auto=True
)


fig2.update_traces(textposition="inside",
                   textfont=dict(size=12),   # Réduire la taille de la police si nécessaire
                   cliponaxis=False,
                   textangle=0 
                )

fig2.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=mois_ordres),  # S'assurer que les mois sont bien triés
    xaxis=dict(
        showticklabels=False,  # Masquer les étiquettes de l'axe des x
        zeroline=False,        # Masquer la ligne zéro de l'axe des x
        showline=False,
        title=''),               # Masquer le nom de l'axe des x
        bargap=0.1,  # Ajouter de l'espace entre les barres
    )

# 1/ PLUS LONGUE LECTURE
# le temps de lecture max
temps_maxi = df_book_updated[df_book_updated["temps passé sur le livre en heure"] == df_book_updated["temps passé sur le livre en heure"].max()]
# prisme livre
titre_max_temps_lecture = df_book_updated[df_book_updated["temps passé sur le livre en heure"] == df_book_updated["temps passé sur le livre en heure"].max()]["Titre"].values[0]
auteur_max_temps_lecture = df_book_updated[df_book_updated["temps passé sur le livre en heure"] == df_book_updated["temps passé sur le livre en heure"].max()]["Auteurs"].values[0]
temps_max_lecture = df_book_updated["temps passé sur le livre en heure"].max()
# print(f"Livre le plus long à lire : {titre_max_temps_lecture} de {auteur_max_temps_lecture} : {temps_max_lecture}")

# # 2/ PLUS RÉGULIER
# # Compter le nombre de lignes où "jours de lecture effectifs (jl)" est égal à "Durée lecture (j)"
# count_regulier = df_book_updated[df_book_updated["jours de lecture effectifs (jl)"] == df_book_updated["Durée lecture (j)"]].shape[0]

# # affiche le dernier, puis l'avant dernier, puis l'avant avant dernier
# df_book_updated[df_book_updated["jours de lecture effectifs (jl)"] == df_book_updated["Durée lecture (j)"]].sort_values(by="Date de lecture", ascending
# =False).head(3)[["Titre", "Durée lecture (j)", "jours de lecture effectifs (jl)", "Date de lecture"]]
# # enregistre les 3 titres dans une liste
# liste_livres = df_book_updated[df_book_updated["jours de lecture effectifs (jl)"] == df_book_updated["Durée lecture (j)"]].sort_values(by="Date de lecture", ascending   =False).head(3)["Titre"].values

# 3/ PLUS RAPIDE
livre_rapide = df_book_updated[df_book_updated["temps passé sur le livre en minute"] > 35]
livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]

titre_livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["Titre"].values[0]
auteur_livre_rapide =livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["Auteurs"].values[0]
vitesse_livre_rapide =livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["pages lues à la minute"].values[0].round(1)

# 4/ PLUS ADDICTIF
livre_addict = df_book_updated[df_book_updated["minutes de lecture/jl"] == df_book_updated["minutes de lecture/jl"].max()]
titre_livre_addict = livre_addict["Titre"].values[0]
auteur_livre_addict = livre_addict["Auteurs"].values[0]
minutes_livre_addict = livre_addict["minutes de lecture/jl"].values[0]

# # 5/ JOURS AVEC LE PLUS DE LECTURE
# # Convertir la colonne 'date lecture' en datetime
# df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'], format='%Y-%m-%d')

# # Joindre df_stat avec df_book_updated pour inclure le nom des livres
# df_stat = df_stat.merge(df_book_updated, left_on='id_book', right_on='id', how='left')

# # Agréger les données par 'date lecture'
# agg_data = df_stat.groupby('date lecture').agg({
#     'Temps de lecture en minute': 'sum',
#     'page': 'nunique',
#     'id_book': 'nunique'
# }).reset_index()

# # Ajouter la liste des id_book et des titres pour chaque date de lecture
# book_ids_titles_by_date = df_stat.groupby('date lecture').apply(
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

# books_info = df_stat.groupby(['date lecture', 'Heure']).apply(
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
nb_livres_lus = df_book_updated[df_book_updated['% lu'] == 100].shape[0]



# print le nombre d'Auteurs lus de df_book_updated

nb_auteurs_lus = df_book_updated[df_book_updated['% lu'] == 100]["Auteurs"].nunique()

# # page configuration


# FILTERS

## filter by year



# KPIs/summary cards
# create 4 columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
text1, text2, text3, text4 = st.columns(4)
table = st.columns(1)
chart1, chart2,chart4 = st.columns(3)
chart3 = st.columns(1)

# 1/ plus longue lecture 
kpi1.metric(
    label="# Longest Reading",
    value=round(temps_max_lecture),
    help=("hours")
    )

text1.markdown(titre_max_temps_lecture+" de "+auteur_max_temps_lecture)

# 2/ plus rapide
kpi2.metric(
    label="# Fastest Reading",
    value=vitesse_livre_rapide,
    help=("pages read per minute")
    )
text2.markdown(titre_livre_rapide+" de "+auteur_livre_rapide)


# 3/ plus addictif
kpi3.metric(
    label="# Most Addictive Reading",
    value=round(minutes_livre_addict),
    help=("reading minutes per day")
    )
text3.markdown(titre_livre_addict+" de "+auteur_livre_addict)

#4/ auteurs et livres
kpi4.metric(
    label="# Books Read",
    value=nb_livres_lus
    )
text4.markdown(f"by {nb_auteurs_lus}  different authors")


st.markdown("## Book table")

with chart1:
    st.markdown("### Reading by Category")
    fig = fig0
    st.write(fig)

# with chart2:
#     st.markdown("### Lecture par mois")
#     fig = fig1
#     st.write(fig)


# chart2 = st.container()
with chart2:
    st.markdown("### Reading by Month")
    st.plotly_chart(fig1) 

# chart2 = st.container()
with chart4:
    st.markdown("### Time of Reading by Month")
    st.plotly_chart(fig2) 
# 5/ table

# df_print = df_book_updated[df_book_updated['% lu'] == 100]
auteurs_a_exclure = ["Tamara Rosier", "Michael Joseph"] 
titres_a_exclure = ["ERROR: Error reading EPUB format"]
df_print = df_book_updated[~df_book_updated['Auteurs'].isin(auteurs_a_exclure)]
df_print = df_print[~df_print['Titre'].isin(titres_a_exclure)]
# changer la caolonne date lecture en YYYY-MM-DD
df_print['Date de lecture'] = df_print['Date de lecture'].dt.strftime('%Y-%m-%d')

st.markdown("Books read during the year :")
st.dataframe(
    df_print[["Titre","Auteurs","Catégorie","Date de lecture","Year rel", "# pages lues","pages lues à la minute","Durée lecture (j)", "jours de lecture effectifs (jl)", "# pages lues/jl","temps passé sur le livre en heure","minutes de lecture/jl" ]],
             hide_index=True,
             height=500,
             )

# # pour faire un print : 
# text0 = st.empty()
# aa = df_print.shape[0]
# text0.markdown(str(aa))
# # ou text0.markdown(aa)


# ===== HEATMAP =====

# V1
st.markdown("## Heatmap")

# heatmap 
import calmap
import matplotlib.pyplot as plt
# passer df_stat['date lecture'] en dt time
df_stat = df_stat
df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])
df_aggregated = df_stat.groupby('date lecture')['Temps de lecture en minute'].sum().reset_index()
df_serie = df_aggregated.set_index('date lecture')['Temps de lecture en minute']

# Remplir les dates manquantes avec 0
df_serie = df_serie.asfreq('D', fill_value=0)

# filter_annee est au format ['2024'], on veut 2024
annee = int(filter_annee[0])


# st.pyplot(figure)
def create_calmap(df_serie):
    plt.figure(figsize=(16, 10))
    calmap.yearplot(
        df_serie,
        year=annee,
        fillcolor='lightgrey',
        cmap='YlGn',
        linewidth=2,
        daylabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],  # Correction pour daylabels
        dayticks=[0, 1, 2, 3, 4, 5, 6], monthly_border=False,
    )

    
    
    plt.title('Year of reading')
    # plt.text("test")
    st.pyplot(plt)

# Afficher le plot dans Streamlit
create_calmap(df_serie)
# ====== fin heatmap =====


# ===== MATRICE =====

# TEMPS DE LECTURE MOYEN
df_stat['Date de lecture en jour'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
# Temps de lecture moyen par jour, distinct date de lecture en jour
temps_quotidien_moyen_ALL = df_stat["Temps passé sur la page en seconde"].sum() / df_stat["Date de lecture en jour"].nunique()/60 # c
# Temps de lecture dernier jour (df_stat)
temps_quotidien_moyen_lastday = df_stat[df_stat["Date de lecture en jour"] == df_stat["Date de lecture en jour"].max()]["Temps passé sur la page en seconde"].sum()/60

# temps de lecture 3 derniers jours (df_stat)
temps_quotidien_moyen_3days_sum = (df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)]["Temps passé sur la page en seconde"].sum()/60).round(0)
temps_quotidien_moyen_3days = (df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)]["Temps passé sur la page en seconde"].sum()/60/3).round(0)
temps_quotidien_moyen_7days_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)]["Temps passé sur la page en seconde"].sum()/60
temps_quotidien_moyen_7days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)]["Temps passé sur la page en seconde"].sum()/60/7
temps_quotidien_moyen_30days_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)]["Temps passé sur la page en seconde"].sum()/60
temps_quotidien_moyen_30days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)]["Temps passé sur la page en seconde"].sum()/60/30
temps_quotidien_moyen_365days_glissants_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)]["Temps passé sur la page en seconde"].sum()/60
temps_quotidien_moyen_365days_glissants = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)]["Temps passé sur la page en seconde"].sum()/60/365
temps_quotidien_moyen_this_year_sum = df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year]["Temps passé sur la page en seconde"].sum()/60
temps_quotidien_moyen_this_year = df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year]["Temps passé sur la page en seconde"].sum()/60/df_stat["Date de lecture en jour"].nunique()





# NOMBRE DE PAGE MOYEN
# faire un group by de df_stat par id_book et page
df_stat_grouped_nb_pages = df_stat.groupby(["id_book", "page"]).size().reset_index(name='count')
nombre_de_lignes = df_stat_grouped_nb_pages.shape[0]
pages_quotidien_moyen_ALL = nombre_de_lignes / df_stat["Date de lecture en jour"].nunique() # compte que les jours de lecture
pages_hebdo_moyen_ALL = nombre_de_lignes / df_stat["Date de lecture en jour"].nunique() * 7
pages_monthly_moyen_ALL = nombre_de_lignes / df_stat["Date de lecture en jour"].nunique() * 30
pages_quotidien_moyen_lastday = df_stat[df_stat["Date de lecture en jour"] == df_stat["Date de lecture en jour"].max()].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_3days_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_3days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]/3
pages_quotidien_moyen_7days_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_7days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]/7
pages_quotidien_moyen_30days_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_30days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]/30
pages_quotidien_moyen_365days_glissants_sum = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_365days_glissants = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]/365
pages_quotidien_moyen_this_year_sum = df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]
pages_quotidien_moyen_this_year = df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0]/df_stat["Date de lecture en jour"].nunique()




print('ALL', 'Last day', 'moyenne 3 days', '3 days sum', 'moyenne 7 days', '7 days sum', 'moyenne 30 days', '30 days sum', 'moyenne 365 days glissants', '365 days glissants sum', 'moyenne this year', 'this year sum')

# vitesse de lecture
vitesse_lecture_ALL = nombre_de_lignes / df_stat["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_lastday = df_stat[df_stat["Date de lecture en jour"] == df_stat["Date de lecture en jour"].max()].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"] == df_stat["Date de lecture en jour"].max()]["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_3days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=3)]["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_7days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=7)]["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_30days = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=30)]["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_365days_glissants = df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"] > df_stat["Date de lecture en jour"].max() - timedelta(days=365)]["Temps passé sur la page en seconde"].sum() * 60*60
vitesse_lecture_this_year = df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year].groupby(["id_book", "page"]).size().reset_index(name='count').shape[0] / df_stat[df_stat["Date de lecture en jour"].dt.year == df_stat["Date de lecture en jour"].max().year]["Temps passé sur la page en seconde"].sum() * 3600


# matrice  12x2

data = [
    [temps_quotidien_moyen_ALL, temps_quotidien_moyen_lastday, temps_quotidien_moyen_3days, temps_quotidien_moyen_7days, temps_quotidien_moyen_30days, temps_quotidien_moyen_365days_glissants, temps_quotidien_moyen_this_year],
    [pages_quotidien_moyen_ALL, pages_quotidien_moyen_lastday, pages_quotidien_moyen_3days, pages_quotidien_moyen_7days, pages_quotidien_moyen_30days, pages_quotidien_moyen_365days_glissants, pages_quotidien_moyen_this_year],
    [vitesse_lecture_ALL, vitesse_lecture_lastday, vitesse_lecture_3days, vitesse_lecture_7days, vitesse_lecture_30days, vitesse_lecture_365days_glissants, vitesse_lecture_this_year]
]

# Définir les noms des colonnes et des index (lignes)
columns = ['All', 'Last day', '3 days',  '7 days',  '30 days',  '12 months',  'this year']
index = ['Average reading time (min)', 'Average daily pages read',"Average reading speed (pages/hour)"]
matrice = pd.DataFrame(data, columns=columns, index=index)
matrice = matrice.fillna(0)
matrice = matrice.astype(int)

st.markdown("## Matrix")
st.dataframe(
    matrice,
             hide_index=False,
            #  height=500,
             )
# ====== fin matrice =====



# ====== LINE CHART Temps de lecture ======
# group by df_stat par date de lecture en jour, puis somme Temps passé sur la page en seconde
daily_reading_time = df_stat.groupby('Date de lecture en jour')['Temps passé sur la page en seconde'].sum().reset_index()
daily_reading_time['Temps passé sur la page en minute'] = daily_reading_time['Temps passé sur la page en seconde'] / 60
daily_reading_time['Temps passé sur la page en heure'] = daily_reading_time['Temps passé sur la page en minute'] / 60
# ajoute annotation : titre des 5 jours avec le plus de lecture, si il y a plusieurs livre, affiche le premier
top_days = daily_reading_time.nlargest(15, 'Temps passé sur la page en heure')

top_days_with_books = top_days.merge(
    df_stat[['Date de lecture en jour', 'id_book', 'Titre']].drop_duplicates(),
    left_on='Date de lecture en jour',
    right_on='Date de lecture en jour',
    how='left'
)
# créer une colonne titre_court, reprend uniquement les 10 premiers caractères de Titre
top_days_with_books['Titre_court'] = top_days_with_books['Titre'].str[:25]
# créer une colonne titre_court, reprend uniquement les mots de plus de 4 lettres et les chiffres
# top_days_with_books['Titre_court'] = top_days_with_books['Titre'].str.findall(r'\b\w{4,}\b').str.join(' ')



# new
top_days_with_books['Titre_concatené'] = top_days_with_books.groupby('Date de lecture en jour')['Titre_court'].transform(lambda x: ' & '.join(x))
top_days_with_books_unique = top_days_with_books.drop_duplicates(subset=['Date de lecture en jour'])




# top_days_with_books = top_days_with_books.sort_values(by='Date de lecture en jour').drop_duplicates(subset=['Date de lecture en jour'])

# plot daily_reading_time sur un line chart
plt.figure(figsize=(12, 6))
plt.plot(daily_reading_time['Date de lecture en jour'], daily_reading_time['Temps passé sur la page en heure'], marker='')

# Ajouter des annotations pour les 5 jours avec le plus de lecture
for i, row in top_days_with_books_unique .iterrows():
    date = row['Date de lecture en jour']
    time_spent = row['Temps passé sur la page en heure']
    title = row['Titre_concatené']

        # Créer un offset aléatoire
    offset_x = random.randint(10, 50)  # Décalage horizontal entre 10 et 50
    offset_y = random.randint(10, 30)  # Décalage vertical entre 10 et 30
    
    plt.annotate(
        f"{title}",
        (date, time_spent),
        textcoords="offset points",
        xytext=(offset_x, offset_y),  # Décalage vertical
        ha='center',
        fontsize=9,
        color='blue',
        # rotation=30,
        # ajouter transparence texte
        alpha=0.55,
        arrowprops=dict(arrowstyle="->", color="blue", lw=0.1)  # Optionnel : ajouter une flèche
    )

plt.title('Temps de Lecture Total par Jour')
plt.ylabel('Temps de Lecture (heures)')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()


st.pyplot(plt)


# ====== fin line chart Temps de lecture =======

# ===== LINE CHART AVERAGE SPEED =====
# Conversion des dates et création de colonnes supplémentaires
df_stat['heure de début'] = pd.to_datetime(df_stat['heure de début'])
df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])

# Ajouter une colonne 'année_mois' pour regrouper par année et mois
df_stat['année_mois'] = df_stat['date lecture'].dt.to_period('M')

df_stat = df_stat[(df_stat['Temps passé sur la page en seconde'] > 5) & (df_stat['date lecture'].dt.year == 2024)]

# Groupement par id_book, page et année_mois
grouped = df_stat.groupby(['id_book', 'page', 'année_mois'], as_index=False).agg({
    'Temps passé sur la page en seconde': 'sum',
    'id_long': 'first',  # On garde le premier id_long pour chaque groupe
    'date lecture': 'min',  # Première date de lecture
    'heure de début': 'min'  # Première heure de début
})

# Calcul de la vitesse de lecture
grouped['Temps total en minutes'] = grouped['Temps passé sur la page en seconde'] / 60
grouped['vitesse (pages/minute)'] = 1 / grouped['Temps total en minutes']  # 1 page divisée par le temps en minutes
grouped['vitesse (pages/heure)'] = grouped['vitesse (pages/minute)'] * 60  # Conversion en pages par heure



# Regrouper par date lecture
daily_speed = grouped.groupby('date lecture', as_index=False).agg({
    'page': lambda x: x.nunique(),  # Nombre de pages uniques lues
    'Temps passé sur la page en seconde': 'sum'  # Temps total passé en secondes
})

# Calcul de la vitesse moyenne journalière
daily_speed['vitesse moyenne (pages/heure)'] = daily_speed['page'] / (daily_speed['Temps passé sur la page en seconde'] / 3600)

# Trier par vitesse décroissante pour identifier les anomalies
sorted_daily_speed = daily_speed.sort_values(by='vitesse moyenne (pages/heure)', ascending=False)






# Supprimer les lignes avec une vitesse moyenne < 250
filtered_daily_speed = daily_speed[daily_speed['vitesse moyenne (pages/heure)'] <= 220]

mean_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].mean()
median_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].median()
std_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].std()
top_speeds = filtered_daily_speed.nlargest(3, 'vitesse moyenne (pages/heure)')
top_days = daily_speed.nlargest(4, 'vitesse moyenne (pages/heure)')[['date lecture', 'vitesse moyenne (pages/heure)']]
worst_days = daily_speed.nsmallest(4, 'vitesse moyenne (pages/heure)')[['date lecture', 'vitesse moyenne (pages/heure)']]


# Étape 2 : Associer id_book à ces journées
top_days_with_books = top_days.merge(
    grouped[['date lecture', 'id_book']].drop_duplicates(),  # Récupérer les ids uniques
    on='date lecture',
    how='left'
)


# Joindre les titres des livres au top_days_with_books
top_days_with_titles = top_days_with_books.merge(
    df_book_updated[['id', 'Titre']],  # Garder uniquement les colonnes nécessaires
    left_on='id_book',
    right_on='id',
    how='left'
)
worst_days_with_titles = worst_days.merge(
    grouped[['date lecture', 'id_book']],  # Ajouter l'ID du livre
    on='date lecture',
    how='left'
).merge(
    df_book_updated[['id', 'Titre']],
    left_on='id_book',
    right_on='id',
    how='left'
)
# Tracé de la vitesse moyenne journalière après suppression des anomalies
plt.figure(figsize=(12, 6))
plt.plot(
    filtered_daily_speed['date lecture'],
    filtered_daily_speed['vitesse moyenne (pages/heure)'],
    marker='.',
    label='Average speed page/hour)'
)

# Ajouter des lignes horizontales pour les statistiques
plt.axhline(y=mean_speed, color='red', linestyle='--', label=f'Average ({mean_speed:.0f})')
plt.axhline(y=median_speed, color='green', linestyle='-.', label=f'Median ({median_speed:.0f})')
plt.axhline(y=mean_speed + std_speed, color='blue', linestyle=':', label=f'+1 Std ({(mean_speed + std_speed):.0f})')
plt.axhline(y=mean_speed - std_speed, color='blue', linestyle=':', label=f'-1 Std ({(mean_speed - std_speed):.0f})')

# Annoter les 3 vitesses les plus élevées avec des positions dynamiques
for i, row in enumerate(top_days_with_titles.iterrows()):
    _, row = row
    date = row['date lecture']
    speed = row['vitesse moyenne (pages/heure)']
    title = row['Titre']
    
    # Calcul d'un offset vertical différent pour éviter les chevauchements
    vertical_offset = 15 if i % 2 == 0 else -15  # Alterner les directions
    
    plt.annotate(
        f"{title}",
        (date, speed),
        textcoords="offset points",
        xytext=(0, vertical_offset),  # Décalage vertical dynamique
        ha='center',
        fontsize=10,
        color='purple',
        alpha=0.55,
        arrowprops=dict(arrowstyle="->", color="purple", lw=0.5)  # Optionnel : ajouter une flèche
    )

# Annoter les jours avec les vitesses les plus lentes
for i, row in enumerate(worst_days_with_titles.iterrows()):
    _, row = row
    date = row['date lecture']
    speed = row['vitesse moyenne (pages/heure)']
    title = row['Titre']
    
    vertical_offset = -25 if i % 2 == 0 else 25
    plt.annotate(
        f"{title}",
        (date, speed),
        textcoords="offset points",
        xytext=(0, vertical_offset),
        ha='center',
        fontsize=10,
        color='orange',
        alpha=0.55,
        arrowprops=dict(arrowstyle="->", color="orange", lw=0.5)
    )


# Ajouter des détails au graphique
plt.title("Vitesse Moyenne de Lecture par Jour", fontsize=16)
plt.xlabel("Date de lecture", fontsize=12)
plt.ylabel("Vitesse moyenne (pages/heure)", fontsize=12)
plt.grid(False)
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()

# Afficher le graphique
plt.show()

st.pyplot(plt)

# ======end line chart=======
# # v 2
## plus de paramètres, mais c'est pas encore ça
# import calplot  # Import Calplot au lieu de Calmap

# # Préparer les données
# df_stat = df_stat.copy()  # Fait une copie pour éviter d'éventuelles modifications inutiles
# df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])
# df_aggregated = df_stat.groupby('date lecture')['Temps de lecture en minute'].sum().reset_index()
# df_serie = df_aggregated.set_index('date lecture')['Temps de lecture en minute']

# # Remplir les dates manquantes avec 0
# df_serie = df_serie.asfreq('D', fill_value=0)

# # Filtrer l'année
# annee = int(filter_annee[0])

# # Fonction pour créer le CalMap avec Calplot
# def create_calmap(df_serie, year):
#     # Filtrer les données pour l'année en question
#     df_year = df_serie[df_serie.index.year == year]

#     # Création du plot
#     fig, ax = calplot.calplot(
#         df_year,

#         cmap='YlGn',
#         figsize=(10, 10),
#         colorbar=False,
#         suptitle='Year of reading',
#         linewidth=0.5,
#         linecolor='white',
#         daylabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
#         dayticks=[0, 1, 2, 3, 4, 5, 6],
#     )
#     fig.tight_layout(pad=-45)
#     # fig.subplots_adjust(top=0.9, bottom=0.15, left=0.1, right=0.9)

#     # sm = plt.cm.ScalarMappable(cmap='YlGn', norm=plt.Normalize(vmin=df_year.min(), vmax=df_year.max()))
#     # sm.set_array([])
#     # cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05)
#     # cbar.set_label("Temps de lecture (minutes)", fontsize=8)  # Ajuster la taille du label
#     # cbar.ax.tick_params(labelsize=6)  # Réduire la taille des ticks
#     # Afficher le plot dans Streamlit
#     st.pyplot(fig)

# # Afficher le plot dans Streamlit
# create_calmap(df_serie, annee)
