
from datetime import datetime, timedelta
from wetterdienst import Parameter, Resolution
from geopy.geocoders import Nominatim
import time
from datetime import date

from wetterdienst.provider.dwd.observation import (
    DwdObservationDataset,
    DwdObservationPeriod,
    DwdObservationRequest,
    DwdObservationResolution,
)



def get_coordinates(postal_code):
    geolocator = Nominatim(user_agent="MyApp/1.0")
    location = geolocator.geocode(postal_code + ", Germany")
    return (location.latitude, location.longitude)


def station_example(area_code, given_date):
    """Retrieve stations_result of DWD that measure temperature."""
    given_date = datetime.strptime(given_date, "%d.%m.%Y")
    
    # Calculate the date 8 days before today
    four_days_ago = given_date - timedelta(days=4)
    day_after = given_date

    request = DwdObservationRequest(
            parameter=["TEMPERATURE_AIR_MEAN_200","PRECIPITATION_HEIGHT","SUNSHINE_DURATION"],
            resolution=Resolution.HOURLY,
            period=DwdObservationPeriod.RECENT,
            start_date=four_days_ago,
            end_date= day_after,
               
            )
    
    cor = get_coordinates(area_code)
    


    time.sleep(3)  # delay for 1 second to avoid geopy error

    request.filter_by_distance(latlon=cor, distance=50, unit="km")
    filtered_stations = request.filter_by_distance(latlon=cor, distance=50, unit="km")


    values = filtered_stations.values.all()
    values.df.fillna(0, inplace=True)
    values.df = values.df[values.df['quality'] != 0.0]
    values.df.to_csv("testu_v.csv")
    