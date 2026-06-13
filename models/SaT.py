import pandas as pd
import time
from wtpsplit import SaT

start = time.perf_counter()


data = pd.read_csv('../Data/FacebookDataSet.csv')


#model
sat_adapted = SaT("sat-12l-sm")



data['predicted_sentence'] = data['Comments'].apply(lambda x: sat_adapted.split(x))

data.to_csv('../f1Score/predictions.csv', index=False)


elapsed = time.perf_counter() - start


print(f"Runtime: {elapsed:.4f} seconds")



