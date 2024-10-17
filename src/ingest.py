import os
import pandas as pd
import pickle
import minsearch

DATA_PATH = os.getenv("DATA_PATH", "../dataset/data.csv")

def load_index(data_path=DATA_PATH):
    df = pd.read_csv(data_path)
    documents = df.to_dict(orient="records")
    print(documents[9])

    index = minsearch.Index(
        text_fields=['Questions', 'Answers'],
        keyword_fields=["Question_ID"],
    )

    index.fit(documents)
    return index
