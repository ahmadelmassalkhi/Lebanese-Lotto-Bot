import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import Dense, LSTM
from keras._tf_keras.keras.callbacks import EarlyStopping

########################################################################################################################

def read_data(year):
    file_path = f"./Prediction/{year}.txt"
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        parts = line.split(', ', 2)
        draw_number = int(parts[0])
        date = parts[1]
        numbers = list(map(int, parts[2].strip('[]\n').split(',')))
        data.append([draw_number, date, numbers])
    return pd.DataFrame(data, columns=["DrawNumber", "Date", "Numbers"])

# Load data from all years
years = range(2002, 2025)
data_frames = [read_data(year) for year in years]
data = pd.concat(data_frames, ignore_index=True)

# Split numbers into separate columns
numbers_df = data['Numbers'].apply(lambda x: pd.Series(x[:6]))  # Ensure there are exactly 6 elements
numbers_df.columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Num6']
data = data.drop(columns=['Numbers']).join(numbers_df)

# Convert Date to datetime
data['Date'] = pd.to_datetime(data['Date'])

# Calculate frequency of each number
number_frequency = data.iloc[:, 2:].apply(pd.Series.value_counts).fillna(0).sum(axis=1).sort_values(ascending=False)

########################################################################################################################
# apply a neural network, test its fitness, and predict next draw

# Prepare the data
def prepare_data(df):
    # Flatten the numbers columns into a single feature vector
    numbers = df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Num6']].values
    scaler = MinMaxScaler()
    numbers_scaled = scaler.fit_transform(numbers)

    # Create sequences of past draws
    X, y = [], []
    for i in range(len(numbers_scaled) - 1):
        X.append(numbers_scaled[i])
        y.append(numbers_scaled[i + 1])
    X = np.array(X)
    y = np.array(y)
    return X, y, scaler

X, y, scaler = prepare_data(data)

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build the model
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(6, activation='linear'))
model.compile(optimizer='adam', loss='mse')

# Train the model
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
model.fit(X_train, y_train, validation_split=0.2, epochs=100, batch_size=16, callbacks=[early_stopping])

# Save the model
model.save('lottery_model.h5')

# Evaluate the model
loss = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}")

# Predict the next draw
next_draw_scaled = model.predict(X_test[-1].reshape(1, -1))
next_draw = scaler.inverse_transform(next_draw_scaled)

next_draw = np.round(next_draw).astype(int)
print(f"Predicted Next Draw: {next_draw}")

'''
6 12 18 24 30 37
6 13 19 25 30 37
6 13 18 25 31 37
6 13 19 25 31 37
6 13 18 25 30 37
6 13 18 24 30 37
7 14 19 24 30 37
7 13 19 25 31 37
7 13 19 25 31 38
7 13 19 24 31 37
7 13 18 25 30 37
'''