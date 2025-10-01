kobo-reading-analytics/
│
├── data/                     # Dossier des données
│   ├── raw/ 
        paper-audio
        sqlite                 # Copie brute du SQLite exporté de la Kobo
│   ├── archives/         # old sqlite files
│   └── processed/            # Tables parquet finales (fact/dim/agg)
│
├── notebooks/                # Explorations rapides (optionnel)
│   └── eda.ipynb             # Analyse exploratoire initiale
│
├── transformations/          # Code de transformation
│   ├──
│   └── scripts/              # Scripts Python standalone (ETL si pas dbt)
│       ├── extract-transform.py        # Copie le SQLite de la liseuse → data/raw

│       └── validate.py       # Tests data quality (Pandera/Great Expectations)
│
├── app/                      # Application de dataviz
│   ├── app.py                # Streamlit dashboard
│   └── utils.py              # Fonctions de visualisation
│
├── orchestrator/             # Workflow orchestration
│   ├── prefect_flow.py       # Exemple avec Prefect
│   └── airflow_dag.py        # Exemple avec Airflow (bonus)
│
├── tests/                    # Tests unitaires (données & code)
│   ├── test_extract.py
│   └── test_transform.py
│
├── .github/
│   └── workflows/            # CI/CD avec GitHub Actions
│       ├── ci.yml            # Linter + tests
│       └── build.yml         # Run ETL + déploiement dashboard
│
├── Dockerfile                # Pour containeriser l’app + pipeline
├── docker-compose.yml        # Local orchestration si besoin
├── requirements.txt          # Dépendances Python
├── README.md                 # Présentation du projet
└── LICENSE
