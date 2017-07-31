from urlchecker import DataPull
import pandas as pd

d = DataPull("/Users/mdobbali/Desktop/test")
campaign_index = pd.read_csv("data/campaign_index.csv", encoding= "ISO-8859-1")
print(d.generate_campaign_index(["Accessories_2007","Attribute Test"],campaign_index))