import pandas as pd
from wtpsplit import SaT

data = pd.read_csv('../FacebookDataSet.csv')


#model
sat_adapted = SaT("sat-12l-sm")



data['predicted_sentence'] = data['Comments'].apply(lambda x: sat_adapted.split(x))

#output to excel
data.to_csv("predictions.csv", index=False)

data.to_csv("SaT_predictions.csv", index=False)



