import pandas as pd
from pymongo import MongoClient
from typing import Dict, Any, List

class MongoDBManager:
    def __init__(self, uri: str = 'mongodb://localhost:27017', db_name: str = 'airline_twitter_db', col_name: str = 'tweets'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[col_name]

    def prep_and_bulk_insert(self, df: pd.DataFrame) -> int:
        self.collection.drop()

        df_cleaned = df.where(pd.notnull(df), None)

        records = []

        for _, row in df_cleaned.iterrows():
            doc = {
                "tweet_id": row.get("tweet_id"),
                "text": row.get("text"),
                "tweet_created": row.get("tweet_created"),
                "retweet_count": row.get("retweet_count"),
                "airline_info": {
                    "name": row.get("airline"),
                    "sentiment": row.get("airline_sentiment"),
                    "confidence": row.get("airline_sentiment_confidence")
                },
                "feedback": {
                    "negative_reason": row.get("negativereason")
                },
                "user": {
                    "name": row.get("name"),
                    "timezone": row.get("user_timezone")
                }
            }
            records.append(doc)

        result = self.collection.insert_many(records)
        return len(result.inserted_ids)