import logging

import numpy as np
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

    d = df.copy()

    for col in cols:
        d[col] = d[col].str.strip().str.title()

    return d


def texto_upper(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    d = df.copy()

    for col in cols:
        d[col] = d[col].str.strip().str.upper()

    return d


def texto_lower(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    d = df.copy()

    for col in cols:
        d[col] = d[col].str.strip().str.lower()

    return d

def replace_text(df: pd.DataFrame, mapa: dict) -> pd.DataFrame:

    d = df.copy()

    d.replace(mapa)

    return d

def anular_fora_de_faixa(df, col: str, minimo: float, maximo: float) -> pd.DataFrame:
    
    d = df.copy()
    fora = ~d[col].between(minimo, maximo)
    logger.info(f"{col}: anulando {fora.sum()} valor(es) fora de [{minimo}, {maximo}]")
    d.loc[fora, col] = np.nan

    return d

def anula_data_futura(df, col: str) -> pd.DataFrame:
    
    d = df.copy()

    fora = d[col] > pd.Timestamp.now()

    d.loc[fora, col] = np.nan

    return d

# ----------
# SILVER - estacoes
# ----------

def estacoes_to_silver(df_bronze: pd.DataFrame):

    mapa_status = {"ativo": "ativa", "desativada": "inativa", "manutenção": "manutencao"}

    df_silver = (
        df_bronze.pipe(drop_nulls, cols=["estacao_id"])
        .pipe(texto_title, cols=["nome", "cidade"])
        .pipe(drop_dupes, cols=["estacao_id"])
        .pipe(texto_upper, cols=["uf"])
        .pipe(texto_lower, cols=["status"])
        .pipe(replace_text, mapa=mapa_status)
        .pipe(anular_fora_de_faixa, col= "latitude", minimo= -90, maximo= 90)
        .pipe(anular_fora_de_faixa, col= "longitude", minimo= -180, maximo= 180)
        .pipe(anula_data_futura, col= "data_instalacao")
    )

    return df_silver
