import snowflake.connector
import pandas as pd
import os
import json
import streamlit as st
from millify import millify

events_df = pd.read_csv('events_dash_dataset.csv')



# Database credentials
ctx = snowflake.connector.connect(
    user=str(os.getenv("SNOWFLAKE_USER", '')),
    password=str(os.getenv("SNOWFLAKE_PASSWORD", '')),
    account=str(os.getenv("SNOWFLAKE_ACCOUNT", '')),
    warehouse=str(os.getenv("SNOWFLAKE_WAREHOUSE", '')),
    database=str(os.getenv("SNOWFLAKE_DATABASE", '')),
    schema=str(os.getenv("SNOWFLAKE_SCHEMA", ''))
)
cur = ctx.cursor()


# Get artists basic data
def get_artists():
    sql = f"""select
                artist_id,
                name,
                case 
                    when disambiguation is not null then concat(name, ' - ', disambiguation)
                    else name
                end as name_disambiguation
            from core.artists
            order by name;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_artist: ", e)
        return pd.DataFrame()


# Get Mexico states
def get_states():
    sql = f"""select
                distinct state
            from demographics.income_by_city
            order by state;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_states: ", e)
        return pd.DataFrame()


# Get the cities of a state
def get_state_cities(state):
    sql = f"""select
                distinct city
            from demographics.income_by_city
            where state = '{state}'
            order by city;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_state_cities: ", e)
        return pd.DataFrame()
    

# Get city venues
# NOTA: se filtraron aquellos que staffs skippearon
def get_city_venues(state, city):
    sql = f"""select
                place_id as venue_id,
                name as venue_name
            from core.places
            where state = '{state}' and city = '{city}'
            and skip_reason is null
            order by name;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        # Consider the case when there are no match venues for the city
        if df.empty:
            return pd.DataFrame({'VENUE_ID': [0], 'VENUE_NAME': ['Sin venues disponibles']})
        else:
            return df
    
    except Exception as e:
        print("Error en query get_city_venues: ", e)
        return pd.DataFrame()
    

# Music genres
# TO DO: check other genres sources
def get_genres():
    sql = f"""select
                distinct genre
            from core.music_genres
            order by genre;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_genres: ", e)
        return pd.DataFrame()


# Get artist metadata from chartmetric
# TO DO: Fix to just query one table
def get_artist_cm_metadata(artist_id):
    # First try in table 1
    sql = f"""select
                cm_response:artists[0]:id::string as cm_id,
                coalesce(cm_response:artists[0]:image_url::string, 'images/no_image.jpg') as image_url,
                cm_response:artists[0]:sp_followers::float as sp_followers
            from raw.chartmetric.ids
            where artist_id = '{artist_id}';
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        # If the df is empty, try in the other table
        if df.empty:
            sql = f"""select
                        cm_response:artists[0]:id::string as cm_id,
                        coalesce(cm_response:artists[0]:image_url::string, 'images/no_image.jpg') as image_url,
                        cm_response:artists[0]:sp_followers::float as sp_followers
                    from raw.chartmetric.ids_by_name
                    where artist_id = '{artist_id}';
                    """
            
            cur.execute(sql)
            # Overwrite dataframe
            df = cur.fetch_pandas_all()  
        
            # If is ampty again, return default df
            if df.empty:
                return pd.DataFrame({'CM_ID': [0], 'IMAGE_URL': ['no_image.jpg']})
            # Else return the result
            else:
                return df
            
        # Else return the result
        else:
            return df
    
    except Exception as e:
        print("Error en query get_artist_cm_metadata: ", e)
        return pd.DataFrame()
    

# Get artist metadata from musicbrainz
def get_artist_mb_metadata(artist_id):
    sql = f"""select
                a.name,
                a.gender,
                a.country,
                a.tags,
                a.disambiguation,
                aa.name as area
            from prod.core.artists a
            left join staging.musicbrainz.stg_musicbrainz_areas aa
            on a.area_id = aa.area_id
            where artist_id = '{artist_id}';
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_artist_mb_metadata: ", e)
        return pd.DataFrame()


# Get artist current snapshot
def get_artist_snapshot(artist_cm_id):
    sql = f"""select
                first_value(spotify_followers ignore nulls) over (partition by id order by timestamp desc) as sp_followers,
                first_value(spotify_popularity ignore nulls) over (partition by id order by timestamp desc) as sp_popularity,
                first_value(spotify_listeners ignore nulls) over (partition by id order by timestamp desc) as sp_listeners,
                first_value(spotify_followers_to_listeners_ratio ignore nulls) over (partition by id order by timestamp desc) as sp_followers_to_listeners_ratio,
                first_value(facebook_likes ignore nulls) over (partition by id order by timestamp desc) as fb_likes,
                first_value(facebook_talks ignore nulls) over (partition by id order by timestamp desc) as fb_talks,
                first_value(twitter_followers ignore nulls) over (partition by id order by timestamp desc) as tw_followers,
                first_value(twitter_retweets ignore nulls) over (partition by id order by timestamp desc) as tw_retweets,
                first_value(instagram_followers ignore nulls) over (partition by id order by timestamp desc) as ig_followers,
                first_value(youtube_channel_subscribers ignore nulls) over (partition by id order by timestamp desc) as yt_subscribers,
                first_value(youtube_channel_views ignore nulls) over (partition by id order by timestamp desc) as yt_views,
                first_value(youtube_channel_comments ignore nulls) over (partition by id order by timestamp desc) as yt_comments
            from prod.artists.fan_metrics
            where id = '{artist_cm_id}'
            limit 1;
            """
    try:
        cur.execute(sql)
        print(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_artist_snapshot: ", e)
        return pd.DataFrame()  


# Get the 5 latest boletia events of an artist
def get_latest_boletia_events(artist_id):
    sql = f"""select
                e.name as evento,
                coalesce(e.gmaps_place_name, e.venue) as venue,
                coalesce(e.gmaps_place_city, city) as city,
                date(e.started_at) as fecha
            from core.events as e
            join core.event_artists as ea on e.event_id = ea.event_id
            where ea.artist_id = '{artist_id}'
            order by fecha desc
            limit 5;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_latest_boletia_events: ", e)
        return pd.DataFrame()
    

# Get the 5 latest global events of an artist
def get_latest_global_events(artist_cm_id):
    sql = f"""select
                venue,
                state as ciudad,
                date(timestamp) as fecha
            from raw.songkick.events
            where artist_id = '{artist_cm_id}'
            order by fecha desc
            limit 5;
            """
    try:
        cur.execute(sql)
        print(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        return df
    
    except Exception as e:
        print("Error en query get_latest_global_events: ", e)
        return pd.DataFrame()


# Get IG stats of an artist
def get_city_ig_followers(artist_id, city):
    sql = f"""select
                closest_ig_date,
                top_countries,
                top_cities
            from raw.chartmetric.ig_audience_data
            where artist_id = '{artist_id}'
            order by closest_ig_date desc
            limit 1;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

       # First try to look for the city data 
        cities = json.loads(df.iloc[0]['TOP_CITIES'])
        for dict in cities:
            if dict["name"] == city:
                return dict["followers"], city
            
        # If there is no match then look for the country data
        countries = json.loads(df.iloc[0]['TOP_COUNTRIES'])
        for dict in countries:
            if dict["name"] == "Mexico":
                return dict["followers"], 'Mexico'
            
        # If there is no match again return 0
        return 0
    
    except Exception as e:
        print("Error en query get_city_ig_followers: ", e)
        return pd.DataFrame(), ''
    

# Get Spotify listeners of an artist in a specific city, state of mexico
def get_city_sp_listeners(artist_cm_id, city, state):
    sql = f"""select
                location_type,
                location_name,
                response
            from raw.chartmetric.spotify_monthly_listeners
            where id = '{artist_cm_id}'
            and (location_name = '{city}' or location_name = '{state}' or location_name = 'Mexico')
            order by location_type
            limit 10;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()
        listeners_list = json.loads(df.iloc[0]['RESPONSE'])
        city = df.iloc[0]['LOCATION_NAME']
        # Get the latest dictionary with the listeners metric
        dict = listeners_list[-1]
        return dict["listeners"], city
    
    except Exception as e:
        print("Error en query get_city_sp_listeners: ", e)
        return 0, ''
    

# Get Spotify listeners of an artist
def get_general_sp_listeners(artist_cm_id):
    sql = f"""select
                --location_type,
                location_name,
                response
            from raw.chartmetric.spotify_monthly_listeners
            where id = '{artist_cm_id}'
            and location_type = 'city'
            order by location_type
            limit 15;
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        # Comvert the json string into dictionaries
        df['RESPONSE'] = df['RESPONSE'].apply(lambda x: json.loads(x))
        # Expand the dictionaries list (1 row for list element)
        df_expanded = df.explode('RESPONSE')
        # Convert dictionaries into separete columns
        df_expanded = pd.concat([df_expanded.drop(['RESPONSE'], axis=1), df_expanded['RESPONSE'].apply(pd.Series)], axis=1)
        # Convert timestp column into a datetime and trunc just date
        df_expanded['timestp'] = pd.to_datetime(df_expanded['timestp']).dt.date
        # Drop data from cities outside Mexico
        df_expanded = df_expanded[df_expanded['code2'] == 'MX']
        # Rename columns
        df_expanded = df_expanded.rename(columns={'timestp': 'Fecha', 'listeners': 'Escuchas', 'LOCATION_NAME': 'Locación'})
        
        return df_expanded
    
    except Exception as e:
        print("Error en query get_city_sp_listeners: ", e)
        return pd.DataFrame()


# Get ig followers
def get_ig_followers(artist):
    # Filter df
    filtered_df = events_df[events_df['ARTIST_NAME'] == artist]

    # Calculate and return the mean of IG_FOLLOWERS
    return round(filtered_df['IG_FOLLOWERS'].mean())


# Get previous events
def get_previous_event(artist_id, venue_id):
    sql = f"""select
                hr.*,
                e.name as event_name,
                coalesce(e.gmaps_place_name, venue) as venue,
                coalesce(e.gmaps_place_city, city) as city,
                date(e.started_at) as event_date
            from raw.chartmetric.events_historical_ranks as hr
            join prod.core.events as e on e.event_id = hr.event_id
            where hr.artist_id = '{artist_id}' and e.gmaps_place_id = '{venue_id}'
            order by e.started_at desc
            limit 1
            """
    
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_previous_event: ", e)
        return pd.DataFrame()
    

# Get previous events
def get_last_event(artist_id):
    sql = f"""select
                hr.*,
                e.name as event_name,
                coalesce(e.gmaps_place_name, venue) as venue,
                coalesce(e.gmaps_place_city, city) as city,
                date(e.started_at) as event_date
            from raw.chartmetric.events_historical_ranks as hr
            join prod.core.events as e on e.event_id = hr.event_id
            where hr.artist_id = '{artist_id}'
            and hr.sp_followers>1
            order by e.started_at desc
            limit 1
            """
    
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_last_event: ", e)
        return pd.DataFrame()


# Get city stats
def get_city_stats(city, state):
    sql = f"""select
                total_population,
                male_population,
                female_population,
                pct_lower_class * 100 as "Baja",
                pct_lower_middle_class * 100 as "Media baja",
                pct_upper_middle_class * 100 as "Media alta",
                pct_upper_class * 100 as "Alta",
                pct_10,
                pct_30,
                pct_50,
                pct_70,
                pct_90,
                pct_95,
                households
            from prod.demographics.income_by_city
            where city = '{city}' and state = '{state}'
            """
    
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_city_stats: ", e)
        return pd.DataFrame()


# Get best venues in town
# NOTA: Se filtraron los venues skippeados por los staffs
# y se consideran aquellos que tengan capacity +- 15% de los boletos que desean venderse
def get_best_venues(state, city, num_tickets):
    sql = f"""select
                place_id as venue_id,
                name as venue_name,
                website,
                phone_number,
                postal_code,
                address,
                latitude,
                longitude,
                rating,
                user_ratings_total,
                venue_genre,
                has_parking,
                owner,
                owner_legal_name,
                capacity
            from core.places
            where state = '{state}' and city = '{city}'
            and skip_reason is null
            and capacity between {num_tickets*0.85} and {num_tickets*1.15}
            and venue_genre in ('DJ / Dance / Electronica', 'Rock', 'Hip-Hop / Rap / Batallas de Rap', 'Alternativa', 'Trópical', 'Concierto', 'Folklorica', 'Blues y Jazz')
            order by user_ratings_total desc, rating desc
            limit 3
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_best_venues: ", e)
        return pd.DataFrame()


# Show venue card
def show_venue_card(venue, capacity, website, phone_number, address, opt_num):
    # If is the first venue option, then is the best
    if opt_num == 0:
        st.info("⭐ **Recomendado para tu evento**")
    else:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")

    st.subheader(f"**{venue}**")
    st.write(f"**Aforo:** {millify(capacity)} personas")
    if website is not None:
        st.write(f"**Página web:** {website}")
    if phone_number is not None:
        st.write(f"**Teléfono:** {phone_number}")
    if address is not None:
        st.write(f"**Dirección:** {address}")

    # Botón "Conocer Venue"
    #return st.button("Conocer Venue", key=f"button_{venue}")


# Show venue info
def show_venue_info(venue, capacity, contact, recent_events):
    st.write("\n")
    st.write("\n")
    st.subheader(f"Datos del venue")
    st.write(f"**{venue}**")
    st.write(f"**Aforo:** {capacity}")
    st.write(f"**Contacto:** {contact}")

    st.subheader("Últimos eventos de artistas similares")

    data = {
        'Artista': ['Artista1', 'Artista2', 'Artista3'],
        'Fecha': ['2022-01-01', '2022-02-15', '2022-03-20'],
        'Tickets Vendidos': [100, 150, 120]
    }
    df_events = pd.DataFrame(data)
    st.dataframe(df_events, hide_index=True)
    st.map(latitude=19.4326, longitude=-99.1332, size=20, color='#0044ff')
    st.markdown(f"Ubicación del venue")


# Show artist data for comparison
def show_artist_data(artist):   
    st.image(artist['Foto'], caption=artist['Nombre'], use_column_width=True)
    st.write(f"**Nombre:** {artist['Nombre']}")
    st.write(f"**Contacto:** {artist['Contacto']}")
    st.write(f"**Audiencia:** {artist['Audiencia']}")
    st.table(artist['UltimosEventos'])


# Get potencial cities and venues
# NOTA: De momento calculado en ratings y aforo
def get_potencial_cities_venues(state, city, num_tickets):
    sql = f"""select
                state as estado,
                city as ciudad,
                name as venue,
                capacity as aforo,
                rating,
                user_ratings_total as ratings_usuarios,
                venue_genre as genero
            from core.places
            where city != '{city}'
            and skip_reason is null
            and capacity between {num_tickets*0.85} and {num_tickets*1.15}
            and venue_genre in ('DJ / Dance / Electronica', 'Rock', 'Hip-Hop / Rap / Batallas de Rap', 'Alternativa', 'Trópical', 'Concierto', 'Folklorica', 'Blues y Jazz')
            order by user_ratings_total desc, rating desc
            limit 5
            """
    try:
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_potencial_cities_venues: ", e)
        return pd.DataFrame()


# Get similar artist
def get_similar_artists(artist_id, artist_cm_id):
    sql = f"""select
                ac.artist_id,
                ac.name,
                ac.disambiguation,
                ac.tags,
                cm.cm_response:artists[0]:id::string as cm_id,
                coalesce(cm.cm_response:artists[0]:image_url::string, 'images/no_image.jpg') as image_url,
                cm.cm_response:artists[0]:sp_followers::float as sp_followers
            from prod.core.artists as a
            join prod.core.artists as ac
            on a.area_id = ac.area_id and a.artist_type = ac.artist_type and a.country = ac.country
            join raw.chartmetric.ids_by_name as cm
            on cm.artist_id = ac.artist_id
            where a.artist_id = '{artist_id}'
            and ac.artist_id != '{artist_id}'
            and ac.tags is not null
            --and ARRAY_CONTAINS(a.tags[0]::variant, ac.tags)
            limit 5;
            """
    try:
        print(sql)
        cur.execute(sql)
        # Converting data into a dataframe
        df = cur.fetch_pandas_all()

        return df
    
    except Exception as e:
        print("Error en query get_similar_artists: ", e)
        return pd.DataFrame()