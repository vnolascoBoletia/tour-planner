import utils
import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    st.title("TOUR PLANNER")

    st.header("Onboarding")

    st.write("Responde las siguientes preguntas y te ayudaremos a crear tu evento.")

    # Artist selection
    artists_df = utils.get_artists()

    artist_opt = st.selectbox("¿Con qué artista trabajarás?", artists_df['NAME_DISAMBIGUATION'] )
    artist_row = artists_df[artists_df["NAME_DISAMBIGUATION"] == artist_opt]
    artist_id = artist_row.iloc[0]["ARTIST_ID"]
    artist_name = artist_row.iloc[0]["NAME"]
    
    st.session_state["artist_id"] = artist_id
    st.session_state["artist_name"] = artist_name
    st.session_state["artist_cm_id"] = utils.get_artist_cm_metadata(artist_id).iloc[0]["CM_ID"]


    # Genre selection
    genre = st.selectbox("¿Conoces el género musical que quieres para tu evento?", utils.get_genres())
    st.session_state["genre"] = genre


    # State and city selection
    col1, col2 = st.columns(2)

    with col1:
        state = st.selectbox("¿En qué estado será tu evento?", utils.get_states())
    with col2:
        city = st.selectbox("¿En qué ciudad será tu evento?", utils.get_state_cities(state))
    
    st.session_state["state"] = state
    st.session_state["city"] = city
    

    # Venue selection
    venues_df = utils.get_city_venues(state, city)

    venue_opt = st.selectbox("¿En qué venue se hará tu evento?", venues_df["VENUE_NAME"])
    venue_row = venues_df[venues_df["VENUE_NAME"] == venue_opt]
    venue_id = venue_row.iloc[0]["VENUE_ID"]
    venue_name = venue_row.iloc[0]["VENUE_NAME"]
    st.session_state["venue_id"] = venue_id
    st.session_state["venue_name"] = venue_name


    # Event date selection
    event_date = st.date_input("¿Cuándo será tu evento?", min_value=datetime.today())
    st.session_state["event_date"] = event_date
    

    # Number of tickets selection
    num_tickets = st.number_input("¿Cuántos boletos vas a vender?", min_value=100, step=100)
    st.session_state["num_tickets"] = num_tickets
    
    st.session_state["filters_status"] = True


if __name__ == "__main__":
    main()