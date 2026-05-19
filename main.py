import json
import sys
from pathlib import Path
from src.data_ingestion import DataExplorer
from src.data_processing import DataCleaner
from src.database import MongoDBManager
from src.query_manager import QueryManager
from src.spark_manager import SparkManager
from src.spark_vs_pandas import PerformanceComparer
from src.visualizer import DataVisualizer

explorer = DataExplorer(file_path="data/raw/Tweets.csv")
df = explorer.load()

# # %% Data_ingension
# summary = explorer.get_summary()

# print("--- Boyut ---")
# print(summary["dimensions"])

# print("\n--- Sütun İsimleri ---")
# print(summary["columns"])

# print("\n--- Veri Tipleri ---")
# print(summary["dtypes"])

# print("\n--- Örnek Kayıtlar ---")
# print(summary["samples"])

# print("\n--- Eksik Bilgiler ---")
# print(summary["missing_data"])

# print("\n--- Tekrarlayan kayıtlar ---")
# print(summary["duplicates"])

# print("\n--- Bellek Tüketimi ---")
# print(summary["memory_usage"])

# print("\n--- Veri Seti Yapısal Bilgisi (info) ---")
# print(explorer.get_info_string())

# print("\n--- Temel İstatistiksel Dağılımlar (describe) ---")
# print(explorer.get_statistical_summary())


###########################################################################################################
# data_processing


# # Aşama 2.1 çıktısı 'clean_text_data()'

# cleaner = DataCleaner(df=df)
# print("\n--- Temizleme ÖNCESİ Örnek Metinler ---")
# print(cleaner.cleaned_df[['tweet_id', 'text']].head())

# cleaner.clean_text_data()

# print("\n--- Temizleme SONRASI Örnek Metinler ---")
# print(cleaner.cleaned_df[['tweet_id', 'text']].head()) 


# # --- ADIM 2.5: Tip Dönüşümü (Type Casting) ---
# cleaner = DataCleaner(df=df)

# print("--- Dönüşüm ÖNCESİ Veri Tipi ---")
# print(f"tweet_created sütun tipi: {cleaner.cleaned_df['tweet_created'].dtype}")
# print(cleaner.cleaned_df[['tweet_id', 'tweet_created']].head(3))

# # OOP Mimarisindeki tip dönüşüm (datetime) metodunun çağrılması
# cleaner.convert_data_types()

# print("\n--- Dönüşüm SONRASI Veri Tipi ---")
# print(f"tweet_created sütun tipi: {cleaner.cleaned_df['tweet_created'].dtype}")
# print(cleaner.cleaned_df[['tweet_id', 'tweet_created']].head(3))



# #Genel data_processing (Tüm adımlar pipeline ile uygulanıyor)

# cleaner = DataCleaner(df=df)
# clean_df = cleaner.execute_pipeline()
# metrics = cleaner.get_metrics_report()

# print("--- Temizleme Öncesi ve Sonrası Kayıt Sayısı ---")
# print(f"Başlangıç: {metrics['before_count']}")
# print(f"Bitiş: {metrics['after_count']}")
# print(f"Silinen Mükerrer Satır: {metrics['before_count'] - metrics['after_count']}")

# print("\n--- Eksik Veri Yönetimi ---")
# print(f"Kaldırılan Sütunlar (Düşük Tamlık): {metrics['dropped_columns']}")

# print("\n--- Veri Kalitesi Boyutları ---")
# print(json.dumps(metrics['quality_dimensions'], indent=4, ensure_ascii=False))

# print("\n--- Temizlenmiş Veri Örneği ---")
# print(clean_df[['tweet_id', 'text', 'tweet_created']].sample(10))

# cleaner.save_to_csv("data/processed/cleaned_tweets.csv")

# # MONGO DB Insert işlemi

# db_manager = MongoDBManager()
# inserted_count = db_manager.prep_and_bulk_insert(clean_df)    
# print(f"\nPipeline Execution Successful. Inserted {inserted_count} documents into MongoDB.")

###########################################################################################################
## SORGULAR

db_manager = MongoDBManager()

query_manager = QueryManager(collection=db_manager.collection)

# # 1. find sorgusu
# query_manager.get_negative_united_tweets(limit = 5)

# # 2. find sorgusu
# query_manager.get_retweeted_positive_tweets(limit=5)

# # 3. find sorgusu
# query_manager.get_top_retweeted_with_pagination(skip=1, limit=5)

# # 4. find sorgusu
# query_manager.get_high_confidence_specific_airlines(limit=5)

# # 5. find sorgusu 
# query_manager.get_highly_retweeted_or_positive_tweets(limit=5)


###########################################################################################################

# # 1. aggregation sorgusu
# query_manager.get_avg_confidence_by_airline()

# # 2. aggregation sorgusu
# query_manager.get_top_complaints_for_us_airways(limit=5)

# # 3. aggregation sorgusu
# query_manager.get_sentiment_distribution()

# # 4. aggregation sorgusu
# query_manager.get_confidence_score_histogram()

# # 5. aggregation sorgusu
# query_manager.get_comprehensive_summary_report()


###########################################################################################################
# index

# # 1. index
# query_manager.test_index_performance()

# # 2. index
# query_manager.search_with_text_index(limit=5)


###########################################################################################################
# Update

# # 1. update
# query_manager.review_single_complaint()


# # 2. update
# query_manager.boost_positive_tweet_retweets()


###########################################################################################################
# delete

# # 1. delete
# query_manager.delete_low_confidence_tweets()

# # 2. delete
# query_manager.delete_anomalous_tweet()


###########################################################################################################
# İleri Düzey Sorgular

# # 1. ileri düzey sorgu
# query_manager.get_eastern_time_negative_users(limit=5)

# # 2. ileri düzey sorgu
# query_manager.search_baggage_issues_regex(limit = 5)

# # 3. ileri düzey sorgu
# query_manager.get_long_complaints(limit=5)

# # 4. ileri düzey sorgu
# query_manager.get_delay_tweets_in_time_range(limit=5)


###########################################################################################################
# PySpark

# spark_manager = SparkManager()

# # veri yükleme
# spark_manager.load_cleaned_csv()

# # 1. Transformation
# spark_manager.filter_negative_us_airways()

# # 2. Transformation
# spark_manager.add_text_length_column()

# # 3. Transformation
# spark_manager.calculate_avg_retweets_by_airline()

# # 4. Transformation
# spark_manager.get_top_unique_retweeted_tweets()


# # 1. Action
# spark_manager.count_total_records()

# # 2. Action
# spark_manager.describe_numerical_columns()

# # 3. Action
# spark_manager.collect_top_retweeted()


# # 1. ve 2.  Spark SQL
# spark_manager.execute_spark_sql_basic()

# # 3. Spark SQL
# spark_manager.execute_spark_sql_advanced()


# pandas vs PySpark

# comparer = PerformanceComparer()
# comparer.run_comparison()


###########################################################################################################
# Grafikler

visualizer = DataVisualizer()

# # 1. grafik - duygu dağılımı
# visualizer.plot_sentiment_distribution()

# # 2. grafik - kelime bulutu
# visualizer.plot_wordcloud()

# # 3. grafik
# visualizer.plot_time_series()

# # 4. grafik
# visualizer.plot_top_users()

# 5. grafik
visualizer.plot_sentiment_by_airline()

# 6. grafik
visualizer.plot_negative_reasons()