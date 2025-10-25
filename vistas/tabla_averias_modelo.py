import streamlit as st
import pandas as pd
from typing import Optional

from logica.modelo import give_work

# Column name constants (avoid repeated literals)
COL_FECHA = "Fecha"
COL_ORDEN = "Orden de trabajo"
COL_AVARIA = "Descripción avería"
COL_REPAR = "Descripción reparación"
COL_COMMENT = "Comentarios"

def _load_css():
    """Small CSS for the table header."""
    st.markdown(
        """
        <style>
            .header { padding: 1.25rem 0.5rem; background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0; text-align: center; margin-bottom: 1rem; }
            .header h1 { color: #C62828; font-weight: 700; margin: 0; font-size: 1.25rem; }
            .header p { color: #555555; margin: 0.25rem 0 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_table_for_model(primary: Optional[str] = None, secondary: Optional[str] = None) -> None:
    """Render an example table for the given model.

    If primary/secondary are None, they will be taken from session_state keys
    'selected_primary' and 'selected_secondary'. Shows a header with
    format 'secondary-primary' and a sample dataframe. Includes a 'Volver'
    button that clears 'page' from session_state to return to the previous view.
    """
    if primary is None:
        primary = st.session_state.get("selected_primary")
    if secondary is None:
        secondary = st.session_state.get("selected_secondary")

    if not primary or not secondary:
        st.warning("No hay modelo seleccionado. Selecciona primary y secondary antes de ver la tabla.")
        return

    _load_css()

    if(primary == "--"):
        title = f"{secondary}"
        st.markdown(
            
            f"""
            <div class="header">
                <h1>➡️ {title}</h1>
                <p>Resultados del  clavero {secondary} sin modelo</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        title = f"{secondary}-{primary}"
        st.markdown(
            
            f"""
            <div class="header">
                <h1>➡️ {title}</h1>
                <p>Resultados del modelo {primary} con clavero {secondary}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Load real rows from the data layer using give_work(clavero)
    try:
        works = give_work(secondary,primary)
        # give_work returns a list of rows [fecha_creacion, descripcion_ot, descripcion_averia, descripcion_reparacion]
        if not works:
            st.info("No se encontraron órdenes de trabajo para la selección proporcionada.")
            df = pd.DataFrame(columns=[COL_FECHA, COL_ORDEN, COL_AVARIA, COL_REPAR, COL_COMMENT])
        else:
            df = pd.DataFrame(works, columns=[COL_FECHA, COL_ORDEN, COL_AVARIA, COL_REPAR, COL_COMMENT])
    except Exception as exc:
        st.error(f"Error al cargar datos: {exc}")
        df = pd.DataFrame(columns=[COL_FECHA, COL_ORDEN, COL_AVARIA, COL_REPAR, COL_COMMENT])

    st.dataframe(df, use_container_width=True)

    if st.button("⏮️ Volver", use_container_width=True):
        if "page" in st.session_state:
            st.session_state.pop("page", None)
        # Return to allow the app to re-run and show previous view
        return


if __name__ == "__main__":
    # Quick local test
    render_table_for_model(primary="Modelo A1", secondary="Submodelo 1")
