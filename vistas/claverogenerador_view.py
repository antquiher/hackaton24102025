import streamlit as st
import pandas as pd
import os


@st.cache_data
def cargar_datos_view():
    """Carga el CSV de jerarquía desde la carpeta data."""
    try:
        csv_path = os.path.join('data', 'jerarquia.csv')
        if not os.path.exists(csv_path):
            return None
        df = pd.read_csv(csv_path)
        columnas_requeridas = ['clavero', 'componente', 'nivel', 'nivel1', 'nivel2',
                              'componente_nivel1', 'componente_nivel2']
        if not all(col in df.columns for col in columnas_requeridas):
            return None
        return df
    except Exception:
        return None


@st.cache_data
def cargar_diccionario_view():
    try:
        csv_path = os.path.join('data', 'diccionario.csv')
        if not os.path.exists(csv_path):
            return None
        return pd.read_csv(csv_path)
    except Exception:
        return None


def render_claverogenerador():
    """Renderiza la vista del generador de claveros (sin set_page_config)."""
    st.markdown("<h1 style='text-align: center;'>🛠️ Generador de Claveros de Frenos</h1>", unsafe_allow_html=True)
    st.markdown("---")

    df = cargar_datos_view()
    if df is None:
        st.error("❌ No se encontró o no es válido 'data/jerarquia.csv'.")
        return

    # Initialize session state keys
    if 'nivel1_sel' not in st.session_state:
        st.session_state.nivel1_sel = None
    if 'nivel2_sel' not in st.session_state:
        st.session_state.nivel2_sel = None
    if 'componente_sel' not in st.session_state:
        st.session_state.componente_sel = None

    st.subheader("📋 Paso 1: Seleccione el sistema principal")

    nivel1_opciones = df[df['componente_nivel1'].notna()]['componente_nivel1'].unique()
    nivel1_opciones = sorted([opt for opt in nivel1_opciones if opt != ''])

    if len(nivel1_opciones) == 0:
        st.warning("⚠️ No se encontraron sistemas principales en el archivo CSV.")
        return

    nivel1_seleccionado = st.selectbox("Sistema principal:", options=['Seleccione...'] + list(nivel1_opciones), key='select_nivel1')
    if nivel1_seleccionado == 'Seleccione...':
        return
    st.session_state.nivel1_sel = nivel1_seleccionado

    df_filtrado_n1 = df[df['componente_nivel1'] == nivel1_seleccionado]
    st.markdown("---")

    st.subheader("📋 Paso 2: Seleccione el subsistema")
    nivel2_opciones = df_filtrado_n1[df_filtrado_n1['nivel'] == 2]['componente'].unique()
    nivel2_opciones = sorted([opt for opt in nivel2_opciones if opt != ''])

    nivel3_sin_nivel2 = df_filtrado_n1[(df_filtrado_n1['nivel'] == 3) & ~df_filtrado_n1['clavero'].str[:7].isin(df_filtrado_n1[df_filtrado_n1['nivel'] == 2]['clavero'])]
    if not nivel3_sin_nivel2.empty:
        nivel2_opciones = list(nivel2_opciones) + ['Otros']

    nivel2_seleccionado = st.selectbox("Subsistema:", options=['Seleccione...'] + list(nivel2_opciones), key='select_nivel2')
    if nivel2_seleccionado == 'Seleccione...':
        return
    st.session_state.nivel2_sel = nivel2_seleccionado

    if nivel2_seleccionado == 'Otros':
        df_filtrado_n2 = nivel3_sin_nivel2
    else:
        df_filtrado_n2 = df_filtrado_n1[df_filtrado_n1['componente_nivel2'] == nivel2_seleccionado]

    st.markdown("---")
    st.subheader("📋 Paso 3: Seleccione el componente")

    componentes_finales = df_filtrado_n2[df_filtrado_n2['nivel'] == 3]['componente'].unique()
    if len(componentes_finales) > 0:
        componente_seleccionado = st.selectbox("Componente:", options=['Seleccione...'] + list(sorted(componentes_finales)), key='select_componente')
        if componente_seleccionado == 'Seleccione...':
            return
        st.session_state.componente_sel = componente_seleccionado
    else:
        st.info("ℹ️ Este subsistema no tiene componentes específicos de nivel 3.")
        st.session_state.componente_sel = None

    st.markdown("---")
    if st.button("🔧 Generar Clavero", type="primary", use_container_width=True):
        st.session_state.select_actuacion = 'Seleccione...'
        st.session_state.clavero_generado = None
        st.session_state.ruta_seleccion = []

        if st.session_state.componente_sel:
            resultado = df[(df['componente_nivel1'] == st.session_state.nivel1_sel) & (df['componente_nivel2'] == st.session_state.nivel2_sel) & (df['componente'] == st.session_state.componente_sel) & (df['nivel'] == 3)]
            st.session_state.ruta_seleccion = [st.session_state.nivel1_sel, st.session_state.nivel2_sel, st.session_state.componente_sel]
        elif st.session_state.nivel2_sel:
            resultado = df[(df['componente_nivel1'] == st.session_state.nivel1_sel) & (df['componente'] == st.session_state.nivel2_sel) & (df['nivel'] == 2)]
            st.session_state.ruta_seleccion = [st.session_state.nivel1_sel, st.session_state.nivel2_sel]
        else:
            resultado = df[(df['componente'] == st.session_state.nivel1_sel) & (df['nivel'] == 1)]
            st.session_state.ruta_seleccion = [st.session_state.nivel1_sel]

        if not resultado.empty:
            st.session_state.clavero_generado = resultado.iloc[0]['clavero']
        else:
            st.session_state.clavero_generado = None

    if st.session_state.get('clavero_generado'):
        clavero_generated = st.session_state.clavero_generado
        df_diccionario = cargar_diccionario_view()
        if df_diccionario is not None:
            actuaciones = df_diccionario[df_diccionario.iloc[:, 0] == clavero_generated]
            st.markdown('---')
            st.markdown('### ✅ Resultado')
            st.write('**Ruta seleccionada:**')
            for i, item in enumerate(st.session_state.get('ruta_seleccion', []), 1):
                display_item = item.strip() if isinstance(item, str) else item
                st.write(f"  {i}. {display_item}")

            st.markdown(f"<div style='background-color: #e7f3fe; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3; margin-top: 20px;'><h2 style='color: #0b5394; margin: 0;'>➡️ Clavero base:</h2><h1 style='color: #0b5394; margin: 10px 0 0 0; font-size: 36px;'>{clavero_generated}</h1></div>", unsafe_allow_html=True)

            if not actuaciones.empty:
                descripcion_col = actuaciones.columns[3] if len(actuaciones.columns) > 3 else actuaciones.columns[1]
                actuaciones_validas = actuaciones[actuaciones[descripcion_col].notna() & (actuaciones[descripcion_col].astype(str).str.strip() != '')]
                if actuaciones_validas.empty:
                    st.info('ℹ️ No existe actuación preexistente para este clavero.')
                else:
                    st.markdown('### 📋 Seleccione la actuación realizada:')
                    opciones_map = {}
                    for _, row in actuaciones_validas.iterrows():
                        display = f"{row.iloc[1]} - {row.iloc[3]}"
                        opciones_map[display] = (row.iloc[1], row.iloc[3])
                    st.session_state.opciones_map = opciones_map
                    actuacion = st.selectbox('Tipo de actuación:', options=['Seleccione...'] + list(opciones_map.keys()), key='select_actuacion')
                    if st.session_state.get('select_actuacion') and st.session_state.select_actuacion != 'Seleccione...':
                        sel = st.session_state.select_actuacion
                        codigo_txx, descripcion = st.session_state.opciones_map[sel]
                        clavero_final = f"{clavero_generated}{codigo_txx}"
                        st.markdown('---')
                        st.markdown('### 📑 Resumen')
                        st.write(f"**Clavero base:** {clavero_generated}")
                        st.write(f"**Actuación:** {sel}")
                        st.write(f"**Código:** {codigo_txx}")
                        st.write(f"**Descripción:** {descripcion}")
                        st.markdown(f"<div style='background-color: #d4edda; padding: 12px; border-radius: 8px; border-left: 4px solid #28a745; margin-top: 10px;'><strong>Clavero final:</strong> <span style='font-size:18px'>{clavero_final}</span></div>", unsafe_allow_html=True)

    st.markdown('---')
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Generador de Claveros v1.0 | Sistema de Mantenimiento Ferroviario</p>", unsafe_allow_html=True)
