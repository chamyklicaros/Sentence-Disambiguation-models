from wtpsplit import SaT
import pandas as pd
from tqdm import tqdm
import time

tqdm.pandas()

start = time.perf_counter()


data = pd.read_csv('../Data/FacebookDataSet.csv')
#model
sat_lora_adapted = SaT(
	"sat-3l",
	lora_path="wtpsplit/sat-3l-Taglish_lora/facebook-comments/tl",
)

data['predicted_sentence'] = data['Comments'].progress_apply(lambda x: sat_lora_adapted.split(x))

data.to_csv('../f1Score/predictions.csv', index=False)


elapsed = time.perf_counter() - start


print(f"Runtime: {elapsed:.4f} seconds")
