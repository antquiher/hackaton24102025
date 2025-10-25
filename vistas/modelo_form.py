import streamlit as st
from typing import List, Dict, Tuple

from logica.modelo import get_models, give_claveros


# Small constants to avoid duplicate-literal linter warnings
PRIMARY_PLACEHOLDER = "-- Selecciona modelo principal --"
SECONDARY_PLACEHOLDER = "-- Selecciona subtipo/modelo secundario --"
COLOR_PRIMARY = "#C62828"
COLOR_PRIMARY_DARK = "#B71C1C"


def load_css() -> None:
    """Load minimal CSS used by other views (kept small and consistent)."""
    st.markdown(
        f"""
        <style>
            [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
            [data-testid="stFooter"] {{ visibility: hidden; height: 0; }}
            .stApp {{ background-color: #F4F6F8; color: #333333; }}
            .header {{ padding: 2rem 1rem; background-color: #FFFFFF; border-bottom: 2px solid #E0E0E0; text-align: center; margin-bottom: 2rem; }}
            .header h1 {{ color: {COLOR_PRIMARY}; font-weight: 700; margin: 0; }}
            .header p {{ color: #555555; font-size: 1.1rem; margin-top: 0.5rem; }}
            .card {{ background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 1.5rem; width: 100%; text-align: left; border-top: 5px solid {COLOR_PRIMARY}; }}
            .card h3 {{ color: {COLOR_PRIMARY}; margin-bottom: 1rem; }}
            .stButton > button {{ width: 100%; border-radius: 8px; background-color: {COLOR_PRIMARY}; color: #FFFFFF; border: 2px solid {COLOR_PRIMARY_DARK}; padding: 0.6rem 1rem; font-weight: 600; }}
            .stButton > button:hover {{ background-color: #FFFFFF; color: {COLOR_PRIMARY}; border: 2px solid {COLOR_PRIMARY_DARK}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_primary_choice(choice: str) -> str:
    """Normalize the label chosen in the primary selectbox to a compact model code.

    Strategy:
    - Strip a leading 'Modelo ' (case-insensitive) if present.
    - Trim whitespace.
    - If the resulting token is short (<=3 chars) return it as-is, else return the last 2 chars.
    """
    if not choice:
        return ""
    s = choice.strip()
    low = s.lower()
    if low.startswith("modelo "):
        s = s[len("modelo ") :].strip()
    if len(s) <= 3:
        return s
    return s[-2:]


def _format_claveros_map(claveros: Dict[str, int]) -> List[Tuple[str, str]]:
    """Turn a mapping clavero->count into a sorted list of (display_label, clavero).

    Returns items sorted by count desc then by clavero code.
    Example display: 'FRE010113 (12)'
    """
    items = list(claveros.items())
    # sort by count desc, then key
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return [(f"{k} ({v})", k) for k, v in items]


def render_model_form() -> None:
    """Render the model selection form.

    - Uses `get_models()` for primary options.
    - Uses `give_claveros(model_code)` to get a dict clavero->count and shows labels
      like 'CLAVERO (count)'. Stores the selected clavero code in
      `st.session_state['selected_secondary']` so the results view can call `give_work()`.
    """
    load_css()

    st.markdown(
        """
        <div class="header">
            <h1>Selección de Modelos</h1>
            <p>Selecciona un modelo principal y un subtipo para continuar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Obtain primary models from data layer
        try:
            models_set = get_models()
            primary_models: List[str] = sorted([m for m in models_set if m and m != "EMPTY"])
            if not primary_models:
                raise ValueError("empty primary list")
        except Exception:
            primary_models = [f"Modelo {c}" for c in ["A1", "A2", "A3", "B1", "B2", "C1", "C2", "D1", "E1", "F1"]]

        primary_choice = st.selectbox("Modelo principal", [PRIMARY_PLACEHOLDER] + primary_models, key="primary_model")

        selected_secondary_display = None
        secondary_models_display: List[str] = []

        if primary_choice != PRIMARY_PLACEHOLDER:
            model_code = normalize_primary_choice(primary_choice)
            try:
                claveros_map = give_claveros(model_code) or {}
                if isinstance(claveros_map, dict) and claveros_map:
                    formatted = _format_claveros_map(claveros_map)
                    # formatted: list of (display, clavero)
                    display_labels = [d for d, _ in formatted]
                    # store mapping for later resolution
                    display_to_clavero = {d: c for d, c in formatted}
                    secondary_models_display = display_labels
                else:
                    # fallback example labels
                    display_to_clavero = {f"Submodelo {i}": f"SUB{i}" for i in range(1, 11)}
                    secondary_models_display = list(display_to_clavero.keys())
            except Exception:
                display_to_clavero = {f"Submodelo {i}": f"SUB{i}" for i in range(1, 11)}
                secondary_models_display = list(display_to_clavero.keys())

            selected_secondary_display = st.selectbox(
                "Modelo secundario",
                [SECONDARY_PLACEHOLDER] + secondary_models_display,
                key="secondary_model",
            )
        else:
            st.info("Selecciona primero un modelo principal para habilitar el segundo desplegable.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Button area (centered)
    can_continue = (
        primary_choice != PRIMARY_PLACEHOLDER
        and selected_secondary_display is not None
        and selected_secondary_display != SECONDARY_PLACEHOLDER
    )

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if not can_continue:
            st.button("Siguiente", key="next_disabled", disabled=True)
        else:
            if st.button("Siguiente", key="next"):
                # Persist selections for the results view
                st.session_state["selected_primary"] = primary_choice
                # Resolve the clavero code from display_to_clavero when possible
                try:
                    clavero_code = display_to_clavero.get(selected_secondary_display, selected_secondary_display)
                except Exception:
                    clavero_code = selected_secondary_display
                # store the clavero code so give_work() can use it
                st.session_state["selected_secondary"] = clavero_code
                st.session_state["selected_secondary_label"] = selected_secondary_display
                st.session_state["selected_primary_code"] = normalize_primary_choice(primary_choice)
                st.session_state["page"] = "TablaModelo"
                return


def main() -> None:
    try:
        st.set_page_config(page_title="Seleccionar modelo", layout="wide")
    except Exception:
        pass
    render_model_form()


if __name__ == "__main__":
    main()

import streamlit as st
import streamlit.components.v1 as components

def load_css():
    """Re-use the same CSS as the main view for consistent styling."""
    st.markdown("""
        <style>
            /* --- Global Styles --- */
            [data-testid="stHeader"] { visibility: hidden; height: 0; position: relative; }
            [data-testid="stFooter"] { visibility: hidden; height: 0; position: relative; }
            .stApp { background-color: #F4F6F8; color: #333333; }
            .header { padding: 2rem 1rem; background-color: #FFFFFF; border-bottom: 2px solid #E0E0E0; text-align: center; margin-bottom: 2rem; }
            .header h1 { color: #C62828; font-weight: 700; margin: 0; }
            .header p { color: #555555; font-size: 1.25rem; margin-top: 0.5rem; }
            .card { background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 2rem; width: 100%; text-align: left; transition: transform 0.3s ease, box-shadow 0.3s ease; border-top: 5px solid #C62828; }
            .card h3 { color: #C62828; font-weight: 600; margin-bottom: 1rem; }
            .stButton > button { width: 100%; border-radius: 8px; background-color: #C62828; color: #FFFFFF; border: 2px solid #B71C1C; padding: 0.75rem 1rem; font-weight: 600; }
            .stButton > button:hover { background-color: #FFFFFF; color: #C62828; border: 2px solid #B71C1C; }
        </style>""", unsafe_allow_html=True)
    def render_model_form():
        """Renderiza la UI del formulario de modelos sin llamar a st.set_page_config().
        Esto permite que `main_view.py` importe y muestre la vista sin reconfigurar la página.
        """
        load_css()

        st.markdown("""
            <div class="header">
                <h1>Selección de Modelos (Demo)</h1>
                <p>Selecciona un modelo principal y un subtipo para continuar.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # Primer desplegable: 10 modelos de ejemplo
            primary_models = [
                "Modelo A1",
                "Modelo A2",
                "Modelo A3",
                "Modelo B1",
                "Modelo B2",
                "Modelo C1",
                "Modelo C2",
                "Modelo D1",
                "Modelo E1",
                "Modelo F1",
            ]

            placeholder_primary = "-- Selecciona modelo principal --"
            primary_choice = st.selectbox("Modelo principal", [placeholder_primary] + primary_models, key="primary_model")

            # Mostrar/activar el segundo desplegable solo si se ha seleccionado un modelo real
            secondary_models = [
                "Submodelo 1",
                "Submodelo 2",
                "Submodelo 3",
                "Submodelo 4",
                "Submodelo 5",
                "Submodelo 6",
                "Submodelo 7",
                "Submodelo 8",
                "Submodelo 9",
                "Submodelo 10",
            ]

            selected_secondary = None
            if primary_choice != placeholder_primary:
                placeholder_secondary = "-- Selecciona subtipo/modelo secundario --"
                selected_secondary = st.selectbox("Modelo secundario", [placeholder_secondary] + secondary_models, key="secondary_model")
            else:
                st.info("Selecciona primero un modelo principal para habilitar el segundo desplegable.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Habilitar botón 'Siguiente' solo cuando ambos existan y no sean placeholders
        can_continue = (
            primary_choice != placeholder_primary and
            selected_secondary is not None and
            selected_secondary != "-- Selecciona subtipo/modelo secundario --"
        )

        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            if not can_continue:
                st.button("Siguiente", key="next_disabled", disabled=True)
            else:
                if st.button("Siguiente", key="next"):
                    # Guardamos selección en session_state por si la necesitamos
                    st.session_state['selected_primary'] = primary_choice
                    st.session_state['selected_secondary'] = selected_secondary

                    # Redirigir a otra web (placeholder). Cambia la URL según necesites.
                    target_url = "https://example.com/next-step"
                    # Usamos un pequeño snippet JS para forzar la navegación en el navegador
                    components.html(f"""
                        <script>
                            window.location.href = "{target_url}";
                        </script>
                    , height=0)
                        window.location.href = "{target_url}";
                    </script>
                """, height=0)


def main():
    st.set_page_config(page_title="Seleccionar modelo", layout="wide")
    render_model_form()


if __name__ == "__main__":
    main()
