# Supprimer les années de publications générés par IA car incohérent.

import sys
import shutil
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

SRC_PATH = "1.data/2.processed/df_book.parquet"
BACKUP_PATH = "1.data/2.processed/df_book.backup.parquet"
COL = "First published date"

def main():
    # Sauvegarde
    shutil.copy2(SRC_PATH, BACKUP_PATH)

    # Lecture
    df = pd.read_parquet(SRC_PATH, engine="pyarrow")

    if COL not in df.columns:
        raise ValueError(f"Colonne introuvable: {COL}. Colonnes: {list(df.columns)}")

    # Choix du null
    na_value = pd.NaT if is_datetime64_any_dtype(df[COL]) else pd.NA

    # Index des 20 dernières lignes (si moins de 20 lignes, prend tout)
    last_idx = df.tail(20).index

    # Remplacement
    df.loc[last_idx, COL] = na_value

    # Écriture
    df.to_parquet(SRC_PATH, engine="pyarrow", index=False)

    # Vérification
    null_count = df[COL].isna().sum()
    print(f"Terminé. Nombre de valeurs nulles dans '{COL}': {null_count}")

if __name__ == "__main__":
    sys.exit(main())