import utils
import streamlit as st
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

        # Presentation section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader("Presentación")
        c1, c2 = st.columns(2)

        with c1:
            st.write("\n")
            artist_cm_metadata = utils.get_artist_cm_metadata(artist_id)
            artist_mb_metadata = utils.get_artist_mb_metadata(artist_id)
            # Show artist image
            st.image(artist_cm_metadata.iloc[0]['IMAGE_URL'], width=250, caption=artist_name)
            # Apply circle format to the image
            st.markdown(
                """
                <style>
                    img {
                        border-radius: 60%;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

        with c2:
            # Mostrar el nombre del artista, audiencia y engagement rate
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write(f"**Nombre:** {artist_name}")

            if artist_mb_metadata.iloc[0]["DISAMBIGUATION"] is not None:
                st.write(artist_mb_metadata.iloc[0]["DISAMBIGUATION"])

            if artist_mb_metadata.iloc[0]["COUNTRY"] is not None:
                st.write(f"**Pais:** {artist_mb_metadata.iloc[0]['COUNTRY']}")

            if artist_mb_metadata.iloc[0]["TAGS"] is not None:
                st.write(f"**Tags:** {artist_mb_metadata.iloc[0]['TAGS']}")

            if artist_cm_metadata.iloc[0]['SP_FOLLOWERS'] is not None and artist_cm_metadata.iloc[0]['SP_FOLLOWERS'] != 0:
                st.write(f"**Audiencia:** {millify(artist_cm_metadata.iloc[0]['SP_FOLLOWERS'])} followers en Spotify")


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


        # Social Media info section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader("Redes Sociales")
        
        snapshot = utils.get_artist_snapshot(artist_cm_id)

        c3, c4, c5, c6, c7 = st.columns(5)

        with c3:
            # Show artist image
            st.image("images/spotify.png", width=100)
            st.metric("Escuchas", millify(snapshot.iloc[0]['SP_LISTENERS'], precision=2))
        with c4:
            st.image("images/youtube.png", width=100)
            st.metric("Suscriptores", millify(snapshot.iloc[0]['YT_SUBSCRIBERS'], precision=2))
        with c5:
            st.image("images/facebook.png", width=100)
            st.metric("Likes", millify(snapshot.iloc[0]['FB_LIKES'], precision=2))
        with c6:
            st.image("images/x.png", width=100)
            st.metric("Followers", millify(snapshot.iloc[0]['TW_FOLLOWERS'], precision=2))
        with c7:
            st.image("images/instagram.png", width=100)
            st.metric("Followers", millify(snapshot.iloc[0]['IG_FOLLOWERS'], precision=2))

        


if __name__ == "__main__":
    main()