import pandas as pd 

df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})

path = './test.csv'
df.to_csv(path)