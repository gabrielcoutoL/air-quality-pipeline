import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class SilverEstacoes(pa.DataFrameModel):
    estacao_id: Series[str] = pa.Field(
        nullable=False, unique=True, str_matches=r"^E\d{3}$"
    )

    nome: Series[str] = pa.Field(nullable=True)

    cidade: Series[str] = pa.Field(nullable=False)

    uf: Series[str] = pa.Field(nullable=False, str_matches=r"^[A-Z]{2}$")

    latitude: Series[float] = pa.Field(nullable=True, ge=-90, le=90)
    longitude: Series[float] = pa.Field(nullable=True, ge=-180, le=180)

    data_instalacao: Series[pd.Timestamp] = pa.Field(nullable=True)

    status: Series[str] = pa.Field(
        nullable=False, isin=["ativa", "inativa", "manutencao"]
    )

    @pa.dataframe_check
    def data_nao_futura(cls, df: pd.DataFrame) -> Series[bool]:
        return df["data_instalacao"].isna() | (df["data_instalacao"] <= pd.Timestamp.now())

    class Config:
        strict = True
        coerce = False