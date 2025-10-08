import pandas as pd  
import plotly.express as px  
import streamlit as st 
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from datetime import timedelta
import os 
from pathlib import Path
import datetime
import calmap

# launch the script from anywhere
os.chdir(os.path.dirname(__file__))

# paths
# df_book_updated_path = Path(__file__).parent.parent / "1.data" / "2.processed" / "df_book_updated.parquet"
# df_stat_path = Path(__file__).parent.parent / "1.data" / "2.processed" / "stats_lecture.parquet"


def get_data_path(filename: str, folder="1.data/2.processed") -> Path:
    base = Path(__file__).parent.parent / folder
    file = base / filename
    demo = base / filename.replace(".parquet", "_demo.parquet")
    return file if file.exists() else demo

df_book_updated_path = get_data_path("df_book_updated.parquet")
df_stat_path = get_data_path("stats_lecture.parquet")

# excel option
base_path = Path(__file__).parent.parent / "1.data" / "1.raw" / "paper_audio"
file_path = base_path / "paper_audio.xlsx"
demo_path = base_path / "paper_audio_demo.xlsx"
book_paper_path = file_path if file_path.exists() else demo_path


# book_paper_path = Path(__file__).parent.parent / "1.data"/"1.raw"/"paper_audio" / "paper_audio.xlsx"

# page config
st.set_page_config(
    page_title="book log analysis",
    page_icon="📖",
    layout="wide", 
    initial_sidebar_state="collapsed",
) 
for path in [df_book_updated_path, df_stat_path, book_paper_path]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

# Cache
@st.cache_data
def load_data():
    df_book_updated = pd.read_parquet(df_book_updated_path)
    df_stat = pd.read_parquet(df_stat_path)
    df_book_paper = pd.read_excel(book_paper_path)
    df_book_updated['Date de lecture'] = pd.to_datetime(df_book_updated['Date de lecture'], format="%Y-%m-%dT%H:%M:%S.%fZ")
    df_book_paper['date de lecture'] = pd.to_datetime(df_book_paper['date de lecture'],dayfirst=True,errors="coerce")
    df_book_paper = df_book_paper.dropna(subset=['date de lecture'])
    return df_book_updated, df_book_paper, df_stat

df_book_updated, df_book_paper, df_stat = load_data()
df_for_graph = df_book_updated.copy()

# dashboard title
st.title("📚 Book Data Analysis")
st.subheader("Exploring my KO e-reader reading stats")
st.markdown("""From page flips to patterns: diving into my reading journey with KO-reader. 
Every session, every book, every page, now visualized.""")

# Sidebar : filters
with st.sidebar:
    st.header("Chart parameters ⚙️")
    filter_annee = st.multiselect('Year', ['2023', '2024', '2025', "last 12 months"], default=['2024'])
    livre_termine = st.radio("Reading status", options=["read", "unfinished", "read + unfinished"])
    filter_auteur = st.multiselect('Author', df_book_updated['Auteurs'].unique())
    filter_title = st.multiselect('Title', df_book_updated['Titre'].unique())
    filter_category1 = st.multiselect('Category', df_book_updated['category1'].unique())
    filter_category2 = st.multiselect('Subcategory', df_book_updated['category2'].unique())

    st.markdown("---")
    st.markdown(
        '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/christopheoliveres/">@chris</a></h6>',
        unsafe_allow_html=True,
    )

# apply year filter function
def filter_by_year(df, date_col, filter_val):
    if not filter_val:
        return df
    if filter_val == ["last 12 months"]:
        return df[df[date_col] > df[date_col].max() - timedelta(days=365)]
    else:
        return df[df[date_col].dt.year.astype(str).isin(filter_val)]

df_book_updated = filter_by_year(df_book_updated, 'Date de lecture', filter_annee)
df_book_paper = filter_by_year(df_book_paper, 'date de lecture', filter_annee)
df_stat = filter_by_year(df_stat, 'date lecture', filter_annee)

# status filter
if livre_termine == "read":
    df_book_updated = df_book_updated[df_book_updated['% lu'] == 100]
elif livre_termine == "unfinished":
    df_book_updated = df_book_updated[df_book_updated['% lu'] != 100]


# auteur filter
if filter_auteur:
    df_book_updated = df_book_updated[df_book_updated['Auteurs'].isin(filter_auteur)]
if filter_title:
    df_book_updated = df_book_updated[df_book_updated['Titre'].isin(filter_title)]
if filter_category1:
    df_book_updated = df_book_updated[df_book_updated['category1'].isin(filter_category1)]
if filter_category2:
    df_book_updated = df_book_updated[df_book_updated['category2'].isin(filter_category2)]


# DATAVIZ PREPARATION 

# count category
category_counts = df_book_updated['Catégorie'].value_counts().reset_index()
category_counts.columns = ['Catégorie', 'nombre de livre']

# Bar chart
category_counts_sorted = category_counts.sort_values(by='nombre de livre', ascending=True)

fig0 = px.bar(category_counts_sorted,
             x='nombre de livre', 
             y='Catégorie',
             orientation='h',
             title='Books by Genre',
             labels={'nombre de livre': 'Number of books', 'Catégorie': ''},
             text_auto=True
             
             )
fig0.update_traces(textposition="inside")
fig0.update_layout(xaxis=dict(
        showticklabels=False,  
        zeroline=False,     
        showline=False,
        title=''  

    ),
    title=dict(
        text='Books by Genre',  
        x=0.5,                        
        xanchor='center',
        yanchor='top',
        pad=dict(t=5, b=0)            
    ),
    margin=dict(t=50, l=20, r=20, b=20), 
)

# count read per month
df_book_updated['end_date'] = pd.to_datetime(df_book_updated['end_date'], errors='coerce')

df_book_updated['month'] = df_book_updated['end_date'].dt.strftime('%B')
df_book_updated['month_num'] = df_book_updated['end_date'].dt.month
mois_ordres = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
df_book_updated['month'] = pd.Categorical(df_book_updated['month'], categories=mois_ordres, ordered=True)

books_per_month = df_book_updated.groupby(['month', 'month_num']).size().reset_index(name='nombre de livres')


books_per_month = books_per_month.sort_values(by='month_num',ascending=True)

# Bar chart
fig1 = px.bar(books_per_month,
              x='nombre de livres', 
              y='month',
              orientation='h',
              title='Books Read per Month',
              labels={'nombre de livres': 'Nombre de livres', 'month': 'Month'},
              text='nombre de livres',
              text_auto=True
)


fig1.update_traces(textposition="inside",

                   textangle=0
                    
                )
fig1.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=mois_ordres,autorange="reversed",title=""),  
    xaxis=dict(
        showticklabels=False,  
        zeroline=False,        
        showline=False,
        title=''),              
        bargap=0.1,  
        
    )

# month reading time

time_per_month = df_book_updated.groupby(['month', 'month_num'])['temps passé sur le livre en heure'].sum().reset_index(name='Temps de lecture en heure').round(0)
books_per_month = books_per_month.sort_values(by='month_num',ascending=True)
# Bar chart
fig2 = px.bar(time_per_month,
              x='Temps de lecture en heure', 
              y='month',
              orientation='h',
              title='Monthly Reading Hours',
              labels={'Temps de lecture en heure': 'Hours of reading', 'month': 'Month'},
              text='Temps de lecture en heure',
              text_auto=True
)


fig2.update_traces(textposition="inside",
                   textfont=dict(size=12),  
                   cliponaxis=False,
                   textangle=0 
                )

fig2.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=mois_ordres,autorange="reversed",title=""),  
    xaxis=dict(
        showticklabels=False,  
        zeroline=False,        
        showline=False,
        title=''),
    title=dict(
        text='Monthly Reading Hours',  
        x=0.5,                        
        xanchor='center',
        yanchor='top',
        pad=dict(t=5, b=0)            
    ),
    margin=dict(t=50, l=20, r=20, b=20),             
        bargap=0.1,  
    )

# 1/ longest read

temps_maxi = df_book_updated[df_book_updated["temps passé sur le livre en heure"] == df_book_updated["temps passé sur le livre en heure"].max()]

titre_max_temps_lecture = df_book_updated[df_book_updated["temps passé sur le livre en heure"] == df_book_updated["temps passé sur le livre en heure"].max()]["Titre"].str.title().values[0].split('-')[0].strip()
auteur_max_temps_lecture = " ".join(
    df_book_updated[df_book_updated["temps passé sur le livre en heure"] 
                    == df_book_updated["temps passé sur le livre en heure"].max()]["Auteurs"]
    .str.title()
    .values[0]
    .split()[:3]
)
temps_max_lecture = df_book_updated["temps passé sur le livre en heure"].max()



# 3/ fastest
livre_rapide = df_book_updated[df_book_updated["temps passé sur le livre en minute"] > 35]
livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]

titre_livre_rapide = livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["Titre"].str.title().values[0]
auteur_livre_rapide = " ".join(
    livre_rapide[livre_rapide["pages lues à la minute"] == 
                 livre_rapide["pages lues à la minute"].max()]["Auteurs"]
    .str.title()
    .values[0]
    .split()[:3]
)


vitesse_livre_rapide =livre_rapide[livre_rapide["pages lues à la minute"] == livre_rapide["pages lues à la minute"].max()]["pages lues à la minute"].values[0].round(1)

# 4/ Addictive
livre_addict = df_book_updated[df_book_updated["minutes de lecture/jl"] == df_book_updated["minutes de lecture/jl"].max()]
titre_livre_addict = livre_addict["Titre"].str.title().values[0]
auteur_livre_addict = livre_addict["Auteurs"].str.title().values[0]
minutes_livre_addict = livre_addict["minutes de lecture/jl"].values[0]


nb_livres_lus = df_book_updated[df_book_updated['% lu'] == 100].shape[0]
nb_livres_lus_papier = df_book_paper.shape[0]


nb_auteurs_lus = df_book_updated[df_book_updated['% lu'] == 100]["Auteurs"].nunique()
nb_auteurs_lus_papier = df_book_paper["Auteurs"].nunique()



# =====Day of the Week Analysis=======


# count hours per day of the week
df_stat['Date de lecture'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")
df_stat['day_of_week'] = df_stat['Date de lecture'].dt.day_name()
books_per_day_week = df_stat.groupby('day_of_week')['Temps de lecture en heure'].sum().round(0).reset_index(name='hours of reading')

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
books_per_day_week['day_of_week'] = pd.Categorical(books_per_day_week['day_of_week'], categories=days_order, ordered=True)


fig3 = px.bar(books_per_day_week,
              y='day_of_week',
              x='hours of reading',
              orientation='h',
              title='Weekly Reading Hours',
              labels={'hours of reading': 'hours of reading', 'day_of_week': ''},
              text='hours of reading',
              text_auto=True
)
fig3.update_traces(textposition="inside",cliponaxis=False,)
fig3.update_layout(
    xaxis=dict(
        showticklabels=False,  
        zeroline=False,       
        showline=False,
        title='',
    ),
    yaxis=dict(
        categoryorder="array", categoryarray=days_order,autorange="reversed" 
        ),
    title=dict(
        text='Weekly Reading Hours',  
        x=0.5,                        
        xanchor='center',
        yanchor='top',
        pad=dict(t=5, b=0)          
    ),
    margin=dict(t=50, l=20, r=20, b=20)            
)


# ======Day of the Week Analysis=======
# =====hour of the day Analysis =======


# count read by bins of hours


df_stat['hour_of_day'] = df_stat['heure de début'].dt.hour

bins = [i for i in range(0, 25, 2)]
labels = [f'{str(i).zfill(2)}h-{str(i+2).zfill(2)}h' for i in range(0, 24, 2)]
df_stat['tranche_horaire'] = pd.cut(df_stat['hour_of_day'], bins=bins, labels=labels, right=False)


books_per_hour = df_stat.groupby('tranche_horaire')['Temps de lecture en heure'].sum().reset_index(name='total_reading_time').round(1)



fig5, ax = plt.subplots(figsize=(12, 6))

# books_per_hour calculated
fig5 = px.area(
    books_per_hour,
    x='tranche_horaire',
    y='total_reading_time',
    labels={'tranche_horaire': 'Hour of the Day', 'total_reading_time': 'Reading Time (hours)'},
    title='Density of Reading Time by Hour of Day',
    line_shape='spline'
)

fig5.update_layout(
    xaxis=dict(tickmode='linear',tickangle=45,title=""),
    yaxis=dict(title='Reading Time (hours)'),
    font=dict(family='Arial', size=14)

)



# ======Day of the Week Analysis=======

### scatter plot fig4



tdf_books_plot = df_book_updated.copy()

tdf_books_plot['vitesse_lecture'] = tdf_books_plot['# pages lues'] / tdf_books_plot['temps passé sur le livre en minute']
# Remove outliers
tdf_books_plot = tdf_books_plot[
    (tdf_books_plot['vitesse_lecture'] < 6) &
    (tdf_books_plot['temps passé sur le livre en minute'] > 35)
]
# Scatter plot : Temps passé vs Vitesse de lecture
fig4 = px.scatter(
    tdf_books_plot,
    x='temps passé sur le livre en minute',  
    y='vitesse_lecture',                     
    color='category2',                 
    hover_data=['Titre', 'Auteurs', 'Catégorie', 'série', 'Durée lecture (j)'],
    labels={
        'temps passé sur le livre en minute': 'Total Time Spent (minutes)',
        'vitesse_lecture': 'Reading Speed (pages/minute)',
        'category2': 'Genre'
    },
    title='Reading Speed vs Total Time Spent per Book',
    size_max=30,
    color_discrete_sequence=px.colors.qualitative.Set2  
)



# add le hovertemplate
fig4.update_traces(
    hovertemplate=
    "<b>Title:</b> %{customdata[0]}<br>" +
    "<b>Author:</b> %{customdata[1]}<br>" +
    "<b>Genre:</b> %{customdata[2]}<br>" +
    "<b>Reading days:</b> %{customdata[4]}<br>" +
    "<b>Speed:</b> %{y:.2f} pages/min<br>" +
    "<b>Time spent:</b> %{x} min<extra></extra>",
    customdata=tdf_books_plot[['Titre','Auteurs','category2','série','Durée lecture (j)']].values
)

# Layout
fig4.update_layout(
    font=dict(family='Arial', size=14)
)




###

# KPIs/summary cards
# create 4 columns
kpi1, kpi2, kpi3, kpi4,kpi5 = st.columns(5)
text1, text2, text3, text4,text5 = st.columns(5)
table = st.columns(1)


# order
chart1, chart4,chart6,chart2 = st.columns(4)
chart7,chart8 = st.columns(2)
chart3 = st.columns(1)

with chart7:

    st.write(fig4)
with chart6:

    fig = fig3
    st.write(fig)
with chart8:

    fig = fig5
    st.write(fig)

# 1/ longest read 
kpi1.metric(
    label="# Marathon Read (hours)",
    value=round(temps_max_lecture),
    help=("hours")
    )

text1.markdown(f"""
<div style= line-height: 1.2;">
    <div style="font-size:14px; font-weight:600;color:#555;">{titre_max_temps_lecture}</div>
    <div style="font-size:12px; color:#555;">{auteur_max_temps_lecture}</div>
</div>
""", unsafe_allow_html=True)



# 2/ fastest
kpi2.metric(
    label="# Page turner (p/min)",
    value=vitesse_livre_rapide,
    help=("pages read per minute")
    )
    # stylisation moderne du titre et de l'auteur
text2.markdown(f"""
<div style= line-height: 1.2;">
    <div style="font-size:14px; font-weight:600;color:#555;">{titre_livre_rapide}</div>
    <div style="font-size:12px; color:#555;">{auteur_livre_rapide}</div>
</div>
""", unsafe_allow_html=True)

    # text2.markdown(titre_livre_rapide+" de "+auteur_livre_rapide)


# 3/ addictive
kpi3.metric(
    label="# Daily Obsessed (min/day)",
    value=round(minutes_livre_addict),
    help=("reading minutes per day")
    )

text3.markdown(f"""
<div style= line-height: 1.2;">
    <div style="font-size:14px; font-weight:600;color:#555;">{titre_livre_addict}</div>
    <div style="font-size:12px; color:#555;">{auteur_livre_addict}</div>
</div>
""", unsafe_allow_html=True)

#4/ auteurs et books
kpi4.metric(
    label="# e-Books Read",
    value=nb_livres_lus
    )

text4.markdown(f"""
<div style= line-height: 1.2;">
    <div style="font-size:14px; font-weight:600;color:#555;">by {nb_auteurs_lus}  different authors</div>

</div>
""", unsafe_allow_html=True)



kpi5.metric(
    label="# paper Books Read",
    value=nb_livres_lus_papier
    )
text5.markdown(f"""
<div style= line-height: 1.2;">
    <div style="font-size:14px; font-weight:600;color:#555;">by {nb_auteurs_lus_papier}  different authors</div>

</div>
""", unsafe_allow_html=True)


st.markdown("## Book table")

with chart1:

    fig = fig0
    st.write(fig)


with chart2:
    st.plotly_chart(fig1) 


with chart4:

    st.plotly_chart(fig2) 

# 5/ table without erros
auteurs_a_exclure = [] 
titres_a_exclure = ["ERROR: Error reading EPUB format"]
df_print = df_book_updated[~df_book_updated['Auteurs'].isin(auteurs_a_exclure)]
df_print = df_print[~df_print['Titre'].isin(titres_a_exclure)]
df_print['Date de lecture'] = df_print['Date de lecture'].dt.strftime('%Y-%m-%d')

st.markdown("e-Books read during the period :")
st.dataframe(
    df_print[["Titre","Auteurs","Catégorie","Date de lecture","Year rel", "# pages lues","pages lues à la minute","Durée lecture (j)", "jours de lecture effectifs (jl)", "# pages lues/jl","temps passé sur le livre en heure","minutes de lecture/jl" ]],
             hide_index=True,
             height=500,
             )
st.markdown("## Paper Books")
df_book_paper["date de lecture"] = pd.to_datetime(df_book_paper["date de lecture"]).dt.date

# this should be done during the ETL phase #TODO
df_book_paper = df_book_paper.rename(columns={
    "Titre": "Title",
    "Auteurs": "Authors",
    "date de lecture": "Reading Date",
    "# pages lues":"# pages read",
})

df_book_paper = df_book_paper.sort_values(by="Reading Date", ascending=False)

st.dataframe(
    df_book_paper[["Title","Authors","Reading Date","# pages read","format"]]
                  ,hide_index=True)


# ===== HEATMAP =====
st.markdown("## Heatmap")

# heatmap 
df_stat = df_stat
df_stat['date lecture'] = pd.to_datetime(df_stat['date lecture'])
df_aggregated = df_stat.groupby('date lecture')['Temps de lecture en minute'].sum().reset_index()
df_serie = df_aggregated.set_index('date lecture')['Temps de lecture en minute']

df_serie = df_serie.asfreq('D', fill_value=0)

# filter_annee 
if filter_annee == ["last 12 months"]:
    annee = df_serie.index.max().year
elif filter_annee == [] :
    annee = df_serie.index.max().year
else:
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
        daylabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 
        dayticks=[0, 1, 2, 3, 4, 5, 6], monthly_border=False,
    )

    
    
    plt.title('Year of reading')

    st.pyplot(plt)


create_calmap(df_serie)
# ====== end heatmap =====


# ===== MATRICE =====


df_stat['Date de lecture en jour'] = pd.to_datetime(df_stat['date lecture'], format="%Y-%m-%d")

temps_quotidien_moyen_ALL = df_stat["Temps passé sur la page en seconde"].sum() / df_stat["Date de lecture en jour"].nunique()/60 # c

temps_quotidien_moyen_lastday = df_stat[df_stat["Date de lecture en jour"] == df_stat["Date de lecture en jour"].max()]["Temps passé sur la page en seconde"].sum()/60

# reading time last 3 days (df_stat)
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


# average page read

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

# read speed
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

# columns and index
columns = ['Overall', 'Yesterday', 'Last 3 days', 'Last week', 'Last month', 'Last 12 months', 'Year-to-date']
index = ['⏱️ Avg. Reading Time (min)', '📖 Avg. Pages Read / Day', '⚡ Reading Speed (pages/hour)']

matrice = pd.DataFrame(data, columns=columns, index=index)
matrice = matrice.fillna(0)
matrice = matrice.astype(int)

# Style
matrice_styled = matrice.style.format("{:.0f}").set_properties(**{
    'font-size': '14px', 'text-align': 'center', 'font-weight': 'bold'
})


st.markdown("## Reading Insights Matrix")
st.dataframe(matrice_styled, hide_index=False)


# ====== end matrice =====

st.markdown("---")
st.markdown("""
## 📚 Reading Timeline & Daily Sessions

This section visualizes how my reading unfolds over time.  

- The **timeline chart** shows when each book was started and finished, giving a sense of overlaps and reading pace.  
- The **daily session chart** breaks down reading intervals by hour, highlighting session lengths, gaps, and activity patterns throughout the year.
""")




# =====timeline of reading=======
plt.figure(figsize=(18, 9))  

df_book_updated['start_date'] = pd.to_datetime(df_book_updated['start_date'])
df_book_updated['end_date'] = pd.to_datetime(df_book_updated['end_date'])

# space
espacement_vertical = 1
positions = [i * espacement_vertical for i in range(len(df_book_updated))]

# Mapping catégorie
categories = df_book_updated['Catégorie'].unique()
colors = px.colors.qualitative.Set2
def rgb_to_hex(rgb_str):
    rgb = [int(x) for x in rgb_str.strip("rgb()").split(",")]
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

color_map = {cat: rgb_to_hex(colors[i % len(colors)]) for i, cat in enumerate(categories)}


for pos, (_, row) in zip(positions, df_book_updated.iterrows()):
    couleur = color_map[row['Catégorie']]
    plt.plot([row['start_date'], row['end_date']], [pos, pos], marker='o', color=couleur)
    plt.text(row['end_date'], pos, f" {row['Titre']}", va='center', fontsize=9)

plt.xlabel('')
plt.suptitle('Timeline of Reading', fontsize=16, y=1)
plt.title('Dots represent starting and ending date', fontsize=12, y=1)
plt.yticks([])


ax = plt.gca()
for spine in ax.spines.values():
    spine.set_visible(False)

plt.grid(axis='x', linestyle='--', alpha=0.7)


months = pd.date_range(df_book_updated['start_date'].min(), df_book_updated['end_date'].max(), freq='MS')
month_labels = [m.strftime('%b') for m in months]
plt.xticks(months, month_labels, rotation=0)

# Legend
legend_elements = [Line2D([0], [0], color=color_map[cat], marker='o', linestyle='-', label=cat, markersize=8) for cat in categories]
plt.legend(handles=legend_elements, loc='upper right', title='Category')

plt.tight_layout()
plt.show()
st.pyplot(plt)

# ======end timeline of reading=====



# =====sessions de lecture=======

# Convertir les colonnes en datetime
df_stat['heure de début'] = pd.to_datetime(df_stat['heure de début'])
df_stat['date de fin de lecture'] = pd.to_datetime(df_stat['date de fin de lecture'])

# Filter
df_stat = df_stat.sort_values(by='heure de début')

# calculate diff between logs and assign session_id
df_stat['diff_minutes'] = df_stat['heure de début'].diff().dt.total_seconds() / 60
session_threshold = 20
df_stat['session_id'] = (df_stat['diff_minutes'] > session_threshold).cumsum()

# group sessions
sessions = df_stat.groupby('session_id').agg({
    'id_book': 'first',
    'heure de début': 'min',
    'date de fin de lecture': 'max',
    'Temps passé sur la page en seconde': 'sum',
    'page': ['min','max'],
    'id_long': 'first'
})
sessions.columns = ['_'.join(col).strip() for col in sessions.columns]
sessions = sessions.reset_index()

# Merge
sessions_with_titles = sessions.merge(
    df_book_updated[['id','Titre','Catégorie']],
    left_on='id_book_first',
    right_on='id',
    how='left'
)
sessions_with_titles.drop(columns=['id'], inplace=True)


sessions_with_titles["nombre de pages lues"] = sessions_with_titles["page_max"] - sessions_with_titles["page_min"] + 1
sessions_with_titles["Temps de lecture en minute"] = (sessions_with_titles["Temps passé sur la page en seconde_sum"]/60).round(2)
sessions_with_titles['heure de fin'] = sessions_with_titles['heure de début_min'] + pd.to_timedelta(sessions_with_titles['Temps passé sur la page en seconde_sum'], unit='s')

if filter_annee == ["last 12 months"] or filter_annee == []:
    année_plot = df_stat['date lecture'].dt.year.max()
else:
    année_plot = int(filter_annee[0])

session_plot = sessions_with_titles[sessions_with_titles['heure de début_min'].dt.year == année_plot]
session_plot_droped = session_plot[session_plot['heure de début_min'].dt.day == session_plot['heure de fin'].dt.day]

# hours in seconds
def time_to_seconds(t):
    return t.hour*3600 + t.minute*60 + t.second
session_plot_droped['heure_debut_sec'] = session_plot_droped['heure de début_min'].dt.time.apply(time_to_seconds)
session_plot_droped['heure_fin_sec'] = session_plot_droped['heure de fin'].dt.time.apply(time_to_seconds)


categories = session_plot_droped['Catégorie'].unique()
colors = px.colors.qualitative.Set2
color_map = {}
for i, cat in enumerate(categories):
    rgb_str = colors[i % len(colors)]  
    rgb_tuple = tuple(int(x) for x in rgb_str[4:-1].split(','))
    hex_color = mcolors.to_hex([c/255 for c in rgb_tuple])
    color_map[cat] = hex_color


# Mapping catégorie
categories = session_plot_droped['Catégorie'].unique()
colors = px.colors.qualitative.Set2


# Plot
plt.figure(figsize=(18,10))
for _, row in session_plot_droped.iterrows():
    couleur = color_map[row['Catégorie']]
    plt.plot([row['heure de début_min'].date(), row['heure de début_min'].date()],
             [row['heure_debut_sec'], row['heure_fin_sec']],
             marker='o', color=couleur, linestyle='-')

# Axe Y : hours
ticks = [i*3600 for i in range(24)]
labels = [f'{i:02d}:00' for i in range(24)]
plt.yticks(ticks, labels)
plt.ylim(0, 24*3600-1)
plt.ylabel('Hour (HH:MM)')

# Axe X : month
session_plot_droped['month'] = session_plot_droped['heure de début_min'].dt.strftime('%b')
months_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
month_positions = session_plot_droped.groupby('month')['heure de début_min'].min().reindex(months_order)
plt.xticks(ticks=month_positions.values, labels=month_positions.index, rotation=0)

plt.xlabel('')
plt.title("Each colored line represents a reading session interval", fontsize=12)
plt.suptitle(f'Daily session chart in {année_plot}', y=1, fontsize=16)

# Légend
legend_elements = [Line2D([0],[0], color=color_map[cat], marker='o', linestyle='-', label=cat) for cat in categories]
plt.legend(handles=legend_elements, loc='upper right', title='Category')

plt.grid(True)
plt.tight_layout()
plt.show()
st.pyplot(plt)


# ======session de  lecture=====


# ======session analyse=====
number_of_reading_session = session_plot.shape[0]

moyenne_temps_lecture_par_sessions_minutes = (session_plot["Temps passé sur la page en seconde_sum"].mean()/60).round(2)

nombre_de_sessions_par_jour_moyen = session_plot["heure de début_min"].dt.date.value_counts().mean().round(1)

session_plus_longue_minutes = session_plot["Temps passé sur la page en seconde_sum"].max()/60

sessions_de_plus_de_30_minutes = session_plot[session_plot["Temps passé sur la page en seconde_sum"] > 30*60].shape[0]
sessions_de_plus_de_60_minutes = session_plot[session_plot["Temps passé sur la page en seconde_sum"] > 60*60].shape[0]
sessions_de_moins_de_15_minutes = session_plot[session_plot["Temps passé sur la page en seconde_sum"] < 15*60].shape[0]
sessions_de_moins_de_5_minutes = session_plot[session_plot["Temps passé sur la page en seconde_sum"] < 5*60].shape[0]


### YEAR COMPARAISON

st.markdown("---")
st.markdown("### Yearly Reading Comparison")
st.markdown("Comparison of reading activity across two consecutive years. This chart ignore filters.")

current_year = 2025
comparison_year = 2024


# VARIABLES
## 1/ started books
nb_livre_current_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['Titre'].nunique()
nb_livre_comparison_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['Titre'].nunique()
## 2/ terminated books 
nb_livre_current_year_lus = df_for_graph[
    (df_for_graph['Date de lecture'].dt.year == current_year) & 
    (df_for_graph['% lu'] == 100)
]['Titre'].nunique()

nb_livre_comparison_year_lus = df_for_graph[
    (df_for_graph['Date de lecture'].dt.year == comparison_year) & 
    (df_for_graph['% lu'] == 100)
]['Titre'].nunique()
ratio_lu_current = round((nb_livre_current_year_lus / nb_livre_current_year) * 100)
ratio_lu_comparison = round((nb_livre_comparison_year_lus / nb_livre_comparison_year) * 100)

## 3/ count authors
nb_auteurs_current_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['Auteurs'].nunique()
nb_auteurs_comparison_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['Auteurs'].nunique()
ratio_auteurs_current_year = round((nb_auteurs_current_year / nb_livre_current_year) * 100)
ratio_auteurs_comparison_year = round(( nb_auteurs_comparison_year/nb_livre_comparison_year)*100)

nb_auteurs_current_year_only = df_for_graph[
    (df_for_graph['Date de lecture'].dt.year == current_year) &
    (df_for_graph['Auteurs'].isin(df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['Auteurs']) == False)
]['Auteurs'].nunique()

nb_auteurs_comparison_year_only = df_for_graph[
    (df_for_graph['Date de lecture'].dt.year == comparison_year) &
    (df_for_graph['Auteurs'].isin(df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['Auteurs']) == False)
]['Auteurs'].nunique()

## 4/ page number
### nombre de pages total
nb_page_current_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['# pages lues'].sum()
nb_page_comparison_year = df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['# pages lues'].sum()

### nombre de page par livre en moyenne
nb_page_moyen_current_year = round(df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['# pages lues'].mean())
nb_page_moyen_comparison_year = round(df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['# pages lues'].mean())

## 5/ temps de lecture
### somme temps de lecture
temps_lecture_current_year = (df_for_graph[df_for_graph['Date de lecture'].dt.year == current_year]['temps passé sur le livre en minute'].sum())/60
temps_lecture_comparison_year = round((df_for_graph[df_for_graph['Date de lecture'].dt.year == comparison_year]['temps passé sur le livre en minute'].sum())/60)

### temps de lecture par jour # temps de lecture / nombre de jours entre le 1er janvier et aujourd'hui
days_elapsed = (datetime.date.today() - datetime.date(current_year, 1, 1)).days

temp_lecture_par_jour = temps_lecture_current_year / days_elapsed
temps_lecture_par_jour_comparison_year = temps_lecture_comparison_year / 365
### vitesse de lecture


# df plot
data = {
    comparison_year: [
        f"{nb_livre_comparison_year} Books Started",
        f"{nb_livre_comparison_year_lus} Books Finished<br>{ratio_lu_comparison}%",
        f"{nb_auteurs_comparison_year} Authors<br>{ratio_auteurs_comparison_year}% Authors / Books<br>{nb_auteurs_comparison_year_only} Unique Authors",
        f"{nb_page_comparison_year} Pages Read<br>{nb_page_moyen_comparison_year} Avg Pages/Book",
        f"{temps_lecture_comparison_year}h Total Reading<br>~{round(temps_lecture_par_jour_comparison_year*60)} min/day"
    ],
    " ": ["", "", "🆚", "", ""],
    current_year: [
        f"{nb_livre_current_year} Books Started",
        f"{nb_livre_current_year_lus} Books Finished<br>{ratio_lu_current}%",
        f"{nb_auteurs_current_year} Authors<br>{ratio_auteurs_current_year}% Authors / Books<br>{nb_auteurs_current_year_only} New Authors",
        f"{nb_page_current_year} Pages Read<br>{nb_page_moyen_current_year} Avg Pages/Book",
        f"{round(temps_lecture_current_year)}h Total Reading<br>~{round(temp_lecture_par_jour*60)} min/day"
    ]
}

df = pd.DataFrame(data)

# df HTML
html_table = df.style.set_table_styles([
    {
        'selector': 'table, th, td',
        'props': [
            ('border', '0px'), 
            ('padding', '10px 100px') 
        ]
    }
]).hide(axis="index").to_html()


# display table
st.markdown(html_table, unsafe_allow_html=True)

### END YEAR COMPARAISON
st.markdown("---")
st.markdown(f"### Reading session KPI in {année_plot}")
st.markdown("One session is a group of records with a threshold of "+str(session_threshold)+" minutes of inactivity")



kpi_values = {
    "Number of Reading Sessions": number_of_reading_session,
    "Avg Reading Time per Session (min)": round(moyenne_temps_lecture_par_sessions_minutes),
    "Avg Sessions per Day": round(nombre_de_sessions_par_jour_moyen,1),
    "Longest Session (min)": round(session_plus_longue_minutes),
    "Sessions > 30 min": sessions_de_plus_de_30_minutes,
    "Sessions > 60 min": sessions_de_plus_de_60_minutes,
    "Sessions < 15 min": sessions_de_moins_de_15_minutes,
    "Sessions < 5 min": sessions_de_moins_de_5_minutes
}

# Display KPIs in 3 columns
cols = st.columns(4)
for i, (label, value) in enumerate(kpi_values.items()):
    cols[i % 4].metric(label, value)


# prepare un canevas pour 4 plots
fig, axs = plt.subplots(2, 2, figsize=(12, 12))
fig.suptitle('Distribution of reading time per session')
fig.text(0.5, 0.95, f'Year {année_plot}, number of session : {number_of_reading_session} ', ha='center')

# plot 1 : Distribution des temps de lecture par catégorie
sns.violinplot(data=session_plot, y='Temps de lecture en minute', x='Catégorie', ax=axs[0, 0])
axs[0, 0].set_title('Session by category')
axs[0, 0].set_xlabel('Category')
axs[0, 0].tick_params(axis='x', rotation=45)
axs[0, 0].set_ylabel('Reading time in minutes')
# y axis every 30 min
axs[0, 0].set_yticks(range(0, 300, 30))

# plot 2 : Distribution des temps de lecture par mois de lecture
sns.violinplot(data=session_plot, y='Temps de lecture en minute', x=session_plot["heure de début_min"].dt.month, ax=axs[0, 1])
axs[0, 1].set_title('Session by month')
axs[0, 1].set_ylabel('Reading time in minutes')
axs[0, 1].set_xlabel('Month of reading')
axs[0, 1].set_yticks(range(0, 300, 30))

# plot 3 : Distribution des temps de lecture par jour de la semaine
sns.violinplot(data=session_plot, y='Temps de lecture en minute', x=session_plot["heure de début_min"].dt.dayofweek, ax=axs[1, 0])
axs[1, 0].set_title('Session by day of the week')
axs[1, 0].set_ylabel('Reading time in minutes')
axs[1, 0].set_xlabel('Day of the week')
axs[1, 0].set_yticks(range(0, 300, 30))

# plot 4 : Distribution des temps de lecture par heure de début de session
sns.violinplot(data=session_plot, y='Temps de lecture en minute', x=session_plot["heure de début_min"].dt.hour, ax=axs[1, 1])
axs[1, 1].set_title('Session by hour of reading')
axs[1, 1].set_ylabel('Reading time in minutes')
axs[1, 1].set_xlabel('Start hour of session')
axs[1, 1].set_yticks(range(0, 300, 30))


plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

st.pyplot(plt)

# ======finsession de lecture=====


### la fin ###