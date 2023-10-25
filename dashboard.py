import utils
import streamlit as st
import pandas as pd
import plotly.express as px
from millify import prettify


def main():
    st.title("EVENTS DASHBOARD")

    with st.container():
        c1, c2 = st.columns(2)

        # Artist ID input
        chartmetric_id = int(c1.number_input("Chartmetric ID del artista", min_value=1, step=1))

        # Mexico state selection
        selected_state = c2.selectbox("Estado:", utils.mexico_states)


    st.subheader("Estadísticas del estado")
    state_events_df = utils.get_state_stats(selected_state)

    with st.container():
        c1, c2 = st.columns(2)

        c1.metric("Número de eventos", len(state_events_df))
        c2.metric("Número de venues", state_events_df['GMAPS_PLACE_NAME'].nunique())

    with st.container():
        c1, c2 = st.columns(2)
        c1.metric("Rating promedio de venues", round(state_events_df['VENUE_RATING'].mean(), 2))
        c2.metric("Promedio de ratings en venues", prettify(round(state_events_df['VENUE_RATINGS_TOTAL'].mean()))) 

    st.write("\n")

    # Get the count of events by venue/city
    venue_counts = state_events_df.groupby(['GMAPS_PLACE_NAME', 'VENUE_CITY']).size().reset_index(name='Count')
    # sort values by the events count
    venue_counts = venue_counts.sort_values(by='Count', ascending=False)
    # replace column names
    venue_counts = venue_counts.rename(columns={'GMAPS_PLACE_NAME': 'Venue', 'VENUE_CITY': 'Ciudad', 'Count': 'Eventos'})
    st.subheader("Eventos por venue")
    st.dataframe(venue_counts)
    st.write("\n")
    

    # Get the more popular (the mode) venue
    most_popular_venue = state_events_df['GMAPS_PLACE_NAME'].mode().iloc[0]
    # Get the count of the more popular venue
    events_count = state_events_df[state_events_df['GMAPS_PLACE_NAME'] == most_popular_venue].shape[0]
    st.metric("Venue con más eventos", f"{most_popular_venue}: {events_count} eventos")
    st.write("\n")


    # Get the unique venues and events count by city
    city_info = state_events_df.groupby('VENUE_CITY').agg({'VENUE': 'count', 'GMAPS_PLACE_NAME': 'nunique'})
    city_info = city_info.sort_values(by='VENUE', ascending=False)
    st.subheader("Eventos y venues por ciudad:")
    st.dataframe(city_info.rename(columns={'VENUE_CITY': 'Ciudad', 'GMAPS_PLACE_NAME': 'Venues', 'VENUE': 'Eventos'}))
    st.write("\n")


    # Pie chart VENUE_GENRE
    # drop duplicates to just consider 1 time each venue
    # drop nan in venue_genre to ensure data for the pie chart
    venue_genres = state_events_df[['GMAPS_PLACE_NAME', 'VENUE_GENRE']].drop_duplicates().dropna(subset=['VENUE_GENRE'])
    if not venue_genres.empty:
        genre_counts = venue_genres['VENUE_GENRE'].value_counts()
        fig_genre = px.pie(genre_counts, names=genre_counts.index, title="Géneros de los venues")
        st.plotly_chart(fig_genre)
    
    else:
        st.warning("No hay datos disponibles sobre el género de los venues")
    
    st.write("\n")


    # Pie chart HAS_PARKING
    # drop duplicates to just consider 1 time each venue
    # drop nan in has_parking to ensure data for the pie chart
    venue_parkings = state_events_df[['GMAPS_PLACE_NAME', 'HAS_PARKING']].drop_duplicates().dropna(subset=['HAS_PARKING'])
    if not venue_parkings.empty:
        parking_counts = venue_parkings['HAS_PARKING'].value_counts()
        fig_parking = px.pie(parking_counts, names=parking_counts.index, title="Opciones de estacionamiento")
        st.plotly_chart(fig_parking)
    
    else:
        st.warning("No hay datos disponibles sobre el estacionamiento de los venues")
    
    st.write("\n")


    # Get the distinct venues, city and capacity
    # drop duplicates to just consider 1 time each venue
    # drop nan in venue_capacity to ensure data for the pie chart
    venues_capacity = state_events_df[['GMAPS_PLACE_NAME', 'VENUE_CAPACITY', 'VENUE_CITY']].drop_duplicates().dropna(subset=['GMAPS_PLACE_NAME', 'VENUE_CAPACITY'])

    if not venues_capacity.empty:
        venues_capacity = venues_capacity.sort_values(by='VENUE_CAPACITY', ascending=False)
        st.subheader("Venues por aforo")
        st.dataframe(venues_capacity)

        # Get the largest CAPACITY
        max_capacity_value = state_events_df['VENUE_CAPACITY'].max()
        # Get the name of the venue with the largest capacity
        max_capacity_venue = state_events_df[state_events_df['VENUE_CAPACITY'] == max_capacity_value]['VENUE'].iloc[0]
        st.metric("Venue más grande", f"{max_capacity_venue}:  {prettify(round(max_capacity_value))} personas")
    
    else:
        st.warning("No hay venues con datos de aforo disponibles")

    st.write("\n")
    

    # Get the INEGI stats by city
    average_city_data = state_events_df.groupby('VENUE_CITY')[['TOTAL_POPULATION', 'MALE_POPULATION_PCT', 'FEMALE_POPULATION_PCT',
                                                               'PCT_10', 'PCT_30', 'PCT_50', 'PCT_70', 'PCT_90', 'PCT_95', 'PCT_LOWER_CLASS',
                                                               'PCT_LOWER_MIDDLE_CLASS', 'PCT_UPPER_MIDDLE_CLASS', 'PCT_UPPER_CLASS']].mean().reset_index()
    average_city_data = average_city_data.sort_values(by='TOTAL_POPULATION', ascending=False)
    average_city_data = average_city_data.rename(columns={
        'VENUE_CITY': 'Ciudad',
        'PCT_10': 'Ingresos pct 10',
        'PCT_30': 'Ingresos pct 30',
        'PCT_50': 'Ingresos pct 50',
        'PCT_70': 'Ingresos pct 70',
        'PCT_90': 'Ingresos pct 90',
        'PCT_95': 'Ingresos pct 95',
        'PCT_LOWER_CLASS': '% clase baja',
        'PCT_LOWER_MIDDLE_CLASS': '% clase media baja',
        'PCT_UPPER_MIDDLE_CLASS': '% clase media alta',
        'PCT_UPPER_CLASS': '% a clase alta',
        'TOTAL_POPULATION': 'Población total',
        'MALE_POPULATION_PCT': '% hombres',
        'FEMALE_POPULATION_PCT': '% mujeres'
    })
    st.subheader("Datos demográficos de INEGI")
    st.dataframe(average_city_data)


if __name__ == "__main__":
    main()