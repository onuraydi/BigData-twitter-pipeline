import pandas as pd
import io
from typing import Dict, Any, List, Tuple
from pathlib import Path

class DataExplorer:
    def __init__(self, file_path: str | Path, encoding: str = 'utf-8') -> None:
        self.file_path = Path(file_path)
        self.encoding = encoding
        self._df: pd.DataFrame | None = None

    # Data'yı pandas dataframe olarak okur. 
    def load(self) -> Tuple[int, int]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self._df = pd.read_csv(self.file_path,encoding=self.encoding)
        return self._df
    
    # DataFrame'in boyutunu verir. (satır ve sütün)
    def get_dimensions(self) -> Tuple[int, int]:
        self._check_loaded()
        return self._df.shape
    
    # DataFrame içindeki sütun isimlerini liste olarak döndürür.
    def get_columns(self) -> List[str]:
        self._check_loaded()
        return self._df.columns.tolist()
    
    # DataFrame içindeki her sütunun veri tipini döndürür.
    def get_dtypes(self) -> pd.Series:
        self._check_loaded()
        return self._df.dtypes

    # DataFrame içindeki rastgele 10 (default) örneği getirir.
    def get_sample(self, n: int = 10) -> pd.DataFrame:
        self._check_loaded()
        return self._df.sample(n)
    
    # Veri içindeki eksikleri (NaN/null) analiz etmek
    def get_missing_report(self) -> pd.DataFrame:
        self._check_loaded()
        missing = self._df.isnull().sum()
        missing_percent = (missing / len(self._df)) * 100
        report = pd.DataFrame({
            'Missing_Count': missing,
            'Missing_Percentage': missing_percent
        }).sort_values(by='Missing_Count', ascending=False)
        return report[report['Missing_Count'] > 0]

    # Tekrarlayan (duplicate) satırların sayısını döndürür.
    def get_duplicate_count(self) -> int:
        self._check_loaded()
        return int(self._df.duplicated().sum())
    
    # DataFrame’in bellekte ne kadar yer kapladığını MB cinsinden verir.
    def get_memory_usage(self) -> str:
        self._check_loaded()
        usage_bytes = self._df.memory_usage(deep=True).sum()
        return f"{usage_bytes / (1024 ** 2):.2f} MB"
    

    def get_info_string(self) -> str:
        self._check_loaded()
        buffer = io.StringIO()
        self._df.info(buf=buffer, memory_usage='deep')
        return buffer.getvalue()

    def get_statistical_summary(self) -> pd.DataFrame:
        self._check_loaded()
        return self._df.describe(include='all').T
    
    # özet şeklinde verileri getirir
    def get_summary(self) -> Dict[str, Any]:
        self._check_loaded()
        return {
            "dimensions": self.get_dimensions(),
            "columns": self.get_columns(),
            "dtypes": self.get_dtypes(),
            "samples": self.get_sample(),
            "missing_data": self.get_missing_report(),
            "duplicates": self.get_duplicate_count(),
            "memory_usage": self.get_memory_usage(),
            "info": self.get_info_string(),
            "statistics": self.get_statistical_summary()
        }


    def _check_loaded(self) -> None:
        if self._df is None:
            raise ValueError("DataFrame is not loaded. Call load() first.")