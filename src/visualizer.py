import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS

class DataVisualizer:
    def __init__(self, file_path: str = "data/processed/cleaned_tweets.csv"):
        self.df = pd.read_csv(file_path)
        self.output_dir = "reports/figures"
        os.makedirs(self.output_dir, exist_ok=True)

        sns.set_theme(style="whitegrid", palette="muted")
        plt.rcParams.update({"figure.autolayout": True})

    def plot_sentiment_distribution(self) -> None:
        """Grafik 1: Genel Duygu Dağılımı (Pozitif / Negatif / Nötr)"""
        print("Grafik 1 üretiliyor: Duygu Dağılımı...")

        plt.figure(figsize=(8, 6))
        ax = sns.countplot(data= self.df, x='airline_sentiment',
                           order=self.df['airline_sentiment'].value_counts().index,
                           palette={'negative': '#e74c3c', 'neutral': '#f1c40f', 'positive': '#2ecc71'})
        
        plt.title('Twitter Müşteri Geri Bildirimleri - Duygu Dağılımı', fontsize=14, fontweight='bold')
        plt.xlabel('Duygu Durumu', fontsize=12)
        plt.ylabel('Tweet Sayısı', fontsize=12)

        # barların üstüne yazı yazdırma
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='baseline', fontsize=11, color='black', xytext=(0, 5), 
                        textcoords='offset points')
            
        filepath = f"{self.output_dir}/1_sentiment_distribution.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        print(f"Kaydedildi: {filepath}")

    def plot_wordcloud(self) -> None:
        """Grafik 2: En Sık Kullanılan Kelimeler (WordCloud)"""
        print("Grafik 2 üretiliyor: Kelime Bulutu (WordCloud)...")

        text_data = " ".join(str(tweet) for tweet in self.df['text'] if pd.notna(tweet))

        stopwords = set(STOPWORDS)
        stopwords.update(["flight", "flights", "airline", "usairways", "americanair", "southwestair", "jetblue", "united", "virginamerica","will"])

        wordcloud = WordCloud(width=1200, height=600, 
                              background_color='white', 
                              stopwords=stopwords,
                              colormap='viridis',
                              max_words=150).generate(text_data)
        
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Müşteri Geri Bildirimlerindeki En Sık Kullanılan Kelimeler', fontsize=16, fontweight='bold')
        
        filepath = f"{self.output_dir}/2_wordcloud.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Kaydedildi: {filepath}")


    def plot_time_series(self) -> None:
        """Grafik 3: Zaman Serisi Analizi (Günlük Tweet Sayısı)"""
        print("Grafik 3 üretiliyor: Zaman Serisi Analizi...")

        self.df['tweet_created'] = pd.to_datetime(self.df['tweet_created'])
        daily_tweets = self.df.groupby(self.df['tweet_created'].dt.date).size()

        plt.figure(figsize=(10, 6))

        daily_tweets.plot(kind='line', marker='o', color='#3498db', linewidth=2, markersize = 8)

        plt.title('Günlere Göre Sosyal Medya Etkileşim (Tweet) Yoğunluğu', fontsize=14, fontweight='bold')
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel('Günlük Geri Bildirim Sayısı', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        filepath = f"{self.output_dir}/3_time_series.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Kaydedildi: {filepath}")

    def plot_top_users(self) -> None:
        """Grafik 4: En Aktif Kullanıcılar (Bar Grafik)"""
        print("Grafik 4 üretiliyor: En Aktif Kullanıcılar...")

        top_users = self.df['name'].value_counts().head(10)

        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_users.values, y=top_users.index, palette='magma')

        plt.title('Platformdaki En Aktif (En Çok Etkileşim Veren) 10 Kullanıcı', fontsize=14, fontweight='bold')
        plt.xlabel('Tweet Sayısı', fontsize=12)
        plt.ylabel('Kullanıcı Adı', fontsize=12)
        
        filepath = f"{self.output_dir}/4_top_users.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Kaydedildi: {filepath}")

    
    def plot_sentiment_by_airline(self) -> None:
        """Grafik 5 (Serbest Seçim): Şirketlere Göre Duygu Kırılımı (Grouped Bar)"""
        print("Grafik 5 üretiliyor: Şirketlere Göre Duygu Kırılımı...")

        plt.figure(figsize=(12, 6))
        sns.countplot(data=self.df, x='airline', hue='airline_sentiment',
                      palette={'negative': '#e74c3c', 'neutral': '#f1c40f', 'positive': '#2ecc71'})
        
        plt.title('Havayolu Şirketlerine Göre Müşteri Duygu (Sentiment) Karşılaştırması', fontsize=14, fontweight='bold')
        plt.xlabel('Havayolu Şirketi', fontsize=12)
        plt.ylabel('Tweet Sayısı', fontsize=12)
        plt.legend(title='Duygu Durumu', loc='upper right')
        
        filepath = f"{self.output_dir}/5_sentiment_by_airline.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Kaydedildi: {filepath}")

    def plot_negative_reasons(self) -> None:
        """Grafik 6 (İş Zekası Özel): Şikayet (Negatif) Nedenlerinin Dağılımı"""
        print("Grafik 6 üretiliyor: Kök Neden Analizi (Şikayet Nedenleri)...")

        neg_df = self.df[(self.df['airline_sentiment'] == 'negative') & (self.df['negativereason'].notna())]

        plt.figure(figsize=(10, 6))
        sns.countplot(data=neg_df, y='negativereason', 
                      order=neg_df['negativereason'].value_counts().index,
                      color='#e74c3c')
        
        plt.title('Müşteri Memnuniyetsizliği - Kök Neden Analizi (Root Cause Analysis)', fontsize=14, fontweight='bold')
        plt.xlabel('Şikayet Sayısı', fontsize=12)
        plt.ylabel('Şikayet Nedeni', fontsize=12)
        
        filepath = f"{self.output_dir}/6_negative_reasons.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Kaydedildi: {filepath}")