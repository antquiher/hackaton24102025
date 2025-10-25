import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# --- CACHING: cargar recursos pesados una sola vez ---
@st.cache_resource
def load_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@st.cache_data
def load_embeddings(path="embeddings.npy"):
    return np.load(path)

@st.cache_data
def load_df(path="data/data_ots_completo.csv"):
    return pd.read_csv(path)

@st.cache_data
def load_jerarquia(path="data/jerarquia_total.csv"):
    return pd.read_csv(path)

@st.cache_data
def load_diccionario(path="data/diccionario.csv"):
    return pd.read_csv(path)

# --- UTILIDADES ---
model = load_model()
df = load_df()
embeddings = load_embeddings()
jerarquia_total = load_jerarquia()
diccionario = load_diccionario()

col_texto = "descripcion_ot"
col_clave = "clavero"


def buscar_averias(query, top_k=10):
    """Devuelve los vecinos más similares y un conteo de claves (clavero)."""
    query_vec = model.encode([query], normalize_embeddings=True)
    scores = cosine_similarity(query_vec, embeddings)[0]
    top_idx = np.argsort(scores)[::-1][:top_k]

    cols_to_keep = [col_texto, col_clave]
    if 'clavero_actuacion' in df.columns:
        cols_to_keep.append('clavero_actuacion')
    if 'descripcion_averia' in df.columns:
        cols_to_keep.append('descripcion_averia')

    vecinos = df.iloc[top_idx][cols_to_keep].copy()
    vecinos["similaridad"] = scores[top_idx]

    claves = vecinos[col_clave].dropna().tolist() if col_clave in vecinos.columns else []
    conteo = Counter(claves)

    return vecinos, conteo


def buscar_definicion_por_codigo(cod_act):
    """Busca la definición en el diccionario por diferentes columnas conocidas."""
    if not cod_act or pd.isna(cod_act):
        return 'No hay actuación registrada en el manual.'
    cod_act_clean = str(cod_act).strip()
    defin_row = pd.DataFrame()

    if 'Código tarea std' in diccionario.columns:
        mask1 = diccionario['Código tarea std'].astype(str).str.strip() == cod_act_clean
        if mask1.any():
            defin_row = diccionario.loc[mask1]
    if defin_row.empty and 'Std Tasks Codes' in diccionario.columns:
        mask2 = diccionario['Std Tasks Codes'].astype(str).str.strip() == cod_act_clean
        if mask2.any():
            defin_row = diccionario.loc[mask2]

    if defin_row.empty:
        return 'No hay actuación registrada en el manual.'

    if 'DEFINICION' in defin_row.columns:
        defin_text = defin_row['DEFINICION'].values[0]
    elif 'DEFINITION' in defin_row.columns:
        defin_text = defin_row['DEFINITION'].values[0]
    else:
        possible = [c for c in defin_row.columns if 'defin' in c.lower() or 'descripcion' in c.lower()]
        defin_text = defin_row[possible[0]].values[0] if possible else 'No hay actuación registrada en el manual.'

    if pd.isna(defin_text) or str(defin_text).strip() == '':
        return 'No hay actuación registrada en el manual.'
    return defin_text


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Búsqueda de averías", layout="wide")
st.title("Buscador de averías — Asistente para operarios")
st.write("Introduce la descripción de la avería y el sistema te mostrará averías históricas similares y las actuaciones asociadas.")

with st.form("form_busqueda"):
    consulta = st.text_area("Descripción de la avería (operario):", height=120)
    top_k = 10
    submitted = st.form_submit_button("Buscar")

if submitted:
    if not consulta or str(consulta).strip() == "":
        st.warning("Por favor introduce una descripción de la avería.")
    else:
        with st.spinner("Buscando averías similares..."):
            vecinos, conteo = buscar_averias(consulta, top_k=top_k)

        # Guardar resultados en session_state para que la UI (selectbox) pueda interactuar
        st.session_state['vecinos'] = vecinos
        st.session_state['conteo'] = conteo
        st.session_state['consulta'] = consulta
        st.session_state['top_k'] = top_k

        st.success("Búsqueda realizada. Selecciona una opción en el desplegable para ver los registros históricos.")

# Renderizar la UI de resultados siempre que haya resultados guardados en session_state
if 'conteo' in st.session_state and st.session_state['conteo']:
    vecinos = st.session_state['vecinos']
    conteo = st.session_state['conteo']

    total = sum(conteo.values())
    # construir lista de entradas (clave, freq, porcentaje_float, descripcion)
    entradas = []
    for clave, freq in conteo.items():
        descripcion = jerarquia_total.loc[jerarquia_total['clavero'] == clave, 'componente_total']
        descripcion_texto = descripcion.values[0] if not descripcion.empty else '(sin descripción)'
        porcentaje_float = (freq / total) if total > 0 else 0.0
        entradas.append((clave, freq, porcentaje_float, descripcion_texto))

    # determinar si hay alguna entrada con probabilidad > 10%
    hay_alta = any(pct > 0.10 for (_, _, pct, _) in entradas)

    if hay_alta:
        # filtrar y ordenar por probabilidad descendente
        entradas_filtradas = sorted([e for e in entradas if e[2] > 0.10], key=lambda x: x[2], reverse=True)

        opciones = []
        mapping = {}
        st.subheader("Selecciona el componente implicado")
        st.write("En base al histórico de órdenes de trabajo te presentamos las componentes más probables con las que podría estar relacionada la avería. ")

        for i, (clave, freq, pct, descripcion_texto) in enumerate(entradas_filtradas):
            # no mostrar porcentajes; marcar la primera como 'Más probable'
            if i == 0:
                label = f"{descripcion_texto} (Opción más probable)"
            else:
                label = f"{descripcion_texto} "
            opciones.append(label)
            mapping[label] = (clave, descripcion_texto, pct)

        seleccion = st.selectbox("Componentes:", opciones, key='seleccion_clavero')

        if seleccion:
            clave_sel, desc_sel, pct_sel = mapping[seleccion]

            vecinos_clave = vecinos[vecinos[col_clave] == clave_sel] if col_clave in vecinos.columns else pd.DataFrame()
            if vecinos_clave.empty:
                st.info("No hay registros históricos en los vecinos para la clave seleccionada.")
            else:
                st.subheader("Órdenes de trabajo históricas relacionadas con dicho componente")
                # Mostrar lista resumida y detalles en expanders
                for idx, fila in vecinos_clave.iterrows():
                    desc_averia = fila.get('descripcion_averia', '') if ('descripcion_averia' in fila.index and pd.notna(fila.get('descripcion_averia', ''))) else '(sin descripción de avería)'
                    cod_act = fila.get('clavero_actuacion', '') if ('clavero_actuacion' in fila.index and pd.notna(fila.get('clavero_actuacion', ''))) else ''
                    similar = fila.get('similaridad', None)

                    if cod_act:
                        defin_text = buscar_definicion_por_codigo(cod_act)
                    else:
                        defin_text = 'No hay código de actuación en el registro.'

                    titulo = f"Orden {idx}"
                    with st.expander(titulo, expanded=False):
                        st.write(f"**Descripción de la avería por el operario:** {desc_averia}")
                        st.write(f"**Actuación que se llevó a cabo:** {defin_text}")
                        st.write(f"**Código tarea:** {cod_act if cod_act else '(no indicado)'}")

    else:
        # Todos los componentes tienen probabilidad <= 10% -> mostrar las 5 órdenes con mayor similaridad
        st.write("Presentando las 5 órdenes históricas más similares al texto introducido para que elijas la más relevante.")

        vecinos_sorted = vecinos.sort_values(by='similaridad', ascending=False).head(5)
        opciones = []
        mapping = {}
        for idx, fila in vecinos_sorted.iterrows():
            sim = fila.get('similaridad', 0.0)
            desc = fila.get('descripcion_averia', '') if ('descripcion_averia' in fila.index and pd.notna(fila.get('descripcion_averia', ''))) else '(sin descripción de avería)'
            label = f"Orden idx={idx} — Similaridad {sim:.3f}"
            opciones.append(label)
            # guardamos la fila completa para mostrar detalles al seleccionar
            mapping[label] = fila.to_dict()

        seleccion = st.selectbox("Órdenes más similares:", opciones, key='seleccion_vecino_por_sim')

        if seleccion:
            fila = mapping[seleccion]
            desc_averia = fila.get('descripcion_averia', '(sin descripción de avería)')
            cod_act = fila.get('clavero_actuacion', '')
            similar = fila.get('similaridad', None)

            if cod_act:
                defin_text = buscar_definicion_por_codigo(cod_act)
            else:
                defin_text = 'No hay código de actuación en el registro.'

            st.subheader(f"Detalles de la orden seleccionada (similaridad: {similar:.3f})")
            st.write(f"**Descripción de la avería por el operario:** {desc_averia}")
            st.write(f"**Actuación que se llevó a cabo:** {defin_text}")
            st.write(f"**Código tarea:** {cod_act if cod_act else '(no indicado)'}")

    st.divider()
