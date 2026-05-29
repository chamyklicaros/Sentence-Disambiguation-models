from wtpsplit import SaT
import pandas as pd

data = pd.read_csv('../FacebookDataSet.csv')
#model
sat_lora_adapted = SaT(
	"sat-3l",
	lora_path="/home/koyin/Documents/Sentence-Disambiguation-models/models/wtpsplit/sat-3l-Taglish_lora/facebook-comments/tl",
)

data['predicted_sentence'] = data['Comments'].apply(lambda x: sat_lora_adapted.split(x))

data.to_csv("predictions.csv", index=False)