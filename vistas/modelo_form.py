import streamlit as st
from typing import List, Dict, Tuple

from logica.modelo import get_models, give_claveros


# Small constants to avoid duplicate-literal linter warnings
PRIMARY_PLACEHOLDER = "Seleccione..."
SECONDARY_PLACEHOLDER = "Seleccione..."
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
            <h1>🛠️ Selección de Averías por Modelos</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.subheader("📋 Paso 1: Seleccione el modelo principal")
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

            st.markdown("---")
            st.subheader("📋 Paso 2: Selecciona clavero")

            selected_secondary_display = st.selectbox(
                "Modelo secundario",
                [SECONDARY_PLACEHOLDER] + secondary_models_display,
                key="secondary_model",
            )

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
            st.button("🛠️ Continuar", key="next_disabled", disabled=True, use_container_width=True)
        else:
            if st.button("🛠️ Continuar", key="next", use_container_width=True):
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
