# documentation here https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/

import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

df_book_updated = "df_book_updated.parquet"
df_book_streamlit = "df_book_streamlit.parquet"
df_stat = "stats_lecture.parquet"

# read parquet from a URL and keep it in cache
@st.cache_data
def get_data1() -> pd.DataFrame:
    return pd.read_parquet(df_book_updated)
# @st.cache_data
# def get_data2() -> pd.DataFrame:
#     return pd.read_parquet(df_book_streamlit)
# @st.cache_data
# def get_data3() -> pd.DataFrame:
#     return pd.read_parquet(df_stat)

df_book_updated = get_data1()

df_book_streamlit = get_data2()

df_stat = get_data3()


# page configuration

st.set_page_config(
    page_title="book log analysis",
    page_icon="📖",
    layout="wide", #wide-screen layout
)


# title
# dashboard title
st.title("book log analysis")

# top-level filters

# selectionne les années unique de la colonne end_date
Annee_lecture = st.selectbox("Select a year", pd.unique(df_book_updated["end_date"].dt.year))


