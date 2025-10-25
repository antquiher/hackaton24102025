import streamlit as st
import pandas as pd
import os




# Configuración de la página
st.set_page_config(
    page_title="Generador de Claveros",
    page_icon="🛠️",
    layout="centered"
)

# Título principal
st.markdown("<h1 style='text-align: center;'>🛠️ Generador de Claveros de Frenos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Función para cargar el CSV de jerarquía
@st.cache_data
def cargar_datos():
    """Carga el archivo CSV con la jerarquía de componentes"""
    try:
        # Intentar cargar desde el mismo directorio
        if os.path.exists('data\jerarquia.csv'):
            df = pd.read_csv('data\jerarquia.csv')
        else:
            st.error("❌ Error: No se encontró el archivo 'jerarquia.csv' en el directorio actual.")
            st.info("📁 Asegúrate de que el archivo 'jerarquia.csv' esté en la misma carpeta que este programa.")
            return None
        
        # Validar columnas necesarias
        columnas_requeridas = ['clavero', 'componente', 'nivel', 'nivel1', 'nivel2', 
                              'componente_nivel1', 'componente_nivel2']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error("❌ Error: El archivo CSV no tiene las columnas correctas.")
            st.info(f"Columnas requeridas: {', '.join(columnas_requeridas)}")
            return None
        
        return df
    except Exception as e:
        st.error(f"❌ Error al leer el archivo CSV: {str(e)}")
        return None

# Función para cargar el diccionario CSV
@st.cache_data
def cargar_diccionario():
    """Carga el archivo CSV con el diccionario de actuaciones"""
    try:
        if os.path.exists('data\diccionario.csv'):
            df = pd.read_csv('data\diccionario.csv')
            return df
        else:
            st.error("❌ Error: No se encontró el archivo 'diccionario.csv' en el directorio actual.")
            st.info("📁 Asegúrate de que el archivo 'diccionario.csv' esté en la misma carpeta que este programa.")
            return None
    except Exception as e:
        st.error(f"❌ Error al leer el archivo diccionario.csv: {str(e)}")
        return None

# Cargar datos
df = cargar_datos()

if df is not None:
    st.success("✅ Archivo cargado correctamente")
    st.markdown("---")
    
    # Inicializar variables de sesión
    if 'nivel1_sel' not in st.session_state:
        st.session_state.nivel1_sel = None
    if 'nivel2_sel' not in st.session_state:
        st.session_state.nivel2_sel = None
    if 'componente_sel' not in st.session_state:
        st.session_state.componente_sel = None
    
    # NIVEL 1: Selección de sistema principal
    st.subheader("📋 Paso 1: Seleccione el sistema principal")
    
    # Obtener componentes de nivel 1 únicos (no vacíos)
    nivel1_opciones = df[df['componente_nivel1'].notna()]['componente_nivel1'].unique()
    nivel1_opciones = sorted([opt for opt in nivel1_opciones if opt != ''])
    
    if len(nivel1_opciones) > 0:
        nivel1_seleccionado = st.selectbox(
            "Sistema principal:",
            options=['Seleccione...'] + list(nivel1_opciones),
            key='select_nivel1'
        )
        
        if nivel1_seleccionado != 'Seleccione...':
            st.session_state.nivel1_sel = nivel1_seleccionado
            
            # Filtrar datos por nivel 1
            df_filtrado_n1 = df[df['componente_nivel1'] == nivel1_seleccionado]

           # st.dataframe(df_filtrado_n1)
            
            st.markdown("---")
            
            # NIVEL 2: Selección de subsistema
            st.subheader("📋 Paso 2: Seleccione el subsistema")
            
            # Obtener componentes de nivel 2
            nivel2_opciones = df_filtrado_n1[df_filtrado_n1['nivel']== 2]['componente'].unique()
            nivel2_opciones = sorted([opt for opt in nivel2_opciones if opt != ''])
            
            # Verificar si hay componentes de nivel 3 sin correspondencia en nivel 2
            nivel3_sin_nivel2 = df_filtrado_n1[
                (df_filtrado_n1['nivel'] == 3) & 
                ~df_filtrado_n1['clavero'].str[:7].isin(df_filtrado_n1[df_filtrado_n1['nivel'] == 2]['clavero'])
            ]
            
            # Si hay componentes de nivel 3 sin nivel 2 correspondiente, agregar "Otros" a las opciones
            if not nivel3_sin_nivel2.empty:
                nivel2_opciones = list(nivel2_opciones) + ['Otros']
            
            if len(nivel2_opciones) > 0:
                nivel2_seleccionado = st.selectbox(
                    "Subsistema:",
                    options=['Seleccione...'] + list(nivel2_opciones),
                    key='select_nivel2'
                )
                
                if nivel2_seleccionado != 'Seleccione...':
                    st.session_state.nivel2_sel = nivel2_seleccionado
                    
                    # Filtrar datos por nivel 2
                    if nivel2_seleccionado == 'Otros':
                        # Mostrar componentes de nivel 3 sin correspondencia en nivel 2
                        df_filtrado_n2 = nivel3_sin_nivel2
                    else:
                        # Filtrado normal por nivel 2
                        df_filtrado_n2 = df_filtrado_n1[df_filtrado_n1['componente_nivel2'] == nivel2_seleccionado]
                    
                    st.markdown("---")
                
                    
                    # NIVEL 3: Selección de componente final
                    st.subheader("📋 Paso 3: Seleccione el componente")
                    
                    # Obtener componentes finales (nivel 3)
                    componentes_finales = df_filtrado_n2[df_filtrado_n2['nivel'] == 3]['componente'].unique()
                    
                    if len(componentes_finales) > 0:
                        componente_seleccionado = st.selectbox(
                            "Componente:",
                            options=['Seleccione...'] + list(sorted(componentes_finales)),
                            key='select_componente'
                        )
                        
                        if componente_seleccionado != 'Seleccione...':
                            st.session_state.componente_sel = componente_seleccionado
                    else:
                        st.info("ℹ️ Este subsistema no tiene componentes específicos de nivel 3.")
                        st.session_state.componente_sel = None

            

            else:
                st.info("ℹ️ Este sistema no tiene subsistemas específicos.")
                st.session_state.nivel2_sel = None
                st.session_state.componente_sel = None
            
            st.markdown("---")

            # BOTÓN GENERAR CLAVERO
            if st.button("🔧 Generar Clavero", type="primary", use_container_width=True):
                # Reiniciar selección de actuación al generar un nuevo clavero
                st.session_state.select_actuacion = 'Seleccione...'
                # Determinar qué nivel está seleccionado y guardar en sesión
                st.session_state.clavero_generado = None
                st.session_state.ruta_seleccion = []

                # Buscar el clavero correspondiente según las selecciones
                if st.session_state.componente_sel:
                    # Nivel 3 completo
                    resultado = df[
                        (df['componente_nivel1'] == st.session_state.nivel1_sel) &
                        (df['componente_nivel2'] == st.session_state.nivel2_sel) &
                        (df['componente'] == st.session_state.componente_sel) &
                        (df['nivel'] == 3)
                    ]
                    st.session_state.ruta_seleccion = [
                        st.session_state.nivel1_sel,
                        st.session_state.nivel2_sel,
                        st.session_state.componente_sel
                    ]
                elif st.session_state.nivel2_sel:
                    # Nivel 2
                    resultado = df[
                        (df['componente_nivel1'] == st.session_state.nivel1_sel) &
                        (df['componente'] == st.session_state.nivel2_sel) &
                        (df['nivel'] == 2)
                    ]
                    st.session_state.ruta_seleccion = [
                        st.session_state.nivel1_sel,
                        st.session_state.nivel2_sel
                    ]
                else:
                    # Solo nivel 1
                    resultado = df[
                        (df['componente'] == st.session_state.nivel1_sel) &
                        (df['nivel'] == 1)
                    ]
                    st.session_state.ruta_seleccion = [st.session_state.nivel1_sel]

                if not resultado.empty:
                    st.session_state.clavero_generado = resultado.iloc[0]['clavero']
                else:
                    st.session_state.clavero_generado = None

            # Si ya existe un clavero generado en la sesión, mostrar opciones y resumen
            if st.session_state.get('clavero_generado'):
                clavero_generated = st.session_state.clavero_generado

                # Cargar diccionario de actuaciones
                df_diccionario = cargar_diccionario()
                if df_diccionario is not None:
                    actuaciones = df_diccionario[df_diccionario.iloc[:, 0] == clavero_generated]

                    st.markdown("---")
                    st.markdown("### ✅ Resultado")
                    st.write("**Ruta seleccionada:**")
                    for i, item in enumerate(st.session_state.get('ruta_seleccion', []), 1):
                        # Normalizar strings para evitar diferencias de formato (espacios en componentes nivel 3)
                        display_item = item.strip() if isinstance(item, str) else item
                        st.write(f"  {i}. {display_item}")

                    # Mostrar clavero base
                    st.markdown(
                        f"<div style='background-color: #e7f3fe; padding: 20px; border-radius: 10px; "
                        f"border-left: 5px solid #2196F3; margin-top: 20px;'>"
                        f"<h2 style='color: #0b5394; margin: 0;'>➡️ Clavero base:</h2>"
                        f"<h1 style='color: #0b5394; margin: 10px 0 0 0; font-size: 36px;'>{clavero_generated}</h1>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if not actuaciones.empty:
                        # Filtrar actuaciones que tengan descripción no vacía
                        descripcion_col = actuaciones.columns[3] if len(actuaciones.columns) > 3 else actuaciones.columns[1]
                        actuaciones_validas = actuaciones[actuaciones[descripcion_col].notna() & (actuaciones[descripcion_col].astype(str).str.strip() != '')]

                        if actuaciones_validas.empty:
                            st.info("ℹ️ No existe actuación preexistente para este clavero.")
                        else:
                            st.markdown("### 📋 Seleccione la actuación realizada:")

                            # Crear lista de opciones con descripción -> mapa display -> (codigo, descripcion)
                            opciones_map = {}
                            for _, row in actuaciones_validas.iterrows():
                                display = f"{row.iloc[1]} - {row.iloc[3]}"
                                opciones_map[display] = (row.iloc[1], row.iloc[3])

                            # Guardar mapa en session_state para uso posterior si se quiere
                            st.session_state.opciones_map = opciones_map

                            # Mostrar selectbox usando la misma key para que Streamlit mantenga la selección
                            actuacion = st.selectbox(
                                "Tipo de actuación:",
                                options=['Seleccione...'] + list(opciones_map.keys()),
                                key='select_actuacion'
                            )

                            # Si el usuario ha elegido una actuación, mostrar un resumen sencillo y persistente
                            if st.session_state.get('select_actuacion') and st.session_state.select_actuacion != 'Seleccione...':
                                sel = st.session_state.select_actuacion
                                codigo_txx, descripcion = st.session_state.opciones_map[sel]
                                clavero_final = f"{clavero_generated}{codigo_txx}"

                                st.markdown("---")
                                st.markdown("### 📑 Resumen")
                                st.write(f"**Clavero base:** {clavero_generated}")
                                st.write(f"**Actuación:** {sel}")
                                st.write(f"**Código:** {codigo_txx}")
                                st.write(f"**Descripción:** {descripcion}")
                                st.markdown(
                                    f"<div style='background-color: #d4edda; padding: 12px; border-radius: 8px; "
                                    f"border-left: 4px solid #28a745; margin-top: 10px;'>"
                                    f"<strong>Clavero final:</strong> <span style='font-size:18px'>{clavero_final}</span>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
                    else:
                        st.warning("⚠️ No se encontraron actuaciones definidas para este clavero en el diccionario.")
                else:
                    st.warning("⚠️ No se pudo cargar el diccionario de actuaciones.")
    else:
        st.warning("⚠️ No se encontraron sistemas principales en el archivo CSV.")
else:
    st.info("👆 Por favor, asegúrate de que el archivo 'jerarquia.csv' esté disponible para continuar.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>"
    "Generador de Claveros v1.0 | Sistema de Mantenimiento Ferroviario"
    "</p>",
    unsafe_allow_html=True
)