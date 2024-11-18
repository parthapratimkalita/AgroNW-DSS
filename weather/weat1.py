#import necessary libraries
import pandas as pd
from wetterdienst.provider.dwd.mosmix import DwdMosmixRequest, DwdMosmixType
from wetterdienst import Settings
from geopy.geocoders import Nominatim
import time

def get_coordinates(postal_code):
    geolocator = Nominatim(user_agent="MyApp/1.0")
    location = geolocator.geocode(postal_code + ", Germany")
    return (location.latitude, location.longitude)

def station_example(area_code):

        settings = Settings(
                ts_shape=True,  # Return time series as a DataFrame
                ts_humanize=True,  # Use human-readable column names
                ts_si_units=False  # Use non-SI units for column names
        )
        # Define the data request using the DwdMosmixRequest class
        request = DwdMosmixRequest(
                parameter=["TTT", "RR1c","SunD1"],  # Request sunshine duration and temperature
                mosmix_type=DwdMosmixType.LARGE,  # Use large MOSMIX dataset
                settings=settings,
        )

        cor = get_coordinates(area_code)

        time.sleep(1)  # delay for 1 second to avoid geopy error
        filtered_stations = request.filter_by_distance(latlon=cor, distance=50, unit="km")
        response = next(filtered_stations.values.query())
        
        response.df.to_csv("test1.csv")

