import time
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count

class PerformanceComparer:
    def __init__(self, file_path: str = "data/processed/cleaned_tweets.csv"):
        self.file_path = file_path
        # Spark oturumunu başlat (Mevcut varsa onu kullanır)
        self.spark = (SparkSession.builder
                      .appName("PandasVsSpark")
                      .master("local[*]")
                      .getOrCreate())
        self.spark.sparkContext.setLogLevel("WARN")

    def test_pandas(self) -> float:
        """Pandas ile veriyi okur, şirkete göre gruplar ve süreyi ölçer."""

        start_time = time.time()

        pandas_df = pd.read_csv(self.file_path)
        
        result = pandas_df.groupby('airline').agg(
            avg_retweets=('retweet_count', 'mean'),
            total_feedbacks=('airline_sentiment', 'count')
        )

        end_time = time.time()
        return (end_time-start_time) * 1000
    
    def test_pyspark(self) -> float:
        """PySpark ile veriyi okur, şirkete göre gruplar ve süreyi ölçer."""

        start_time = time.time()

        spark_df = (self.spark.read
                    .option("header", "true")
                    .option("inferSchema", "true")
                    .csv(self.file_path))
        
        result = spark_df.groupBy("airline").agg(
            avg("retweet_count").alias("avg_retweets"),
            count("airline_sentiment").alias("total_feedbacks")
        )

        result.collect()

        end_time = time.time()

        return (end_time - start_time) * 1000
    

    def run_comparison(self) -> None:
        print("\n--- Pandas vs PySpark Performans Karşılaştırması ---")
        print("Açıklama: Aynı Aggregate (Kümeleme) işleminin iki farklı motorda yarıştırılması.\n")
        
        print("Pandas testi çalışıyor...")
        pandas_time = self.test_pandas()
        
        print("PySpark testi çalışıyor...")
        spark_time = self.test_pyspark()
        
        print("\n --- SONUÇLAR --- ")
        print(f"Pandas Çalışma Süresi  : {pandas_time:.2f} ms")
        print(f"PySpark Çalışma Süresi : {spark_time:.2f} ms\n")
        