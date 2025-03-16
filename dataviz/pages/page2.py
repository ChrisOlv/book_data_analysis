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
try:
    from menu import menu_with_redirect
except ImportError as e:
    print("ImportError:", e)


st.set_page_config(
    page_title="page2",
    page_icon="📖",
    layout="wide", #wide-screen layout
    initial_sidebar_state="collapsed", #expanded sidebar
) 

# title
# dashboard title
st.title("📚 Book data analysis - zoom")
st.subheader("Logs analysis from KO e-reader")
st.markdown("""This dashboard presents an analysis of e-book reading data.
            The data comes from the reading logs of an e-reader using Ko-reader.

            """)