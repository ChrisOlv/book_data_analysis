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
st.title(" DataViz Cabinet of Curiosities")
st.subheader("A collection of experiments, almost-works, and “why did I do this?” charts    ")

df_book_updated_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "df_book_updated.parquet"
df_stat_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "stats_lecture.parquet"
book_paper_path = Path(__file__).parent.parent.parent / "1.data"/ "1.raw"/"paper_audio" / "paper_audio.xlsx"


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


### data prep copy from app.py
df_stat['Date de lecture'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
df_stat['day_of_week'] = df_stat['Date de lecture'].dt.day_name()
df_stat['Date de lecture en jour'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
annee = 2025

st.markdown("---")
# ====== LINE CHART Temps de lecture ======
st.markdown("""
#### Total Reading Time per Day

In this chart, I wanted to show the **total reading time per day**.  
In theory, a bar chart would have been more logical and readable, but the line chart with a **rolling average** felt more practical and visually pleasant (I admit, a weak argument).  

Then I experimented with annotations… and that’s where things went south.  
Given the richness and disparity of the data, it’s **impossible to place annotations that work every time**.  
So I took a gamble: put the annotations somewhat randomly.  
Result? **High risk. High loss.**  

Moral of the story: sometimes the code is elegant, the result is chaotic… and that’s exactly the vibe this “museum” is about.
""")

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

plt.suptitle('Total reading time per day', fontsize=16, y=1)
plt.title('Annotations display the title of the book read during the day', fontsize=10, y=1)

plt.ylabel('Temps de Lecture (heures)', fontsize=8)
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()


st.pyplot(plt)


st.markdown("---")


# ===== LINE CHART AVERAGE SPEED =====
st.markdown("""
### Average Reading Speed

Here I wanted to show **how fast I read on average**.  
The idea was solid, but… same story as before: **annotations gone wild**.  

With data all over the place, predicting annotation placement that looks good every time is basically impossible.  
So I went for the risky move again: somewhat random positions.  
Result? Chaos, as expected.  
""")
# Conversion des dates et création de colonnes supplémentaires
df_stat['heure de début'] = pd.to_datetime(df_stat['heure de début'])
df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])

# Ajouter une colonne 'année_mois' pour regrouper par année et mois
df_stat['année_mois'] = df_stat['date lecture'].dt.to_period('M')

df_stat = df_stat[(df_stat['Temps passé sur la page en seconde'] > 5) & (df_stat['date lecture'].dt.year == annee)]

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
plt.suptitle('Average reading speed', fontsize=16, y=1)
plt.title('The graph represents the average reading speed for each day of reading. Annotations describe the top/worst 3 reading speed.', fontsize=10, y=1)
plt.xlabel("Date", fontsize=8)
plt.ylabel("Mean reading speed (pages/hour)", fontsize=8)
plt.grid(False)
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()

# Afficher le graphique
plt.show()

st.pyplot(plt)