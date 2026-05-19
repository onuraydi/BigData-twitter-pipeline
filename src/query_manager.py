import pprint
from pymongo.collection import Collection
import re
from datetime import datetime

class QueryManager:
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_negative_united_tweets(self, limit: int = 10) -> None:
        """
            1. find() sorgusu: Koşullu Filtreleme, Projeksiyon ve Limit.
            United Airlines şirketine atılmış negatif duygu durumuna sahip 
            tweetlerin sadece metnini ve duygu durumunu getirir.
        """

        print(f"\n--- SORGU 1: Temel find() - Filtreleme ve Projeksiyon ---")
        print("Açıklama: United Airlines için negatif duygu durumu içeren tweetler.\n")

        query = {
            "airline_info.name": "United",
            "airline_info.sentiment":"negative"
        }

        # id gelmesin text, sentiment ve user gelsin
        projection = {
            "_id": 0,
            "text": 1,
            "airline_info.sentiment": 1,
            "user": 1,
        }

        cursor = self.collection.find(query,projection).limit(limit)

        for doc in cursor:
            pprint.pprint(doc)


    def get_retweeted_positive_tweets(self, limit: int = 10) -> None:
        """
        2. find() sorgusu: Mantıksal Karşılaştırma ve Filtreleme.
        Retweet almış (retweet_count > 0) ve duygu durumu pozitif olan
        tweetleri getirir. $gt (greater than) operatörü kullanılmıştır.
        """

        print(f"\n--- SORGU 2: Mantıksal Karşılaştırma ($gt) ---")
        print("Açıklama: En az 1 kez retweet edilmiş pozitif tweetler.\n")

        query = {
            "retweet_count": {"$gt": 0},
            "airline_info.sentiment": "positive"
        }

        projection = {
            "_id": 0,
            "text": 1,
            "retweet_count": 1,
            "airline_info.sentiment": 1,
            "user": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)

        for doc in cursor:
            pprint.pprint(doc)


    def get_top_retweeted_with_pagination(self, skip: int= 1, limit: int = 10) -> None:
        """
        3. find() sorgusu: Sıralama (Sort) ve Sayfalama (Pagination).
        En çok retweet alan tweetleri büyükten küçüğe sıralar,
        belirtilen sayı kadarını atlar (skip) ve sonrakileri getirir (limit).
        """

        print(f"\n--- SORGU 3: Sıralama ve Sayfalama (Sort, Skip, Limit) ---")
        print(f"Açıklama: En yüksek retweet alanlardan ilk {skip} kaydı atla, sonraki {limit} kaydı getir.\n")

        projection = {
            "_id": 0,
            "text": 1,
            "retweet_count": 1,
            "airline_info.name": 1
        }

        cursor = (self.collection.find({}, projection)
                  .sort("retweet_count", -1)
                  .skip(skip)
                  .limit(limit))
        
        for doc in cursor:
            pprint.pprint(doc)

    def get_high_confidence_specific_airlines(self, limit: int = 10) -> None:
        """
        4. find() sorgusu: Liste İçi Arama ($in) ve Koşullu Filtreleme.
        Belirli havayolu şirketlerinin ("Delta" veya "US Airways") 
        yüksek güven skorlu (0.9 üstü) tweetlerini getirir.
        """

        print(f"\n--- SORGU 4: Liste İçi Arama ($in) ---")
        print("Açıklama: Delta veya US Airways için güven skoru > 0.9 olan tweetler.\n")

        query = {
            "airline_info.name": {"$in": ["Delta","US Airways"]},
            "airline_info.confidence": {"$gt": 0.9}
        }

        projection = {
            "_id":0, 
            "airline_info.name": 1, 
            "airline_info.confidence": 1,
            "text": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)

    def get_highly_retweeted_or_positive_tweets(self, limit:int = 10) -> None:
        """
        5. find() sorgusu: Mantıksal VEYA ($or) Operatörü.
        Retweet sayısı 5'ten büyük olan YA DA duygu durumu 'positive' olan
        tweetleri getirir.
        """

        print(f"\n--- SORGU 5: Mantıksal VEYA ($or) ---")
        print("Açıklama: Retweet sayısı > 5 VEYA duygu durumu 'positive' olan tweetler.\n")

        query = {
            "$or": [
                {"retweet_count": {"$gt":5}},
                {"airline_info.sentiment": "positive"}
            ]
        }

        projection = {
            "_id": 0, 
            "text": 1, 
            "retweet_count": 1,
            "airline_info.sentiment": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)


    def get_avg_confidence_by_airline(self) -> None:
        """
        1. Aggregation Sorgusu: Şirketlere Göre Ortalama Güven Skoru.
        $group, $avg ve $sort operatörlerini kullanarak her bir havayolu 
        şirketinin ortalama etiket güven skorunu hesaplar ve sıralar.
        """
        
        print(f"\n--- SORGU 1: Aggregation Pipeline ($group, $avg, $sort) ---")
        print("Açıklama: Havayolu şirketlerinin ortalama duygu güven skorları (Azalan Sırayla).\n")

        pipeline = [
            {"$group": {
                "_id": "$airline_info.name",
                "avg_confidence": {"$avg":"$airline_info.confidence"}
            }},
            {"$sort": {"avg_confidence": -1}}
        ]

        cursor = self.collection.aggregate(pipeline)
        for doc in cursor:
            pprint.pprint(doc)

    def get_top_complaints_for_us_airways(self, limit: int = 10) -> None:
        """
        2. Aggregation Sorgusu: Spesifik Şirket İçin En Sık Şikayetler
        $match, $group, $sort, $limit operatörlerini zincirleme kullanarak 
        US Airways'in en çok şikayet aldığı 5 konuyu bulur.
        """

        print(f"\n--- SORGU 2: Zincirleme Aggregation ($match, $group, $sort, $limit) ---")
        print("Açıklama: US Airways için en sık karşılaşılan ilk 5 şikayet nedeni.\n")

        pipeline = [
            {"$match": {
                "airline_info.name": "US Airways",
                "airline_info.sentiment": "negative"
            }},

            {"$group": {
                "_id": "$feedback.negative_reason",
                "count": {"$sum": 1}
            }},

            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        cursor = self.collection.aggregate(pipeline)
        for doc in cursor:
            pprint.pprint(doc)

    def get_sentiment_distribution(self) -> None:
        """
        3. Aggregation Sogusu: $project Operatörü ile Veri Şekillendirme.
        Genel duygu dağılımını (Pozitif, Negatif, Nötr) hesaplar ve 
        $project kullanarak alan adlarını İngilizceden Türkçeye çevirir.
        """

        print(f"\n--- SORGU 3: Projeksiyon ile İsimlendirme ($project) ---")
        print("Açıklama: Duygu dağılımının Türkçe isimlendirilerek raporlanması.\n")

        pipeline = [
            {"$group": {
                "_id": "$airline_info.sentiment",
                "total": {"$sum":1}
            }},
            {"$project": {
                "_id": 0,
                "Duygu_Durumu": "$_id",
                "Toplam_Tweet_Sayisi": "$total"
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        for doc in cursor:
            pprint.pprint(doc)

    def get_confidence_score_histogram(self) -> None:
        """
        4. Aggregation Sogusu: $bucket Operatörü ile Histogram/Sepetleme
        Güven skorlarını (confidence) 0.0-0.5 (Düşük), 0.5-0.8 (Orta) ve 
        0.8-1.0 (Yüksek) aralıklarına bölerek her aralıktaki tweet sayısını bulur.
        """
        print(f"\n--- SORGU 4: Histogram Oluşturma ($bucket) ---")
        print("Açıklama: Etiket güven skorlarının belirli aralıklara (sepetlere) bölünmesi.\n")

        pipeline = [
            {"$bucket": {
                "groupBy": "$airline_info.confidence",
                "boundaries": [0.0, 0.5, 0.8, 1.01],
                "default": "NoN",
                "output": {
                    "tweet_sayisi": {"$sum": 1},
                    "etkilenen_sirketler": {"$addToSet": "$airline_info.name"}
                }
            }}
        ]

        cursor = self.collection.aggregate(pipeline)
        for doc in cursor:
            pprint.pprint(doc)
    
    def get_comprehensive_summary_report(self) -> None:
        """
        5. Aggregation Sogusu: $facet Operatörü ile Çoklu Raporlama.
        Tek bir veritabanı sorgusu (round-trip) içinde hem en çok pozitif 
        tweet alan şirketleri hem de en sık şikayet edilen nedenleri aynı anda getirir.
        """
        print(f"\n--- SORGU 5: Çoklu Raporlama ($facet) ---")
        print("Açıklama: Tek sorguda 'En İyi Şirketler' ve 'En Sık Şikayetler' raporları.\n")

        pipeline = [
            {"$facet": {
                "en_iyi_sirketler": [
                    {"$match": {"airline_info.sentiment": "positive"}},
                    {"$group": {"_id": "$airline_info.name", "pozitif_sayisi": {"$sum": 1}}},
                    {"$sort": {"pozitif_sayisi": -1}},
                    {"$limit": 5}
                ],

                "en_cok_sikayetler": [
                    {"$match": {"airline_info.sentiment": "negative"}},
                    {"$group": {"_id": "$feedback.negative_reason" ,"sikayet_sayisi": {"$sum": 1}}},
                    {"$sort": {"sikayet_sayisi": -1}},
                    {"$limit": 5}
                ]
            }}
        ]

        cursor = self.collection.aggregate(pipeline)
        for doc in cursor:
            pprint.pprint(doc)



    def test_index_performance(self) -> None:
        """
        1. index: B-Tree İndeksi ve Performans Karşılaştırması.
        airline_info.name üzerine indeks oluşturmadan önce ve sonra 
        sorgu maliyetlerini (explain) karşılaştırır.
        """

        print(f"\n--- SORGU 1: İndeksleme ve Performans Testi (explain) ---")
        print("Açıklama: İndeks öncesi ve sonrası taranan doküman sayılarının kıyaslanması.\n")

        self.collection.drop_indexes()

        query = {"airline_info.name": "Delta"}

        # index yokken performans
        plan_before = self.collection.find(query).explain()["executionStats"]
        docs_before = plan_before.get("totalDocsExamined", 0)
        time_before = plan_before.get("executionTimeMillis", 0)
        print(f"İndeks ÖNCESİ -> Taranan Doküman: {docs_before}, Süre: {time_before} ms")

        # index oluşturma
        self.collection.create_index([("airline_info.name", 1)])
        print("\n[*] 'airline_info.name' alanı üzerine B-Tree indeksi oluşturuldu.\n")

        # İndeks varken sorgu performansı
        plan_after = self.collection.find(query).explain()["executionStats"]
        docs_after = plan_after.get("totalDocsExamined", 0)
        time_after = plan_after.get("executionTimeMillis", 0)
        print(f"İndeks SONRASI -> Taranan Doküman: {docs_after}, Süre: {time_after} ms")

    
    def search_with_text_index(self, limit: int = 10) -> None:
        """
        2. index: Full-Text Index ve $text Araması.
        Metin madenciliği için 'text' sütununa Text Index atar ve 
        Google benzeri kelime araması yapar (Alaka düzeyine göre sıralar).
        """

        print(f"\n--- SORGU 2: Full-Text İndeks ve Kelime Araması ($text) ---")
        print("Açıklama: 'baggage' veya 'lost' kelimelerini içeren tweetlerin Text Index ile aranması.\n")

        # Text Index Oluşturma
        self.collection.create_index([("text", "text")])
        print("[*] 'text' alanı üzerine Full-Text indeksi oluşturuldu.\n")

        query = {
            "$text": {"$search": "baggage lost"}
        }

        projection = {
            "_id": 0,
            "airline_info.name": 1,
            "text": 1,
            "alaka_skoru": {"$meta": "textScore"}
        }

        cursor = (self.collection.find(query, projection)
                  .sort([("alaka_skoru", {"$meta": "textScore"})])
                  .limit(limit))

        for doc in cursor:
            pprint.pprint(doc)


    def review_single_complaint(self) -> None:
        """
        1. Update: Tekil Kayıt Güncelleme (updateOne ve $set).
        Spesifik bir şikayet kaydına (örneğin Virgin America'ya ait bir negatif tweet)
        'is_reviewed' bayrağı ve inceleme notu ekler
        """

        print(f"\n--- SORGU 1: Tekil Doküman Güncelleme ($set) ---")
        print("Açıklama: Spesifik bir şikayete 'is_reviewed' bayrağı eklenmesi.\n")

        query = {
            "airline_info.name": "Virgin America",
            "airline_info.sentiment": "negative"
        }

        update_operation = {
            "$set": {
                "is_reviewed": True,
                "reviewer_note": "Müşteri hizmetleri departmanına iletildi.",
                "action_taken": "Pending"
            }
        }

        result = self.collection.update_one(query, update_operation)

        print(f"Eşleşen Doküman Sayısı: {result.matched_count}")
        print(f"Güncellenen Doküman Sayısı: {result.modified_count}")

        if result.modified_count > 0:
            print("\n[+] Güncellenen Dokümanın Son Hali:")
            updated_doc = self.collection.find_one(query)
            pprint.pprint(updated_doc)

    def boost_positive_tweet_retweets(self) -> None:
        """
        2. Update: Toplu Kayıt Güncelleme (updateMany ve $inc).
        Duygu durumu 'positive' olan tüm tweetlerin retweet sayısını
        matematiksel olarak 5 artırır.
        """
        print(f"\n--- SORGU 2: Toplu Doküman Güncelleme ($inc) ---")
        print("Açıklama: Pozitif tweetlerin retweet sayısının topluca artırılması.\n")

        query = {
            "airline_info.sentiment": "positive"
        }

        update_operation = {
            "$inc": {
                "retweet_count": 5
            }
        }

        result = self.collection.update_many(query, update_operation)

        print(f"Eşleşen Doküman Sayısı: {result.matched_count}")
        print(f"Güncellenen Doküman Sayısı: {result.modified_count}")

        if result.modified_count > 0:
            print("\n[+] Örnek Güncellenmiş Doküman (Retweet sayısı kontrolü):")
            sample_doc = self.collection.find_one(query)
            pprint.pprint(sample_doc)

    def delete_low_confidence_tweets(self) -> None:
        """
        1. delete: Toplu Kayıt Silme (deleteMany).
        Makine öğrenmesi modelini yanıltabilecek, güven skoru 0.50'nin 
        altında olan (zayıf etiketlenmiş) verileri koleksiyondan kalıcı olarak siler.
        """
        print(f"\n--- SORGU 1: Toplu Kayıt Silme (deleteMany) ---")
        print("Açıklama: Etiket güven skoru < 0.50 olan zayıf verilerin temizlenmesi.\n")

        query = {
            "airline_info.confidence": {"$lt": 0.50}
        }

        result = self.collection.delete_many(query)

        print(f"Filtreye Uyan ve Kalıcı Olarak Silinen Doküman Sayısı: {result.deleted_count}")

    def delete_anomalous_tweet(self) -> None:
        """
        2. delete: Tekil Kayıt Silme (deleteOne).
        Sistemde anomali yaratan spesifik bir kaydı (örneğin ilk 'neutral' tweeti)
        güvenli bir şekilde, diğerlerine dokunmadan tekil olarak siler.
        """
        print(f"\n--- SORGU 2: Tekil Kayıt Silme (deleteOne) ---")
        print("Açıklama: Anomali yaratan spesifik tek bir kaydın güvenli silinmesi.\n")

        query = {
            "airline_info.sentiment": "neutral"
        }

        result = self.collection.delete_one(query)

        print(f"Anomali Olarak Tespit Edilip Silinen Tekil Doküman Sayısı: {result.deleted_count}")


    def get_eastern_time_negative_users(self, limit: int = 10) -> None:
        """
        1. ileri düzey sorgu: Nested (İç İçe) Doküman Sorgusu.
        Zaman dilimi 'Eastern Time' olan kullanıcıların negatif geri bildirimlerini bulur.
        Nokta notasyonu (dot notation) kullanılmıştır.
        """

        print(f"\n--- SORGU 1: İç İçe Doküman (Nested) Araması ---")
        print("Açıklama: 'Eastern Time' bölgesindeki kullanıcıların şikayet nedenleri.\n")

        query = {
            "user.timezone": {"$regex": "Eastern Time", "$options": "i"},
            "airline_info.sentiment": "negative"
        }

        projection = {
            "_id": 0,
            "user.name": 1,
            "user.timezone": 1,
            "feedback.negative_reason": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)

    def search_baggage_issues_regex(self, limit: int = 10) -> None:
        """
        2. ileri düzey sorgu: Düzenli İfadeler ($regex) ile NLP Ön Hazırlığı.
        Metin içinde büyük/küçük harf duyarsız (case-insensitive) olarak
        'baggage', 'lost' veya 'luggage' geçen tweetleri tespit eder.
        """
        print(f"\n--- SORGU 2: Regex ile Metin İçi Kelime Araması ($regex) ---")
        print("Açıklama: Bagaj kayıp sorunu yaşayan müşteri bildirimleri.\n")

        regex_pattern = re.compile(r"baggage|lost|luggage", re.IGNORECASE)

        query = {
            "text": {"$regex": regex_pattern}
        }

        projection = {
            "_id": 0,
            "airline_info.name": 1,
            "text": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)


    def get_long_complaints(self, limit: int = 10) -> None:
        """
        3. ileri düzey sorgu: Doküman İçi Mantıksal Fonksiyon ($expr).
        Aynı doküman içindeki bir alanın karakter uzunluğunu ($strLenCP) ölçer
        ve 100 karakterden uzun olan, detaylı şikayet tweetlerini getirir.
        """

        print(f"\n--- SORGU 3: Doküman İçi Uzunluk Fonksiyonu ($expr ve $strLenCP) ---")
        print("Açıklama: 100 karakterden uzun, detaylandırılmış müşteri şikayetleri.\n")

        query = {
            "airline_info.sentiment": "negative",
            "$expr": {"$gt": [{"$strLenCP": "$text"}, 100]}
        }

        projection = {
            "_id": 0,
            "text": 1,
            "airline_info.name": 1
        }

        cursor = self.collection.find(query, projection).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)

    def get_delay_tweets_in_time_range(self, limit: int = 10) -> None:
        """
        4. ileri düzey sorgu: İki Tarih Arası (Date Range) Filtreleme.
        22 Şubat - 24 Şubat 2015 tarihleri arasında atılan "gecikme" temalı tweetleri getirir.
        """
        print(f"\n--- SORGU 4 (BONUS): Zaman Serisi (Time-Series) Analizi ---")
        print("Açıklama: 22-24 Şubat 2015 arasında yaşanan uçuş gecikmesi (delay) bildirimleri.\n"),

        start_date = datetime(2015, 2, 22)
        end_date = datetime(2015, 2, 25)

        query = {
            "tweet_created": {"$gte": start_date, "$lt": end_date},
            "text": {"$regex": "delay", "$options": "i"}
        }

        projection = {
            "_id": 0,
            "tweet_created": 1,
            "airline_info.name": 1,
            "text": 1
        }

        cursor = self.collection.find(query, projection).sort("tweet_created", -1).limit(limit)
        for doc in cursor:
            pprint.pprint(doc)