import logging

import pandas as pd

logger = logging.getLogger(__name__)


# ----------
# HELPERS
# ----------


def drop_nulls(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    return df.dropna(subset=cols).reset_index(drop=True)


def drop_dupes(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    return df.drop_duplicates(subset=cols).reset_index(drop=True)


def texto_title(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    df_copia = df.copy()

    for col in cols:
        df_copia[col] = df_copia[col].str.strip().str.title()

    return df_copia


def texto_upper(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    df_copia = df.copy()

    for col in cols:
        df_copia[col] = df_copia[col].str.strip().str.upper()

    return df_copia


def texto_lower(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    df_copia = df.copy()

    for col in cols:
        df_copia[col] = df_copia[col].str.strip().str.lower()

    return df_copia


# ----------
# SILVER - estacoes
# ----------


def estacoes_to_silver(df_bronze: pd.DataFrame):

    df_silver = (
        df_bronze.pipe(drop_nulls, cols=["estacao_id"])
        .pipe(texto_title, cols=["nome", "cidade"])
        .pipe(drop_dupes, cols=["estacao_id"])
        .pipe(texto_upper, cols=["uf"])
        .pipe(texto_lower, cols=["status"])
    )
