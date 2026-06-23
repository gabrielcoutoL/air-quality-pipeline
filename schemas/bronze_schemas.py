import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class BronzeEstacoes(pa.DataFrameModel):
    estacao_id: Series[str] = pa.Field(
        nullable=False, unique=True, str_matches=r"^E\d{3}$"
    )

    nome: Series[str] = pa.Field(nullable=True)

    cidade: Series[str] = pa.Field(nullable=False)

    uf: Series[str] = pa.Field(nullable=False, str_matches=r"^[A-Z]{2}$")

    latitude: Series[float] = pa.Field(nullable=False, ge=-90, le=90)
    longitude: Series[float] = pa.Field(nullable=False, ge=-180, le=180)

    data_instalacao: Series[str] = pa.Field(
        nullable=False, str_matches=r"^\d{4}-\d{2}-\d{2}$"
    )

    status: Series[str] = pa.Field(
        nullable=False, isin=["ativa", "inativa", "manutencao"]
    )

    class Config:
        strict = True
        coerce = False


class BronzeLeituras(pa.DataFrameModel):
    leitura_id: Series[str] = pa.Field(
        nullable=False, unique=True, str_matches=r"^L\d{6}$"
    )

    sensor_id: Series[str] = pa.Field(nullable=False, str_matches=r"^S\d{4}$")

    timestamp: Series[str] = pa.Field(
        nullable=False, str_matches=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
    )  # importante saber quantas leituras estão sem timestamp e quais não seguem o padrão aaaa-mm-dd hh:mm:ss

    valor: Series[str] = pa.Field(nullable=False)

    flag_qualidade: Series[str] = pa.Field(
        nullable=False, isin=["suspeita", "valida", "invalida"]
    )

    class Config:
        strict = True
        coerce = False


class BronzeLimitesParametro(pa.DataFrameModel):
    parametro: Series[str] = pa.Field(unique=True, nullable=False)

    valor_min: Series[float] = pa.Field(nullable=False, ge=0.0)

    valor_max: Series[float] = pa.Field(nullable=False, ge=0.0)

    unidade_esperada: Series[str] = pa.Field(nullable=False, isin=["ug/m3", "mg/m3"])

    @pa.dataframe_check
    def max_maior_igual_min(cls, df: pd.DataFrame) -> Series[bool]:
        return df["valor_max"] >= df["valor_min"]

    class Config:
        strict = True
        coerce = False


class BronzeSensores(pa.DataFrameModel):
    sensor_id: Series[str] = pa.Field(
        unique=True, nullable=False, str_matches=r"^S\d{4}$"
    )

    estacao_id: Series[str] = pa.Field(nullable=False, str_matches=r"^E\d{3}$")

    parametro: Series[str] = pa.Field(
        nullable=False, isin=["PM25", "PM10", "NO2", "O3", "CO", "SO2"]
    )

    unidade: Series[str] = pa.Field(nullable=False, isin=["ug/m3", "mg/m3"])

    data_calibracao: Series[str] = pa.Field(
        nullable=False, str_matches=r"^\d{4}-\d{2}-\d{2}$"
    )

    class Config:
        strict = True
        coerce = False
