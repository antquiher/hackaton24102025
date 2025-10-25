import pandas as pd
from bs4 import BeautifulSoup

data = pd.read_csv('data/work_orders_dict.csv')

def get_models():
    models = set()
    models.add("--")
    for code in data.equipo:
        if code[-3] == "-": models.add(code[-2:])
    return models

def give_claveros(model = ""):
    claveros = {}
    for i, row in data.iterrows():
        if model == "--":
            if row.equipo[-3] != "-":
                if row.clavero in claveros:
                    claveros[row.clavero] += 1
                else:
                    claveros[row.clavero] = 1
        else:
            if row.equipo[-2:] == model:
                if row.clavero in claveros:
                    claveros[row.clavero] += 1
                else:
                    claveros[row.clavero] = 1
    return claveros

def give_work(clavero, model = ""):
    works = []
    for i, row in data.iterrows():
        if row.clavero == clavero:
            if row.comentarios and isinstance(row.comentarios, str) and row.comentarios.strip() != '""':
                clean_comment = BeautifulSoup(row.comentarios, "html.parser").get_text()
            else:
                clean_comment = "SIN COMENTARIOS"
                
            if model == "--":
                if row.equipo[-3] != "-":
                    works.append([row.fecha_creacion, row.descripcion_ot, row.descripcion_averia, row.descripcion_reparacion, clean_comment])
            else:
                if row.equipo[-2:] == model:
                    works.append([row.fecha_creacion, row.descripcion_ot, row.descripcion_averia, row.descripcion_reparacion, clean_comment])
    return works