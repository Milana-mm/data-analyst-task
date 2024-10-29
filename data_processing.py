import pandas as pd
import re
from datetime import datetime
import numpy as np
from geopy.geocoders import Nominatim
import requests

# II Clean
# -- 1.1. Books table
# Define the path - use csv file
file_path = './data/books.csv'
# Load csv file
df = pd.read_csv(file_path)

# # --test
# print(df.head())
# print(df.info())
# print(df.describe())

# --- pages
# keep digits only and remove any special characters
df['pages'] = df['pages'].str.replace(r'\D+', '', regex=True)

# --- price
# reg expr to keep only numbers and up to two decimals
df['price'] = df['price'].str.replace(r'[^\d\.]', '', regex=True)

# Convert the cleaned price to float
df['price'] = df['price'].astype(float)


# --- publishedDate cleaning
# Function to standardize dates
def extract_year(value):
    # If the value is already in YYYY format (4 digits), return it
    if re.match(r'^\d{4}$', str(value)):
        return int(value)
    # Else, try to convert it to datetime and extract the year
    try:
        return pd.to_datetime(value, errors='coerce').year
    except:
        return None  # Return None if it cannot be parsed


# Apply the function to the date column
df['publishedDate'] = df['publishedDate'].apply(extract_year)

# --
# Save cleaned DF to new file
df.to_csv('./temp/cleaned_books.csv', index=False)

# # display option to show all columns - test
# pd.set_option('display.max_columns', None)

# # display the first few rows of the dataframe - test
# print(f"Initial DataFrame {file_path}:")
# print(df.head())


# -- 1.2 Checkouts table
# Define the path - use csv file
file_path = './data/checkouts.csv'

# load csv file
df = pd.read_csv(file_path)

# rename the column
df = df.rename(columns={'id': 'book_id'})

# strip whitespace and ensure column is a string type (leave?)
df['date_checkout'] = df['date_checkout'].astype(str).str.strip()
# remove any non-numeric characters if needed
df['date_checkout'] = df['date_checkout'].str.replace(r'[^0-9]', '', regex=True)

# Convert the date columns to datetime format
df['date_checkout'] = pd.to_datetime(df['date_checkout'], errors='coerce')

# rows where dates are in YYYYMMDD format and resulted in null -
# might not be needed for returned date, but should be standard check
df['date_checkout'] = pd.to_datetime(df['date_checkout'], format='%Y%m%d', errors='coerce')

# # test
# invalid_dates = df[df['date_checkout'].isna()]['date_checkout']
# print(invalid_dates)

df['date_returned'] = pd.to_datetime(df['date_returned'], errors='coerce')

# Define the current date
today = pd.to_datetime(datetime.now().date())

# checkout: dates must be after 1900, can not be after return
# return & checkout: dates must be <= today (exclude far future)
# - assumption: analysis date today (same as 31.May)
# - assumption: return can be empty - not returned
df = df[(df['date_checkout'] >= '1900-01-01') &
        (df['date_checkout'] <= today) &
        ((df['date_returned'] >= '1900-01-01') | df['date_returned'].isna()) &
        ((df['date_returned'] <= today) | df['date_returned'].isna()) &
        ((df['date_checkout'] <= df['date_returned']) | df['date_returned'].isna())]

# calc difference in days and create a new column 'date_difference'
# - assumption: cut of date 31.May (latest return date 21.May)
df['days_until_returned'] = (df['date_returned'].fillna('2019-05-31') - df['date_checkout']).dt.days

# create new column flag for latency
df['late'] = df['days_until_returned'].apply(lambda x: 1 if x > 28 else 0)

# add an ID column starting from 1
df['id'] = range(1, len(df) + 1)
# move the ID column to the first position
cols = ['id'] + [col for col in df.columns if col != 'id']
df = df[cols]

# ---------------
# Save cleaned DF to new file
df.to_csv('./temp/cleaned_checkouts.csv', index=False)

# # display option to show all columns - test
# pd.set_option('display.max_columns', None)

# # display the first few rows of the dataframe - test
# print(f"Initial DataFrame {file_path}:")
# print(df.head())


# -- 1.3 Customers table
# define the path - use csv files
customers = './data/customers.csv'
customers_geo = './temp/missing_val_customers_geo.csv'

# load csv file
df = pd.read_csv(customers)
# in case 1st step of data processing did not work - comment rows 129-139
customers_geo_df = pd.read_csv(customers_geo)

# # keep a copy of the original DF

# join tables
mergedCustomer = df.merge(customers_geo_df, on='id', how='left', suffixes=('', '_geo'))

# populate null values with values in geo file
mergedCustomer['city'] = mergedCustomer['city'].fillna(mergedCustomer['city_geo'])

df = mergedCustomer.drop(columns=mergedCustomer.filter(like='_geo').columns)

# clean all columns by stripping spaces
columns_to_strip = ['name', 'city', 'state', 'street_address', 'gender', 'education', 'occupation']
df[columns_to_strip] = df[columns_to_strip].apply(lambda col: col.str.strip())

# replace multiple spaces with a single space
columns_to_shorten = ['education', 'occupation', 'city', 'state']
df[columns_to_shorten] = df[columns_to_shorten].apply(lambda col: col.str.replace(r'\s+', ' ', regex=True))

# --------- zipcode - might be there is more elegant way to do this
# reg expression to keep only numbers and up to two decimals
df['zipcode'] = df['zipcode'].str.replace(r'[^\d\.]', '', regex=True)

# convert zipcode to int to avoid decimals
df['zipcode'] = df['zipcode'].astype(float)


# --------- birth_date - year is enough
# standardize dates
def extract_year_b(value):
    # if the value is already in YYYY format, return it
    if re.match(r'^\d{4}$', str(value)):
        return int(value)
    # else, try to convert it to datetime and extract the year
    try:
        return pd.to_datetime(value, errors='coerce').year
    except:
        return None  # return None if cannot be parsed


# Apply the function to the date column
df['birth_date'] = df['birth_date'].apply(extract_year_b)

# --------- gender
# Apply the .str.lower()
df['gender'] = df['gender'].str.lower()

# rename columns to avoid duplicated column names in other tables
df = df.rename(columns={'name': 'customer_name'})
df = df.rename(columns={'city': 'customer_city'})

# ---------
# Converts the first character of each word to upper case
columns_to_title = ['customer_city', 'education', 'occupation', 'state']
df[columns_to_title] = df[columns_to_title].apply(lambda col: col.str.title())


# # define the mapping for each character to a numeric value (ponder)
# decided not to go with this > might be useful though
# value_mapping = {
#     'College': 1,
#     'Graduate Degree': 2,
#     'High School': 3,
#     'Others': 4
# }
#
# # map the values in the existing column without replacing it
# df['education_num'] = df['education'].map(value_mapping)
#
# # insert the new column right after the existing one
# # > find the index of the existing column and add the new one immediately after
# col_index = df.columns.get_loc('education') + 1
# df.insert(col_index, 'education_num', df.pop('education_num'))


# populate state based on city value - hardcoded - workaround until geocoder enabled for me
# def update_state(df):
# condition = (df['state'].isnull() & (df['customer_city'] == 'Portland'))
# df.loc[condition, 'state'] = 'Oregon'
def update_state(df):
    # mapping defined
    city_state_mapping = {
        'Portland': 'Oregon',
        'Beaverton': 'Oregon',
        'Hillsboro': 'Oregon',
        'Lake Oswego': 'Oregon',
        'Happy Valley': 'Oregon',
        'Oregon': 'Oregon',  # Optionally included for completeness
        'Vancouver': 'Washington'
    }
    # if empty
    condition = df['state'].isnull()
    # update
    for city, state in city_state_mapping.items():
        df.loc[condition & (df['customer_city'] == city), 'state'] = state


update_state(df)

# Replace None values with "Others"
df['education'] = df['education'].fillna('Others')
df['occupation'] = df['occupation'].fillna('Others')

# ---------------
# Save cleaned DF to new file
df.to_csv('./temp/cleaned_customers.csv', index=False)

# # display option to show all columns - test
# pd.set_option('display.max_columns', None)

# # display the first few rows of the dataframe - test
# print(f"Initial DataFrame {file_path}:")
# print(df.head())


# -- 1.4. Libraries table
# Define the path - use csv file
file_path = './data/libraries.csv'

# Load csv file
df = pd.read_csv(file_path)

# clean all columns by stripping spaces
columns_to_strip = ['name', 'city', 'street_address', 'region']
df[columns_to_strip] = df[columns_to_strip].apply(lambda col: col.str.strip())

# --------- city
# apply formatting - first char to upper, the rest to lower case
df['city'] = df['city'].str.capitalize()

# --------- region
# apply formatting - upper case
df['region'] = df['region'].str.upper()

# --------- postal_code
# reg expression to keep only numbers and up to two decimals
df['postal_code'] = df['postal_code'].str.replace(r'[^\d\.]', '', regex=True)

# rename columns to avoid duplicated column names in other tables and provide clarity
df = df.rename(columns={'name': 'library_name'})


# # Geocoder > to populate city based on address
# does not work for me because of certificates installed for Serbian ID :/
# > ssl.SSLError: not enough data: cadata does not contain a certificate (_ssl.c:4015)
# > SSL Error: HTTPSConnectionPool(host='nominatim.openstreetmap.org', port=443):
# geolocator = Nominatim(user_agent="geoapiExercises")
# response = requests.get('https://nominatim.openstreetmap.org/', verify=False)
#
#
# # Function to get city and postal code
# def get_city_and_postal_code(address):
#     location = geolocator.geocode(address + ", USA")  # Adding country can help
#     if location:
#         return location.address.split(', ')[-3], location.address.split(', ')[-2]  # City and Postal Code
#     return None, None
#
#
# # Apply the function to get city and postal code
# df['customer_city'], df['zipcode'] = zip(*df['street_address'].apply(get_city_and_postal_code))

# instead of geocoder had to perform workaround - separate script to gather city based on customer address


# populate region based on city value
def update_region(df):
    condition = (df['region'].isnull() & (df['city'] == 'Portland'))
    df.loc[condition, 'region'] = 'OR'


# apply
update_region(df)
# until geocoder works for me - keeping city and region empty - but can be calculated based street_address/postcode

# ---------------
# Save cleaned DF to new file
df.to_csv('./temp/cleaned_libraries.csv', index=False)


# # display option to show all columns - test
# pd.set_option('display.max_columns', None)

# # display the first few rows of the dataframe - test
# print(f"Initial DataFrame {file_path}:")
# print(df.head())


# ------------------------------
# SUMMARY
def summarize_changes(original_df, cleaned_df, file_name):
    summary = {}

    # count of rows before and after cleaning
    summary['file_name'] = file_name
    summary['original_count'] = original_df.shape[0]
    summary['cleaned_count'] = cleaned_df.shape[0]

    # # test summary
    # summary['missing_values_before'] = original_df.isnull().sum().to_dict()
    # summary['missing_values_after'] = cleaned_df.isnull().sum().to_dict()
    # summary['data_types_before'] = original_df.dtypes.to_dict()
    # summary['data_types_after'] = cleaned_df.dtypes.to_dict()

    return summary


# list of file names
file_names = [
    "./temp/cleaned_books.csv",
    "./temp/cleaned_checkouts.csv",
    "./temp/cleaned_customers.csv",
    "./temp/cleaned_libraries.csv"
]

# path to original files
original_file_paths = [
    "./data/books.csv",
    "./data/checkouts.csv",
    "./data/customers.csv",
    "./data/libraries.csv"
]

# generate summaries
for original_path, cleaned_file in zip(original_file_paths, file_names):
    try:
        # load the original and cleaned DataFrames
        original_df = pd.read_csv(original_path)
        cleaned_df = pd.read_csv(cleaned_file)

        # generate summary
        change_summary = summarize_changes(original_df, cleaned_df, cleaned_file)

        # print summary
        print(f"Summary for {cleaned_file}:")
        for key, value in change_summary.items():
            print(f"{key}: {value}")
        print("\n" + "=" * 50 + "\n")  # separator

    except FileNotFoundError as e:
        print(f"Error: {e} - Check if the file paths are correct.")
    except Exception as e:
        print(f"An error occurred while processing {cleaned_file}: {e}")
