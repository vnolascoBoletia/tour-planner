import utils
import streamlit as st
import plotly.express as px
import pandas as pd
from millify import millify

def main():
    st.title("TOUR PLANNER")

    if "filters_status" not in st.session_state:
        st.warning("Por favor responde las preguntas del onboarding para poder mostrar las estadísticas.")

    else:
        artist_id = st.session_state["artist_id"]
        artist_name = st.session_state["artist_name"]
        artist_cm_id = st.session_state["artist_cm_id"]
        genre = st.session_state["genre"]
        state = st.session_state["state"]
        city = st.session_state["city"]
        venue_name = st.session_state["venue_name"]
        event_date = st.session_state["event_date"]
        num_tickets = st.session_state["num_tickets"]

        artist_cm_metadata = utils.get_artist_cm_metadata(artist_id)
        artist_mb_metadata = utils.get_artist_mb_metadata(artist_id)

        # Sidebar options
        st.sidebar.subheader("FILTROS")
        st.sidebar.subheader("")
        st.sidebar.write(f"**Artista:** {artist_name}")
        st.sidebar.write(f"**Estado:** {state}")
        st.sidebar.write(f"**Ciudad:** {city}")
        st.sidebar.write(f"**Fecha:** {event_date}")
        st.sidebar.write(f"**Género:** {genre}")
        st.sidebar.write(f"**Venue:** {venue_name}")
        st.sidebar.write(f"**Boletos:** {num_tickets}")

        # Similar artist section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader("Artistas similares")

        artistas = [
            {'Nombre': 'Artista 1', 'Foto': 'images/no_image.jpg', 'Contacto': 'contacto1@example.com', 'Audiencia': 100000, 'Engagement Rate': 8.5},
            {'Nombre': 'Artista 2', 'Foto': 'images/no_image.jpg', 'Contacto': 'contacto2@example.com', 'Audiencia': 80000, 'Engagement Rate': 7.2},
            {'Nombre': 'Artista 3', 'Foto': 'images/no_image.jpg', 'Contacto': 'contacto3@example.com', 'Audiencia': 120000, 'Engagement Rate': 9.0},
            {'Nombre': 'Artista 4', 'Foto': 'images/no_image.jpg', 'Contacto': 'contacto4@example.com', 'Audiencia': 90000, 'Engagement Rate': 8.1},
            {'Nombre': 'Artista 5', 'Foto': 'images/no_image.jpg', 'Contacto': 'contacto5@example.com', 'Audiencia': 110000, 'Engagement Rate': 8.8}
        ]


        similar_artist_df = utils.get_similar_artists(artist_id, artist_cm_id)
        #st.write(similar_artist_df)

        for i, col in enumerate(st.columns(len(similar_artist_df))):

            with col:

                st.image(similar_artist_df.iloc[i]['IMAGE_URL'], caption=similar_artist_df.iloc[i]['NAME'], width=120)
                # Apply circle format to the image
                st.markdown(
                    """
                    <style>
                        img {
                            border-radius: 50%;
                        }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.write(f"**Nombre:** {similar_artist_df.iloc[i]['NAME']}")
                if pd.notna(similar_artist_df.iloc[i]['SP_FOLLOWERS']):
                    st.write(f"**Audiencia:** { millify(similar_artist_df.iloc[i]['SP_FOLLOWERS']) } followers de Spotify")
                st.write(f"**Tags:** {similar_artist_df.iloc[i]['TAGS']}")

                artist_button = st.button("Comparar", key=f"button_artist_{i}")
            
            if artist_button:
                comparison_artist_id = similar_artist_df.iloc[i]['ARTIST_ID']
                comparison_artist_cm_id = similar_artist_df.iloc[i]['CM_ID']


                # Artist comparison section
                st.write("\n")
                st.write("\n")
                st.write("\n")
                st.subheader("Comparativa artista vs artista similar")
                
                col1, col2 = st.columns(2)

                with col1:
                    st.image(artist_cm_metadata.iloc[0]['IMAGE_URL'], width=250, caption=artist_name)
                    
                    st.write(f"**{artist_name}**")
                    
                    if artist_mb_metadata.iloc[0]["DISAMBIGUATION"] is not None:
                        st.write(artist_mb_metadata.iloc[0]["DISAMBIGUATION"])

                    if artist_mb_metadata.iloc[0]["COUNTRY"] is not None:
                        st.write(f"**Pais:** {artist_mb_metadata.iloc[0]['COUNTRY']}")

                    if artist_mb_metadata.iloc[0]["TAGS"] is not None:
                        st.write(f"**Tags:** {artist_mb_metadata.iloc[0]['TAGS']}")

                    # Last events section
                    st.write("\n")
                    st.write("\n")
                    st.write("\n")
                    st.subheader("Últimos eventos")
                    
                    # First check global events
                    last_events = utils.get_latest_global_events(artist_cm_id)
                    if last_events.empty:
                        # If there is no global events info then check for boletia events
                        last_events = utils.get_latest_boletia_events(artist_id)
                        if last_events.empty:
                            st.info("No hay información de eventos recientes.")
                        else:
                            st.dataframe(last_events, hide_index=True)

                   

                with col2:
                    similar_artist_cm_metadata = utils.get_artist_cm_metadata(comparison_artist_id)
                    similar_artist_mb_metadata = utils.get_artist_mb_metadata(comparison_artist_id)
                    st.image(similar_artist_cm_metadata.iloc[0]['IMAGE_URL'], width=250, caption=similar_artist_mb_metadata.iloc[0]['NAME'])
                    
                    st.write(f"**{similar_artist_mb_metadata.iloc[0]['NAME']}**")
                    
                    if similar_artist_mb_metadata.iloc[0]["DISAMBIGUATION"] is not None:
                        st.write(similar_artist_mb_metadata.iloc[0]["DISAMBIGUATION"])

                    if similar_artist_mb_metadata.iloc[0]["COUNTRY"] is not None:
                        st.write(f"**Pais:** {similar_artist_mb_metadata.iloc[0]['COUNTRY']}")

                    if similar_artist_mb_metadata.iloc[0]["TAGS"] is not None:
                        st.write(f"**Tags:** {similar_artist_mb_metadata.iloc[0]['TAGS']}")

                    # Last events section
                    st.write("\n")
                    st.write("\n")
                    st.write("\n")
                    st.subheader("Últimos eventos")
                    
                    # First check global events
                    last_events = utils.get_latest_global_events(comparison_artist_cm_id)
                    if last_events.empty:
                        # If there is no global events info then check for boletia events
                        last_events = utils.get_latest_boletia_events(comparison_artist_id)
                        if last_events.empty:
                            st.info("No hay información de eventos recientes.")
                        else:
                            st.dataframe(last_events, hide_index=True)

            
        # Most popular songs section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        #st.subheader("Canción más escuchada de los artistas")
        datos_reproducciones = pd.DataFrame({
            'Artista / Canción': ['Artista Principal / Cancion1', 'Artista 2 / Cancion 2', 'Artista 3 / Cancion 3', 'Artista 4 / Cancion 4', 'Artista 5 / Cancion 5'],
            'Reproducciones': [5000000, 3000000, 2500000, 2000000, 1800000]
        })

        # Crear gráfica de barras con Plotly Express
        fig = px.bar(datos_reproducciones, x='Artista / Canción', y='Reproducciones')
        fig.update_layout(showlegend=False)

        # Mostrar la gráfica en Streamlit
        #st.plotly_chart(fig)


if __name__ == "__main__":
    main()