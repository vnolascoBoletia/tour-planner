import pandas as pd

events_df = pd.read_csv('events_dash_dataset.csv')

# Mexico states
mexico_states = events_df['VENUE_STATE'].drop_duplicates().sort_values()

# Months dictionary
months = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}

# Months dictionary
days = {
    0: 'Domingo',
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado'
}

# Order or the months
months_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Order of the days of the week
days_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

def get_state_stats(state):
    state_fields = ['VENUE', 'GMAPS_PLACE_NAME', 'VENUE_CITY', 'LATITUDE', 'LONGITUDE', 
                    'VENUE_RATING', 'VENUE_RATINGS_TOTAL', 'VENUE_GENRE', 'HAS_PARKING', 
                    'VENUE_OWNER', 'VENUE_OWNER_TYPE', 'VENUE_CAPACITY', 'PCT_10',
                    'PCT_30', 'PCT_50', 'PCT_70', 'PCT_90', 'PCT_95', 'PCT_LOWER_CLASS',
                    'PCT_LOWER_MIDDLE_CLASS', 'PCT_UPPER_MIDDLE_CLASS', 'PCT_UPPER_CLASS',
                    'TOTAL_POPULATION', 'MALE_POPULATION_PCT', 'FEMALE_POPULATION_PCT']
    state_fields_df = events_df[state_fields]

    return state_fields_df[events_df['VENUE_STATE']==state]

def get_start_day_distribution():
    return events_df['START_DAY']

def get_lead_time_data():
    return events_df['LEAD_TIME_DAYS']

def get_dayofweek_start_data():
    return events_df['DAYOFWEEK_START'].map(days)

def get_start_month_data():
    return events_df['START_MONTH'].map(months)

def get_subcategory_count():
    return events_df['SUBCATEGORY'].value_counts()

def get_venue_state_data():
    return events_df['VENUE_STATE']

def get_commercial_value_data():
    return events_df['COMMERCIAL_VALUE']

def get_ticket_price_distribution():
    return events_df['TICKET_TYPE_PRICE']

def get_ticket_quantity_distribution():
    return events_df['TICKET_TYPE_QUANTITY']

def get_gmv_distribution():
    return events_df['TT_VALUE']