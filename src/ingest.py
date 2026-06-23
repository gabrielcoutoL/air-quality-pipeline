import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class Ingestor:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def ler_csv(
        self,
        filename: str,
        campos: list[str],
        data_types: dict,
        date_columns: Optional[list[str]],
    ) -> pd.DataFrame:

        file_path = self.data_path / f"{filename}.csv"

        try:
            df = pd.read_csv(
                file_path,
                usecols=campos,
                dtype=data_types,
                parse_dates=date_columns,
            )
        except FileNotFoundError as e:
            logger.info(f"Arquivo {filename} não encontrado: {e}")
            raise FileNotFoundError

        return df
