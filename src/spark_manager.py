import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, avg, round

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

class SparkManager:
    def __init__(self,app_name: str = "TwitterSparkAnalysis"):
        self.spark = (SparkSession.builder
                      .appName(app_name)
                      .master("local[*]")
                      .getOrCreate())
        self.spark.sparkContext.setLogLevel("WARN")
        self.df = None

    # Temiz veriyi mongo'dan çekip pyspark DataFrame'e dönüştürür.
    def load_cleaned_csv(self, file_path: str = "data/processed/cleaned_tweets.csv") -> None:
        print(f"Temizlenmiş CSV verisi dağıtık sisteme yükleniyor: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}.")
        
        self.df = (self.spark.read
                   .option("header","true")
                   .option("inferSchema","true")
                   .csv(file_path))
        
        print("\nDağıtık Spark DataFrame Şeması (printSchema):")
        self.df.printSchema()

    ## işlemler
    def filter_negative_us_airways(self) -> None:
        """
        İŞLEM 1 (Transformation): select() ve filter() Operasyonları.
        """
        print("\n--- İŞLEM 1 (Transformation): select() ve filter() ---")
        print("Açıklama: US Airways havayoluna ait olumsuz (negative) tweetlerin ayıklanması.\n")

        if self.df is None:
            print("Hata: Önce veri setini yüklemelisiniz!")
            return
        
        transformed_df = (self.df
                          .select("airline", "airline_sentiment", "text")
                          .filter((col("airline") == "US Airways") & 
                                  (col("airline_sentiment") == "negative")))
        
        transformed_df.show(5, truncate=False)


    def add_text_length_column(self) -> None:
        """
        İŞLEM 2 (Transformation): withColumn() Operasyonu.
        Amacı: Her bir tweet metninin karakter uzunluğunu dinamik olarak hesaplayıp 
        yeni bir özellik (feature) olarak veri setine eklemektir.
        """
        print("\n--- İŞLEM 2 (Transformation): withColumn() ile Sütun Türetme ---")
        print("Açıklama: Tweet metinlerinin uzunluklarının hesaplanıp yeni bir sütuna yazdırılması.\n")

        if self.df is None:
            print("Hata: Önce veri setini yüklemelisiniz!")
            return
        
        transformed_df = (self.df
                          .select("airline", "airline_sentiment", "text")
                          .withColumn("text_length", length(col("text"))))
        
        transformed_df.show(5, truncate=False)
        

    def calculate_avg_retweets_by_airline(self) -> None:
        """
        İŞLEM 3 (Transformation): groupBy() ve agg() Operasyonları.
        Amacı: Şirket bazlı kümeleme yaparak her havayolunun ortalama retweet etkileşimini hesaplamak.
        """

        print("\n--- İŞLEM 3 (Transformation): groupBy() ve agg() ile Kümeleme ---")
        print("Açıklama: Havayolu şirketlerine göre ortalama retweet sayılarının hesaplanması.\n")

        if self.df is None:
            print("Hata: Önce Veri Setini Yüklemelisiniz!")
            return
        
        grouped_df = (self.df
                      .groupBy("airline")
                      .agg(round(avg("retweet_count"), 2).alias("avg_retweets"))
                      .orderBy(col("avg_retweets").desc()))

        grouped_df.show(truncate=False)

    def get_top_unique_retweeted_tweets(self) -> None:
        """
        İŞLEM 4 (Transformation): dropDuplicates() ve orderBy() Operasyonları.
        Amacı: Tekrarlayan (spam/bot) tweetleri temizleyip, en yüksek etkileşim alan özgün tweetleri sıralamak.
        """
        print("\n--- İŞLEM 4 (Transformation): dropDuplicates() ve orderBy() ---")
        print("Açıklama: Mükerrer tweetlerin silinmesi ve en yüksek retweet alanların sıralanması.\n")

        if self.df is None:
            print("Hata: Önce Veri Setini Yüklemelisiniz!")
            return
        
        unique_sorted_df = (self.df
                            .dropDuplicates(["text"])
                            .orderBy(col("retweet_count").desc())
                            .select("airline","retweet_count", "text"))
        
        unique_sorted_df.show(5, truncate=False)

    
    def count_total_records(self) -> None:
        """
        İŞLEM 1 (Action): count() Operasyonu.
        Amacı: Dağıtık veri setindeki toplam satır sayısını hesaplayarak 
        Lazy Evaluation (Tembel Değerlendirme) sürecini tetiklemek.
        """
        print("\n--- İŞLEM 1 (Action): count() ---")
        print("Açıklama: Dağıtık DataFrame üzerindeki toplam kayıt sayısının hesaplanması.\n")

        if self.df is None:
            print("Hata: Önce Veri Setimi Yüklemelisiniz!")
            return
        
        total_rows = self.df.count()
        print(f"Veri setindeki toplam kayıt sayısı: {total_rows}")


    def describe_numerical_columns(self) -> None:
        """
        İŞLEM 2 (Action): describe() ve show() Operasyonu.
        Amacı: Sayısal sütunların (retweet_count) istatistiksel özetini (ortalama, standart sapma, min, max) çıkarmak.
        """
        print("\n--- İŞLEM 2 (Action): describe() ---")
        print("Açıklama: 'retweet_count' sütununun istatistiksel özetinin çıkarılması.\n")

        if self.df is None:
            print("Hata: Önce Veri Setini Yüklemelisiniz!")
            return
        
        desc_df = self.df.describe(["retweet_count"])
        desc_df.show()


    def collect_top_retweeted(self) -> None:
        """
        İŞLEM 3 (Action): collect() Operasyonu.
        Amacı: Dağıtık düğümlerdeki (Worker) işlenmiş spesifik verileri ana makinenin (Driver) 
        belleğine bir Python Listesi olarak geri çekmek. (Dikkat: Sadece küçük verilerde yapılmalıdır)
        """
        print("\n--- İŞLEM 3 (Action): collect() ---")
        print("Açıklama: En yüksek retweet alan 3 tweetin Driver (Ana Makine) belleğine çekilmesi.\n")
        
        if self.df is None:
            print("Hata: Önce veri setini yüklemelisiniz!")
            return
        
        top_tweets_list = (self.df
                           .select("airline", "retweet_count", "text")
                           .orderBy(col("retweet_count").desc())
                           .limit(5)
                           .collect())
        
        print("ÇEKİLEN EN YÜKSEK ETKİLEŞİMLİ 5 TWEET]")
        for i, row in enumerate(top_tweets_list, 1):
            print(f"{i}. Şirket: {row['airline']} | Retweet: {row['retweet_count']}")
            print(f"   Metin: {row['text'][:80]}...\n")

    def execute_spark_sql_basic(self) -> None:
        """
        İŞLEM 1 ve 2 (Spark SQL): Temp View Oluşturma ve Temel SQL Sorgusu.
        Amacı: Dağıtık DataFrame'i sanal bir SQL tablosuna çevirmek ve 
        klasik SQL yeteneklerini Spark motoru üzerinde kullanmak.
        """
        print("\n--- İŞLEM 1 ve 2 (Spark SQL): Temp View ve Temel Sorgu ---")
        print("Açıklama: Verinin SQL tablosuna çevrilip en çok şikayet alan şirketlerin bulunması.\n")
        
        if self.df is None:
            print("Hata: Önce veri setini yüklemelisiniz!")
            return
        
        # 1. işlem
        self.df.createOrReplaceTempView("tweets_view")

        # 2. işlem
        query = """
            SELECT airline, COUNT(*) AS total_negative_feedback
            FROM tweets_view
            WHERE airline_sentiment = 'negative'
            GROUP BY airline
            ORDER BY total_negative_feedback DESC
        """

        sql_df = self.spark.sql(query)
        sql_df.show(truncate=False)

    def execute_spark_sql_advanced(self) -> None:
        """
        İŞLEM 3 (Spark SQL): İleri Düzey SQL ve Window Functions.
        Amacı: ROW_NUMBER() ve PARTITION BY kullanarak her bir havayolu şirketinin 
        kendi içindeki en yüksek retweet alan 1. tweetini bulmak.
        """
        print("\n--- İŞLEM 3 (Spark SQL): İleri Düzey Window Functions ---")
        print("Açıklama: Her bir havayolu şirketinin en çok etkileşim alan şikayetinin bulunması.\n")

        if self.df is None:
            print("Hata: Önce Veri Setini Yüklemelisiniz!")
            return
        
        self.df.createOrReplaceTempView("tweets_view")

        # Mantık: Önce şirketlere göre (PARTITION BY) grupla, retweet'e göre (ORDER BY) sırala, 
        # her birine sıra numarası (rn) ver. Dış sorguda ise sadece sıra numarası 1 olanları getir!
        query = """
            SELECT airline, retweet_count, text
            FROM (
                SELECT airline, retweet_Count, text,
                    ROW_NUMBER() OVER(PARTITION BY airline ORDER BY retweet_count DESC) as rn
                FROM tweets_view
            ) ranked_tweets
            WHERE rn = 1
            ORDER BY retweet_Count DESC
        """

        sql_df = self.spark.sql(query)
        sql_df.show(truncate=False)