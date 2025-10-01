# 📚 KO-log: My E-Reading Habit Data Pipeline & Dashboard



### Introduction

This project is a deep dive into my personal reading habits, transforming the discreet logging data from my **Kobo e-reader** (running **KOReader**) into a complete and robust data pipeline. The goal was to answer specific questions about my reading profile:
* **How much** do I really read? Am I a **sprinter** or a **marathon** reader?
* Which **authors** and **genres** do I binge?
* Are there **temporal patterns** in my reading (e.g., "more sci-fi in winter, more fantasy in spring")?

This solution demonstrates expertise across **Data Engineering**, **Data Analytics**, and **Visualization**, employing modern technologies and an efficient incremental approach.

---

## 🛠️ Technical Architecture (The Pipeline)

The project follows a four-step Extract, Transform, Load (ETL) flow, from the raw source file to the interactive dashboard.

### 1. Data Extraction & Source (SQLite)
* **Source:** The project starts by copying the `statistics.sqlite3` file from the e-reader.
    * This file contains all book metadata (`book` table) and granular reading session logs, including time spent per page flip (`page_stat_data` table).

### 2. Data Engineering & Transformation (Python, Pandas, Parquet)
A central Python script (`transfo python.py`) orchestrates the pipeline, focusing on **efficiency and quality**:
* **Cleaning:** Normalizing data and converting Unix timestamps to readable dates.
* **Incremental Pipeline:** The core logic leverages **Parquet** files (`df_book.parquet` and `stats_lecture.parquet`) to store the processed state. At each run, the script only processes **new** books or **updated** reading sessions.
* **Data Modeling:** Creating structured tables for analytics: **Fact** (reading sessions) and **Dim** (enriched book metadata).
* **Archiving:** The raw SQLite source file is automatically timestamped and archived after processing.

### 3. AI-Powered Data Enrichment (LLM, LangChain) 🤖
To fill in missing metadata (genres, publication years), a **Large Language Model (via Azure OpenAI/GPT-4o)** is seamlessly integrated into the pipeline:
* **Categorization:** Automatically detecting and classifying genres (e.g., `fiction/fantasy`, `non-fiction/history`) using a structured prompt.
* **Metadata Guessing:** Finding the `First published date` for books lacking this information.
* **Cost Optimization:** LLM calls are executed **incrementally**—only for new books or missing fields—to save tokens and minimize API expenses.

### 4. Visualization & Analytics (Streamlit)
The front-end is an interactive dashboard built with **Streamlit** for data storytelling and exploration:
* **Key Metrics:** Total reading time, books completed, average pages read per minute, and reading streaks.
* **Profile Analysis:** Charts comparing authors, genres, reading pace, and time-to-finish a book.
* **Temporal Insights:** Visualizations revealing daily and seasonal reading patterns (e.g., peak reading hours).

---

## 💻 Key Technologies

| Domain | Tool(s) | Specific Use |
| :--- | :--- | :--- |
| **Source** | **SQLite3** (KOReader log) | Raw, granular log database from the e-reader. |
| **Data Engineering** | **Python**, **Pandas** | Cleaning, transformation, and incremental logic. |
| **Storage** | **Parquet** | Columnar format for fast, efficient intermediate data storage. |
| **AI/Enrichment** | **LLM** (Azure OpenAI/GPT-4o), **LangChain** | Incremental enrichment of book metadata (genre, publication year). |
| **Visualization** | **Streamlit**, **Plotly/Matplotlib** | Interactive dashboard creation and data visualization. |

---

## 💡 Key Takeaways & Skills Demonstrated

This project serves as proof of proficiency in several core **Data & Analytics Engineering** concepts:

* **End-to-End Pipeline Design:** Building a complete data flow from a challenging source to a consumer-ready dashboard.
* **Performance & Cost Optimization:** Implementing **incremental data loading** for both processing (Parquet) and costly API calls (LLM). This is a critical skill for production environments.
* **Data Quality with AI:** Creative and practical application of LLMs for **data enrichment** to solve real-world data quality issues.
* **Analytics and Storytelling:** Transforming raw operational data into meaningful **analytics metrics** (e.g., `pages lues à la minute`, `minutes de lecture/jl`) and presenting them visually.

---

## 🚀 Getting Started (Setup)

1.  **Clone the repository**

2.  **Environment Setup**:
    # Create and activate a virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate 

    # Install dependencies
    pip install -r requirements.txt 
    
3.  **Add Your Data Source** :
    * Connect your KO-reader and copy the `statistics.sqlite3` file.
    * Place it in the directory: `1.data/1.raw/sqlite/`

4.  **Execute the Data Pipeline** :
    * *Ensure your Azure OpenAI keys and endpoint are configured in your environment variables or a `.env` file.*

5.  **Launch the Streamlit Dashboard** :
    ```bash
    streamlit run 4.app\app.py
    ```