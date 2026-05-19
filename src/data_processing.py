import pandas as pd
import re
from typing import Dict, Any, List

class DataCleaner:
    def __init__(self, df: pd.DataFrame) -> None:
        self.raw_df = df.copy()
        self.cleaned_df = df.copy()
        self.metrics: Dict[str, Any] = {
            "before_count": len(self.raw_df),
            "after_count": 0,
            "dropped_columns": [],
            "quality_dimensions": {}
        }

    # regex ile veri içerisindeki url, mention, hashtag, özel karakter ve boşlukları temizler.
    def clean_text_data(self) -> None:
        regex_url = r'http\S+|www\S+|https\S+'
        regex_mention= r'@\w+'
        regex_hastag = r'#\w+'
        regex_special = r'[^a-zA-Z0-9\s]'

        df = self.cleaned_df['text']

        df = df.str.replace(regex_url, '', regex=True)
        df = df.str.replace(regex_mention, '', regex=True)
        df = df.str.replace(regex_hastag, '', regex=True)
        df = df.str.replace(regex_special, '', regex=True)
        df = df.str.replace(r'\s+', ' ', regex=True).str.strip() # boşluk vb. için
        df = df.str.lower() 

        self.cleaned_df['text'] = df

    # Sütunun yarısından fazlası boşsa o sütunu siliyor, silinen isimleri geri döndürüyor.
    def handle_missing_value(self) -> None:
        threshold = len(self.cleaned_df) * 0.5
        cols_to_drop = self.cleaned_df.columns[self.cleaned_df.isnull().sum() > threshold].tolist()
        self.cleaned_df.drop(columns=cols_to_drop, inplace=True)
        self.metrics["dropped_columns"] = cols_to_drop

        categorical_cols = self.cleaned_df.select_dtypes(include=['object']).columns
        self.cleaned_df[categorical_cols] = self.cleaned_df[categorical_cols].fillna('Unknown')

        numeric_cols = self.cleaned_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            self.cleaned_df[col] = self.cleaned_df[col].fillna(self.cleaned_df[col].median())

    # duplicate dataları siler.
    def remove_duplicates(self) -> None:
        self.cleaned_df.drop_duplicates(inplace=True)

    # datadaki tarih alanını datetime formatına çeviriyor.
    def convert_data_types(self) -> None:
        if 'tweet_created' in self.cleaned_df.columns:
            self.cleaned_df['tweet_created'] = pd.to_datetime(self.cleaned_df['tweet_created'], errors='coerce')

    # data kalitesini ölçme
    def evaluate_data_quality(self) -> None:
        initial_nulls = self.raw_df.isnull().sum().sum()
        initial_total = self.raw_df.size
        final_nulls = self.cleaned_df.isnull().sum().sum()
        final_total = self.cleaned_df.size

        completeness_before = ((initial_total - initial_nulls) / initial_total) * 100
        completeness_after = ((final_total - final_nulls) / final_total) * 100

        valid_dates = self.cleaned_df['tweet_created'].notna().sum() if 'tweet_created' in self.cleaned_df.columns else 0
        consistency = (valid_dates / len(self.cleaned_df)) * 100 if len(self.cleaned_df) > 0 else 0

        url_count = self.cleaned_df['text'].str.contains(r'http\S+|www\S+|https\S+', regex=True).sum()
        accuracy = ((len(self.cleaned_df) - url_count) / len(self.cleaned_df)) * 100


        self.metrics["quality_dimensions"] = {
            "Tamlık": f"%{completeness_after:.2f} (Öncesi: %{completeness_before:.2f})",
            "Tutarlılık": f"%{consistency:.2f} (Tarih formatı yapısal bütünlüğü)",
            "Doğruluk": f"%{accuracy:.2f} (URL ve gürültüden arındırılmış metin oran)"
        }

    def execute_pipeline(self) -> pd.DataFrame:
        self.remove_duplicates()
        self.handle_missing_value()
        self.clean_text_data()
        self.convert_data_types()
        
        self.metrics["after_count"] = len(self.cleaned_df)
        self.evaluate_data_quality()
        
        return self.cleaned_df
    
    def get_metrics_report(self) -> Dict[str, Any]:
        return self.metrics
    
    def save_to_csv(self, file_path: str = "data/processed/cleaned_tweets.csv") -> None:
        import os
        # Klasör yapısı yoksa (örneğin 'data/processed') otomatik oluştur
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # DataFrame'i indekssiz olarak CSV formatında kaydet
        self.cleaned_df.to_csv(file_path, index=False)
        print(f"\nTemizlenmiş veri PySpark için kaydedildi: {file_path}")