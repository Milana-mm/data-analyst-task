# # initial plan to use geocoder as part of data_processing failed due to certificates installed for Serbian ID :/
# # workaround to gather city data based on street_address
#
# import requests
# from geopy.geocoders import Nominatim
# import pandas as pd
# response = requests.get('https://nominatim.openstreetmap.org/', verify=False)
# # test: script test_geocoder


import requests
from geopy.geocoders import Nominatim
import pandas as pd
import time


# initialize geocoder
geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)


# function to get city and postal code
def get_city_and_postal_code(row):
    if pd.isna(row['city']):
        location = geolocator.geocode(row['street_address'] + ", USA")  # adding country could help
        time.sleep(1)  # Delay for 1 second between requests
        if location:
            return location.address.split(', ')[-3]
        return row['city']
    else:
        return row['city']


file_path = './data/customers.csv'
df = pd.read_csv(file_path)
missingDataDf = df[df['city'].isna()]


missingDataDf['city'] = missingDataDf.apply(get_city_and_postal_code, axis=1)

# Save the DF to a new CSV file
missingDataDf.to_csv('./temp/missing_val_customers_geo.csv', index=False)

