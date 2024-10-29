import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


books = pd.read_csv("./temp/cleaned_books.csv")
checkouts = pd.read_csv("./temp/cleaned_checkouts.csv")
customers = pd.read_csv("./temp/cleaned_customers.csv")
libraries = pd.read_csv("./temp/cleaned_libraries.csv")

# join tables - same as for data analysis
df = checkouts \
    .merge(books, left_on="book_id", right_on="id", how="left", suffixes=('', '_book')) \
    .merge(customers, left_on="patron_id", right_on="id", how="left", suffixes=('', '_patron')) \
    .merge(libraries, left_on="library_id", right_on="id", how="left", suffixes=('', '_library'))

numerical_features = ['publishedDate', 'price', 'pages', 'birth_date']
categorical_features = [
    'book_id', 'title', 'authors', 'publisher', 'categories', 'customer_name',
    'street_address', 'customer_city', 'state', 'zipcode', 'gender',
    'education', 'occupation', 'id_library', 'library_name',
    'street_address_library', 'city', 'region', 'postal_code'
]

# adjust dataset to desired format used by TF
# numerical pipeline
numerical_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

# categorical pipeline
categorical_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# combine preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_pipeline, numerical_features),
        ('cat', categorical_pipeline, categorical_features)
    ]
)


# features (x = input) and target (y)
X = df[['book_id', 'title', 'authors', 'publisher', 'publishedDate', 'categories', 'price', 'pages', 'customer_name',
        'street_address', 'customer_city', 'state', 'zipcode', 'birth_date', 'gender', 'education', 'occupation',
        'id_library', 'library_name', 'street_address_library', 'city', 'region', 'postal_code']]
y = df['days_until_returned']

# split data into training and testing sets - define percentage for test size
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# adjust data type from float (TF expects int or str) - decided to use str
cols = ['publishedDate', 'price', 'zipcode', 'birth_date', 'postal_code']
X_train[cols] = X_train[cols].astype('str')
# X_train[cols] = X_train[cols].astype('Int64')

# data transformation
# fit the preprocessor to the training data and transform
X_train_prepared = preprocessor.fit_transform(X_train)
X_test_prepared = preprocessor.transform(X_test)

# convert sparse matrix to a dense format - expected array
X_train_dense = X_train_prepared.toarray() if hasattr(X_train_prepared, 'toarray') else X_train_prepared
X_test_dense = X_test_prepared.toarray() if hasattr(X_test_prepared, 'toarray') else X_test_prepared

# convert to TF datasets
train_dataset = tf.data.Dataset.from_tensor_slices((X_train_dense, y_train.values))
test_dataset = tf.data.Dataset.from_tensor_slices((X_test_dense, y_test.values))

# batch the data for training
train_dataset = train_dataset.batch(32)
test_dataset = test_dataset.batch(32)

# ----
# create a sequential model
model = Sequential()
model.add(Dense(64, activation='relu', input_shape=(X_train_prepared.shape[1],)))
model.add(Dense(32, activation='relu'))
model.add(Dense(1))  # output layer for regression - one output

# compile the model
model.compile(optimizer='adam', loss='mean_squared_error')


# train the model !!! tested with 50 epoch, still high loss (volume of data?) > higher number of iterations (epoch)
history = model.fit(train_dataset, epochs=100, validation_data=test_dataset)

# INPUT: example input data for a new book rental record
new_data = {
    'book_id': ['ZjZOAAAAMAAJ'],
    'title': ['Library of Advertising'],
    'authors': ['Axel Petrus Johnson'],
    'publisher': None,
    'publishedDate': [1911.0],
    'categories': ['Advertising'],
    'price': [35.99],
    'pages': [428],
    'customer_name': ['Milana Miletic'],
    'street_address': ['1000 NE Multnomah St'],
    'customer_city': ['Portland'],
    'state': ['Oregon'],
    'zipcode': ['97232'],
    'birth_date': [1988.0],
    'gender': ['female'],
    'education': ['High School'],
    'occupation': ['Tech'],
    'id_library': ['222-222@5xc-kkw-bzf'],
    'library_name': ['MULTNOMAH County Library MIDLAND'],
    'street_address_library': ['805 SE 122nd Ave'],
    'city': ['Portland'],
    'region': ['OR'],
    'postal_code': ['97233']
}

# convert the new sample into a DataFrame
new_data_df = pd.DataFrame(new_data)

# preprocess the new data
new_data_prepared = preprocessor.transform(new_data_df)

# make the prediction using the trained model
predicted_days = model.predict(new_data_prepared)

# output the prediction !!!
print(f"Predicted days until return: {predicted_days[0][0]:.2f}")