book_data_analysis

# Python script
"script_1_update" is the main script.
Main steps : 
1. get info from the sqlite db
2. prepare and clean data
3. generate categories / sub categories from gpt4o llm
4. generate 2 parquet files : books and logs

# Power BI dashboard
The report connect to the 2 parquets files + the excel "paper books" (#TODO : rename et format this file)
## power query parameters :
absolute path : define the path of the local repo on your machine. Change it when your change your machine

# tuto

## tuto first instal

## tuto update data :
1. paste the statistics.sqlite3 file from your KO e-reader into the folder "sqlite/update"
2. execute the script





#### duplicates book
Ereader oftentimes create duplicate when you mess with calibre.
To regroup books I use this method : 
DEPRECATED.
#TODO : book cleaned once directly in the sql db



### Update : 
overwrite the statistic.sqlite3 file from your e-reader.
you can add paper book using the xls files (experimental)

### Utilisation 

## Sujets en cours de dev
Check out the github repo to get the backlog and inprogress tasks




# OLD
The following items are no longer needed. They are kept here for history.

## Power BI : 
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