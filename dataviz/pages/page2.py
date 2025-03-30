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
    df_book_updated = pd.read_parquet("../data_sources_from_python/df_book_updated.parquet")
    df_stat = pd.read_parquet("../data_sources_from_python/stats_lecture.parquet")
    df_book_paper = pd.read_excel("../paper_audio/paper_audio.xlsx")
    
    # Conversion des dates
    df_book_updated['Date de lecture'] = pd.to_datetime(df_book_updated['Date de lecture'], format="%Y-%m-%dT%H:%M:%S.%fZ")
    df_book_paper['date de lecture'] = pd.to_datetime(df_book_paper['date de lecture'], format='%d/%m/%Y')
    
    return df_book_updated, df_book_paper, df_stat

df_book_updated, df_book_paper, df_stat = load_data()


