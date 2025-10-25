import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1️⃣ Cargar dataset ---
df = pd.read_csv("data/data_ots_brake_euskotren_con_componente.csv")

# Asegúrate de usar la columna correcta con texto
col_texto = "descripcion_ot"  # cámbialo al nombre real
df = df.dropna(subset=[col_texto]).reset_index(drop=True)

# --- 2️⃣ Cargar modelo de embeddings ---
print("Cargando modelo de embeddings...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# --- 3️⃣ Generar embeddings ---
print("Generando embeddings (puede tardar un poco la primera vez)...")
embeddings = model.encode(df[col_texto].tolist(), normalize_embeddings=True, show_progress_bar=True)
np.save("embeddings2.npy", embeddings)
print("Embeddings guardados en 'embeddings.npy'.")

