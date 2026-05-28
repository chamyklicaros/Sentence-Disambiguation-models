import pysbd
import pandas as pd


seg = pysbd.Segmenter(language="en", clean=False)
data = pd.read_csv('../FacebookDataSet.csv')

data['predicted_sentence'] = data['Comments'].apply(lambda x: seg.segment(x))
data.to_csv('../prediction.csv', index=False)
data.to_csv('../pysbd_prediction.csv', index=False)