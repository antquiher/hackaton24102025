import streamlit as st
import vistas.modelo_form as modelo_form
import vistas.tabla_averias_modelo as tabla_averias_modelo
import vistas.claverogenerador_view as claverogenerador_view

def load_css():
    """Injects custom CSS to style the Streamlit app like a corporate landing page."""
    st.markdown("""
        <style>
            /* --- Global Styles --- */
            /* Hide Streamlit's default header and footer */
            [data-testid="stHeader"] {
                visibility: hidden;
                height: 0;
                position: relative;
            }
            [data-testid="stFooter"] {
                visibility: hidden;
                height: 0;
                position: relative;
            }
            
            /* Set a clean background and text color */
            .stApp {
                background-color: #F4F6F8; /* Light grey background */
                color: #333333; /* Dark text */
            }

            /* --- Custom Header --- */
            .header {
                padding: 2rem 1rem;
                background-color: #FFFFFF;
                border-bottom: 2px solid #E0E0E0;
                text-align: center;
                margin-bottom: 2rem;
            }
            .header h1 {
                color: #C62828; /* Primary deep red */
                font-weight: 700;
                margin: 0;
            }
            .header p {
                color: #555555;
                font-size: 1.25rem;
                margin-top: 0.5rem;
            }

            /* --- Option Cards --- */
            .card-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 2rem;
                padding: 1rem;
            }
            .card {
                background-color: #FFFFFF;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                padding: 2rem;
                width: 350px;
                text-align: left;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border-top: 5px solid #C62828; /* Red accent */
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            }
            .card h3 {
                color: #C62828;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            .card p {
                font-size: 1rem;
                color: #444444;
                min-height: 100px; /* Ensure cards have similar height */
            }

            /* --- Button Styling --- */
            .stButton > button {
                width: 100%;
                border-radius: 8px;
                background-color: #C62828; /* Red */
                color: #FFFFFF;
                border: 2px solid #B71C1C;
                padding: 0.75rem 1rem;
                font-weight: 600;
                transition: background-color 0.3s ease, color 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #FFFFFF;
                color: #C62828;
                border: 2px solid #B71C1C;
            }

        </style>
    """, unsafe_allow_html=True)

def main():
    # Set page config
    st.set_page_config(page_title="Mobility Solutions", layout="wide")
    
    # Load custom CSS
    load_css()

    # --- Custom Header with company logo above the title ---
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Logo_CAF.svg/330px-Logo_CAF.svg.png"
    st.markdown(f"""
        <div class="header">
            <img src="{logo_url}" alt="CAF logo" style="height:80px; display:block; margin: 0 auto 10px auto;" />
            <h1>Hackaton 25/10/2025</h1>
            <p>Trust in Future</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Three Options ---
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("""
            <div class="card">
                <h3>Encuetra tu clavero</h3>
                <p>
                    En este apartado podras introducir los datos del problema y te generará una clavero adecuado según el caso.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver encuetra tu clavero", key="b1"):
            st.session_state.page = "ClaveroGenerador"
            # In a real app, you would use st.switch_page() or similar logic
            # st.toast is not available in all Streamlit versions; use st.info instead
            

    with col2:
        st.markdown("""
            <div class="card">
                <h3>Averías - IA</h3>
                <p>
                    Cuando un operario tenga un problema aquí podra buscar alguna solución con Inteligencia Artificial que le ayude a resolverlo.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.link_button("Ver servicio de averías", "http://172.25.15.152:8502/"):
            st.session_state.page = "Averías"

    with col3:
        st.markdown("""
            <div class="card">
                <h3>Buscar averías por modelo</h3>
                <p>
                    Aquí podrás buscar averías específicas pasadas introduciendo el modelo del tren.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver averías por modelo", key="b3"):
            st.session_state.page = "Modelo"

    # Display the selected "page" for demonstration or render the modelo_form view
    if "page" in st.session_state:
        if st.session_state.page == "Modelo":
            # Render the modelo_form view in-place (avoids calling set_page_config twice)
            modelo_form.render_model_form()
        elif st.session_state.page == "TablaModelo":
            # Render the example results table for the selected model
            tabla_averias_modelo.render_table_for_model()
        elif st.session_state.page == "ClaveroGenerador":
            # Render the claverogenerador view in-place
            claverogenerador_view.render_claverogenerador()

if __name__ == "__main__":
    main()