book_data_analysis

![Inspiration Image](1.inspirations/Sans%20titre.png)

# Python script
"script_1_update" is the main script.
Main steps : 
1. get info from the sqlite db
2. prepare and clean data
3. generate categories / sub categories, year of release from gpt4o llm
4. generate 3 parquet files into data_source_from_python : df_books, stats_lectures, df_book_updated 


# tuto

## tuto install or update data :
1. paste the statistics.sqlite3 file from your KO e-reader into the folder "sqlite/update"
2. execute the script (it handle the first install and the update, with incremental update).

## vizualize data : 
streamlit run app2.py
enjoy

# OLD stuff
The following items are no longer needed. They are kept here for history.

## Power BI : 
no longer used
### installation
#### path
relative path (book.xls & sqlite3) : the relative location of the local sources. Don't touch this. --> Technically, there is no need of these parameters, we can directly type the relative path in the query source.

## database v3
### workflow : 
1. mise à jours du sqlite3
2. data warehouse : 
script python qui s'active à la mise à jour du fichier sqlite3: 
récupération des tables
préparation
génération de la colonne genAI
extraction des tables en .parquet
3. power bi est connecté à ces tables
4. mise à jour de power BI en local lors de la consultation

#### category
1. faire un extract de kobo analysis / liste des livres
2. run le script "ajout_category".py
    Ce script ajoute une colonne category et utilise gpt4o pour générer la categorie et sous categorie du livre
3. l'export se retrouve dans "export xls"
4. dans kobo-analysis, la table liste_livre_category vient enrichir la table liste_livre

# credit
Dataviz style : inspired by https://erdavis.com/