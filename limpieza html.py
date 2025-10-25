import pandas as pd
from bs4 import BeautifulSoup

data = pd.read_csv('data/work_orders_dict.csv')

for i, row in data.iterrows():
    if row.comentarios and isinstance(row.comentarios, str) and row.comentarios.strip() != '""':
        clean_comment = BeautifulSoup(row.comentarios, "html.parser").get_text()
    else:
        clean_comment = "SIN COMENTARIOS"
    data.at[i, 'comentarios'] = clean_comment

data.to_csv('data/work_orders_dict_limpio_sin_html.csv', index=False)