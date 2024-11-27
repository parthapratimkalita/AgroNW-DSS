import pandas as pd


# Convert the 'date' column to datetime objects
def convert_date(df):

    df['date'] = pd.to_datetime(df['date'])

    # Extract the date part
    df['date_only'] = df['date'].dt.date

    # Extract the time part
    df['time_only'] = df['date'].dt.time

    df.drop('date', axis=1, inplace=True)

    return df

def read_weather():

    df = pd.read_csv('weather/testu_v.csv')
    df1 = pd.read_csv('weather/test1.csv')
    df = convert_date(df)
    df1 = convert_date(df1)

    df1['parameter'] = df1['parameter'].apply(lambda x: 'precipitation_height' if x == 'precipitation_height_significant_weather_last_1h' else x)

    mean_df1 = df1.groupby([ 'date_only', 'parameter'])['value'].mean().reset_index()

    pivot_df1 = mean_df1.pivot(index=['date_only'], columns='parameter', values='value').reset_index()
    pivot_df1["temperature_air_mean_200"] = pivot_df1["temperature_air_mean_200"] - 273.15

    mean_df = df.groupby([ 'date_only', 'parameter'])['value'].mean().reset_index()

    pivot_df = mean_df.pivot(index=['date_only'], columns='parameter', values='value').reset_index()
    pivot_df["temperature_air_mean_200"] = pivot_df["temperature_air_mean_200"] - 273.15   

    combined_df = pd.concat([pivot_df, pivot_df1])
    combined_df.to_csv('input_weather_tm.csv')

    return combined_df
    




