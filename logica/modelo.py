import pandas as pd

data = pd.read_csv('data/work_orders_dict.csv')

def get_models():
    models = set()
    models.add("EMPTY")
    for code in data.equipo:
        if code[-3] == "-": models.add(code[-2:])
    return models

def give_claveros(model = ""):
    claveros = {}
    for i, row in data.iterrows():
        if model == "":
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
            if model == "" and row.equipo[-3] != "-":
                works.append([row.fecha_creacion, row.descripcion_ot, row.descripcion_averia, row.descripcion_reparacion])
            if row.equipo[-2:] == model:
                works.append([row.fecha_creacion, row.descripcion_ot, row.descripcion_averia, row.descripcion_reparacion])
    return works