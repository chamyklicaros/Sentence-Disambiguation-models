from tqdm import tqdm
import pysbd
import pandas as pd

import time


tqdm.pandas()

start = time.perf_counter()



seg = pysbd.Segmenter(language="en", clean=False)
data = pd.read_csv('../Data/FacebookDataSet.csv')

data['predicted_sentence'] = data['Comments'].progress_apply(lambda x: seg.segment(x))
data.to_csv('../f1Score/predictions.csv', index=False)

elapsed = time.perf_counter() - start

print(f"Runtime: {elapsed:.4f} seconds")

