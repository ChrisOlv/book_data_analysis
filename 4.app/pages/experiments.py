import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st 
import random
from pathlib import Path
import os

# Menu import
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

# Titles
st.title(" DataViz Cabinet of Curiosities")
st.subheader("A collection of experiments, almost-works, and “why did I do this?” charts")

# Paths
df_book_updated_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "df_book_updated.parquet"
df_stat_path = Path(__file__).parent.parent.parent / "1.data" / "2.processed" / "stats_lecture.parquet"
book_paper_path = Path(__file__).parent.parent.parent / "1.data"/ "1.raw"/"paper_audio" / "paper_audio.xlsx"

for path in [df_book_updated_path, df_stat_path, book_paper_path]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

# Load data
@st.cache_data
def load_data():
    df_book_updated = pd.read_parquet(df_book_updated_path)
    df_stat = pd.read_parquet(df_stat_path)
    df_book_paper = pd.read_excel(book_paper_path)
    
    df_book_updated['Date de lecture'] = pd.to_datetime(df_book_updated['Date de lecture'], format="%Y-%m-%dT%H:%M:%S.%fZ")
    df_book_paper['date de lecture'] = pd.to_datetime(df_book_paper['date de lecture'], format='%d/%m/%Y')
    
    return df_book_updated, df_book_paper, df_stat

df_book_updated, df_book_paper, df_stat = load_data()

# Prepare stats
df_stat['Date de lecture'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
df_stat['day_of_week'] = df_stat['Date de lecture'].dt.day_name()
df_stat['Date de lecture en jour'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
annee = 2025

# st.markdown("---")

# ====== TOTAL READING TIME ======
text1 = """
#### Total Reading Time per Day

In this chart, I wanted to show the total reading time per day.
In theory, a bar chart would have been more logical and readable, but the line chart with a rolling average felt more practical and visually pleasant (I admit, a weak argument).

Then I experimented with annotations… and that’s where things went south.
Given the richness and disparity of the data, it’s impossible to place annotations that work every time.
So I took a gamble: put the annotations somewhat randomly.
Result? High risk. High loss.

Moral of the story: sometimes the code is elegant, the result is chaotic… and that’s exactly the vibe this “museum” is about.
"""

daily_reading_time = df_stat.groupby('Date de lecture en jour')['Temps passé sur la page en seconde'].sum().reset_index()
daily_reading_time['Temps passé sur la page en minute'] = daily_reading_time['Temps passé sur la page en seconde'] / 60
daily_reading_time['Temps passé sur la page en heure'] = daily_reading_time['Temps passé sur la page en minute'] / 60

top_days = daily_reading_time.nlargest(15, 'Temps passé sur la page en heure')

top_days_with_books = top_days.merge(
    df_stat[['Date de lecture en jour', 'id_book', 'Titre']].drop_duplicates(),
    on='Date de lecture en jour',
    how='left'
)

top_days_with_books['Titre_court'] = top_days_with_books['Titre'].str[:25]
top_days_with_books['Titre_concatené'] = top_days_with_books.groupby('Date de lecture en jour')['Titre_court'].transform(lambda x: ' & '.join(x))
top_days_with_books_unique = top_days_with_books.drop_duplicates(subset=['Date de lecture en jour'])

# Create figure for total reading time
fig_time, ax_time = plt.subplots(figsize=(12, 6))
ax_time.plot(daily_reading_time['Date de lecture en jour'], daily_reading_time['Temps passé sur la page en heure'])

# Add annotations
for i, row in top_days_with_books_unique.iterrows():
    date = row['Date de lecture en jour']
    time_spent = row['Temps passé sur la page en heure']
    title = row['Titre_concatené']
    offset_x = random.randint(10, 50)
    offset_y = random.randint(10, 30)
    
    ax_time.annotate(
        f"{title}",
        (date, time_spent),
        textcoords="offset points",
        xytext=(offset_x, offset_y),
        ha='center',
        fontsize=9,
        color='blue',
        alpha=0.55,
        arrowprops=dict(arrowstyle="->", color="blue", lw=0.1)
    )

ax_time.set_title('Total reading time per day')
ax_time.set_ylabel('Temps de Lecture (heures)')
ax_time.grid(True)
plt.tight_layout()

# ====== AVERAGE READING SPEED ======
text2 = """
### Average Reading Speed

Here I wanted to show how fast I read on average.
The idea was solid, but… same story as before: annotations gone wild.

With data all over the place, predicting annotation placement that looks good every time is basically impossible.
So I went for the risky move again: somewhat random positions.

Result? Chaos, as expected.






"""

df_stat['heure de début'] = pd.to_datetime(df_stat['heure de début'])
df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])
df_stat['année_mois'] = df_stat['date lecture'].dt.to_period('M')
df_stat = df_stat[(df_stat['Temps passé sur la page en seconde'] > 5) & (df_stat['date lecture'].dt.year == annee)]

grouped = df_stat.groupby(['id_book', 'page', 'année_mois'], as_index=False).agg({
    'Temps passé sur la page en seconde': 'sum',
    'id_long': 'first',
    'date lecture': 'min',
    'heure de début': 'min'
})

grouped['Temps total en minutes'] = grouped['Temps passé sur la page en seconde'] / 60
grouped['vitesse (pages/heure)'] = 1 / grouped['Temps total en minutes'] * 60

daily_speed = grouped.groupby('date lecture', as_index=False).agg({
    'page': lambda x: x.nunique(),
    'Temps passé sur la page en seconde': 'sum'
})

daily_speed['vitesse moyenne (pages/heure)'] = daily_speed['page'] / (daily_speed['Temps passé sur la page en seconde'] / 3600)
filtered_daily_speed = daily_speed[daily_speed['vitesse moyenne (pages/heure)'] <= 220]

mean_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].mean()
median_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].median()
std_speed = filtered_daily_speed['vitesse moyenne (pages/heure)'].std()

top_days = filtered_daily_speed.nlargest(3, 'vitesse moyenne (pages/heure)')
worst_days = filtered_daily_speed.nsmallest(3, 'vitesse moyenne (pages/heure)')

# Merge titles
top_days_with_titles = top_days.merge(grouped[['date lecture', 'id_book']].drop_duplicates(), on='date lecture', how='left') \
                                .merge(df_book_updated[['id', 'Titre']], left_on='id_book', right_on='id', how='left')
worst_days_with_titles = worst_days.merge(grouped[['date lecture', 'id_book']].drop_duplicates(), on='date lecture', how='left') \
                                   .merge(df_book_updated[['id', 'Titre']], left_on='id_book', right_on='id', how='left')

# Create figure for reading speed
fig_speed, ax_speed = plt.subplots(figsize=(12, 6))
ax_speed.plot(filtered_daily_speed['date lecture'], filtered_daily_speed['vitesse moyenne (pages/heure)'], marker='.')

ax_speed.axhline(y=mean_speed, color='red', linestyle='--', label=f'Average ({mean_speed:.0f})')
ax_speed.axhline(y=median_speed, color='green', linestyle='-.', label=f'Median ({median_speed:.0f})')
ax_speed.axhline(y=mean_speed + std_speed, color='blue', linestyle=':', label=f'+1 Std ({(mean_speed + std_speed):.0f})')
ax_speed.axhline(y=mean_speed - std_speed, color='blue', linestyle=':', label=f'-1 Std ({(mean_speed - std_speed):.0f})')

# Annotations for top/worst
for i, (_, row) in enumerate(top_days_with_titles.iterrows()):
    date = row['date lecture']
    speed = row['vitesse moyenne (pages/heure)']
    title = row['Titre']
    vertical_offset = 15 if i % 2 == 0 else -15
    ax_speed.annotate(f"{title}", (date, speed), textcoords="offset points", xytext=(0, vertical_offset),
                      ha='center', fontsize=10, color='purple', alpha=0.55, arrowprops=dict(arrowstyle="->", color="purple", lw=0.5))

for i, (_, row) in enumerate(worst_days_with_titles.iterrows()):
    date = row['date lecture']
    speed = row['vitesse moyenne (pages/heure)']
    title = row['Titre']
    vertical_offset = -25 if i % 2 == 0 else 25
    ax_speed.annotate(f"{title}", (date, speed), textcoords="offset points", xytext=(0, vertical_offset),
                      ha='center', fontsize=10, color='orange', alpha=0.55, arrowprops=dict(arrowstyle="->", color="orange", lw=0.5))

ax_speed.set_title('Average reading speed')
ax_speed.set_xlabel("Date")
ax_speed.set_ylabel("Mean reading speed (pages/hour)")
ax_speed.grid(False)
ax_speed.legend()
plt.tight_layout()

# ====== Display in Streamlit columns ======
plt1, plt2 = st.columns(2)
with plt1:
    st.markdown(text1)
    st.pyplot(fig_time)

with plt2:
    st.markdown(text2)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.pyplot(fig_speed)


