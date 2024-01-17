import utils
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        venue_id = st.session_state["venue_id"]
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
        

        # IG section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        ig_followers, ig_location = utils.get_city_ig_followers(artist_id, city)
        if ig_followers > 0:
            st.subheader(f"Audiencia de Instagram de {artist_name} en {ig_location}")
            st.metric("Seguidores ", millify(ig_followers, precision=2))
        else:
            st.subheader(f"Audiencia de Instagram ")
            st.info(f"No hay datos de Instagram de {artist_name} para {city}")


        # Spotify section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        sp_listeners, sp_location = utils.get_city_sp_listeners(artist_cm_id, city, state)
        if sp_listeners > 0:
            st.subheader(f"Audiencia de Spotify de {artist_name} en {sp_location}")
            st.metric("Escuchas", millify(sp_listeners, precision=2))
        else:
            st.subheader(f"Audiencia de Spotify de {artist_name} en {city}")
            st.info(f"No hay datos de Spotify de {artist_name} para {city}")


        # Previous presentations of the artist on venue section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader("Presentación del artista en el recinto")

        previous_event = utils.get_previous_event(artist_id, venue_id)
        last_event = utils.get_last_event(artist_id)

        if previous_event.empty:
            st.info(f"No hay datos disponibles de eventos de {artist_name} en {venue_name}")

        else:
            st.write(f"**Venue:** {venue_name}")
            st.write(f"**Fecha:** {previous_event.iloc[0]['EVENT_DATE']}")
            data = {
                'Red Social': ['Instagram', 
                               'Spotify', 
                               'YouTube', 
                               'Facebook'],
                'Anterior': [previous_event.iloc[0]['INS_FOLLOWERS'], 
                                       previous_event.iloc[0]['SP_FOLLOWERS'], 
                                       previous_event.iloc[0]['YCS_SUBSCRIBERS'], 
                                       previous_event.iloc[0]['FS_LIKES']],
                'Actual': [last_event.iloc[0]['INS_FOLLOWERS'], 
                                       last_event.iloc[0]['SP_FOLLOWERS'], 
                                       last_event.iloc[0]['YCS_SUBSCRIBERS'], 
                                       last_event.iloc[0]['FS_LIKES']]
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x='Red Social', y=['Anterior', 'Actual'],
                labels={'value': 'Ranking', 'variable': 'Ranking'},
                barmode='group',  # Agrupa las barras para cada categoría
                color_discrete_map={'Anterior': 'lightblue', 'Actual': 'darkblue'},
                orientation='v')  # 'v' para vertical, invierte el eje y)
            st.plotly_chart(fig)
            st.info('Nota: entre menor sea el ranking, mayor es la popularidad del artista.')

        
        # Demographics section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        city_stats = utils.get_city_stats(city, state)
        st.subheader(f"Distribución de población por género en {city}")
        st.write(f"**Ciudad:** {city}")
        st.write(f"**Población:** {millify(city_stats.iloc[0]['TOTAL_POPULATION'], precision=2)} habitantes")
        data = {'Género': ['Hombres', 'Mujeres'], 
                'Población': [city_stats.iloc[0]['MALE_POPULATION'], city_stats.iloc[0]['FEMALE_POPULATION']]}
        df = pd.DataFrame(data)
        fig = px.pie(df, names='Género', values='Población', hole=0.7)
        st.plotly_chart(fig)


        # Income percentiles section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader(f"Percentiles de ingreso promedio por familia en {city}")
        st.write(f"**Ciudad:** {city}")
        st.write(f"**Familias:** {millify(city_stats.iloc[0]['HOUSEHOLDS'])}")
        income_percentiles = city_stats[['PCT_10', 'PCT_30', 'PCT_50', 'PCT_70', 'PCT_90', 'PCT_95']]
        # Transform the data for the plot
        income_percentiles_melted = income_percentiles.melt(value_name='Income', var_name='Percentile')
        # Create a piechart
        fig = px.area(income_percentiles_melted, x='Percentile', y='Income',
                       labels={'Income': 'Ingreso promedio (MXN)', 'Percentile': 'Percentil'})
        # Add data points
        fig.add_trace(go.Scatter(x=income_percentiles_melted['Percentile'], y=income_percentiles_melted['Income'],
                         mode='markers', marker=dict(color='red', size=8),
                         name='Valor del percentil'))
        st.plotly_chart(fig)


        # Class distribution section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader(f"Distribución de población por clases sociales en {city}")
        st.write(f"**Ciudad:** {city}")
        st.write(f"**Población:** {millify(city_stats.iloc[0]['TOTAL_POPULATION'], precision=2)} habitantes")
        st.write(f"**Familias:** {millify(city_stats.iloc[0]['HOUSEHOLDS'])}")
        # Transform the data for the plot
        df_melted = pd.melt(city_stats[["Baja", "Media baja", "Media alta", "Alta"]])
        df_melted = df_melted.rename(columns={'variable': 'Clase', 'value': 'Porcentaje'})
        # Create a piechart
        fig = px.pie(df_melted, names='Clase', values='Porcentaje')
        st.plotly_chart(fig)


        # Audience section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        #st.subheader("Audiencia")

        data = {
            'Ciudad': ['CDMX', 'GDL', 'MTY', 'PUE', 'VER'],
            'Instagram': [100, 150, 120, 80, 90],
            'Spotify': [50, 70, 80, 40, 60],
            'YouTube': [80, 100, 90, 60, 70],
            'Facebook': [120, 80, 100, 70, 50]
        }
        df = pd.DataFrame(data)

        fig = px.bar(df, x='Ciudad', y=['Instagram', 'Spotify', 'YouTube', 'Facebook'],
                    title='Audiencia por Ciudad',
                    labels={'value': 'Audiencia en miles', 'variable': 'Red Social'},
                    barmode='stack') 
        #st.plotly_chart(fig)


        # Audience growth section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader(f"Crecimiento de audiencia de {artist_name} en Spotify")
        sp_listeners_df = utils.get_general_sp_listeners(artist_cm_id)

        if sp_listeners_df.empty:
            st.info("No hay datos del crecimiento de audiencia de {artist_name}")
        else:
            # Line chart
            fig = px.line(sp_listeners_df, x='Fecha', y='Escuchas', color='Locación')
            fig.update_xaxes(type='date')  # Show by date
            st.plotly_chart(fig)


        # Best venues section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader(f"Mejores venues de {city}")
        best_venues = utils.get_best_venues(state, city, num_tickets)

        if best_venues.empty:
            st.info("No hay datos de venues adecuados para tu evento en la ciudad seleccionada.")

        else:

            venue_columns = st.columns(len(best_venues))

            for i, col in enumerate(venue_columns):

                with col:
                     utils.show_venue_card(best_venues.iloc[i]["VENUE_NAME"], 
                                                   best_venues.iloc[i]["CAPACITY"], 
                                                   best_venues.iloc[i]["WEBSITE"],
                                                   best_venues.iloc[i]["PHONE_NUMBER"],
                                                   best_venues.iloc[i]["ADDRESS"],
                                                   i)
            
                #if button:
                #    utils.show_venue_info(best_venues.iloc[i]["VENUE_NAME"], 10000, "contac@auditoriobb.com", 5)


        # Potencial cities section
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.subheader("Ciudades y venues potenciales")
        st.dataframe(utils.get_potencial_cities_venues(state, city, num_tickets), hide_index=True)


if __name__ == "__main__":
    main()