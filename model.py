import pickle
import warnings
from datetime import datetime
from config import source_map, dest_map, airline_map

# Suppress sklearn feature name warning
warnings.filterwarnings("ignore", message="X does not have valid feature names")

# Load trained pipeline
model = pickle.load(open("pipe.pkl", "rb"))

def predict_fare(form):
    """
    Takes form data (dict) and returns predicted fare.
    """
    try:
        # Departure
        dep_date = form["dep_date"]
        dep_time = form["dep_time"]
        dep_datetime = datetime.strptime(dep_date + " " + dep_time, "%Y-%m-%d %H:%M")
        journey_day = dep_datetime.day
        journey_month = dep_datetime.month
        dep_hour = dep_datetime.hour
        dep_min = dep_datetime.minute

        # Arrival
        arr_date = form["arr_date"]
        arr_time = form["arr_time"]
        arr_datetime = datetime.strptime(arr_date + " " + arr_time, "%Y-%m-%d %H:%M")
        arr_hour = arr_datetime.hour
        arr_min = arr_datetime.minute

        # Duration
        duration = arr_datetime - dep_datetime
        dur_hours = duration.seconds // 3600
        dur_mins = (duration.seconds % 3600) // 60

        # Source
        source_inp = source_map[form["source"]]

        # Destination
        dest_inp = dest_map[form["destination"]]

        # Airline
        air_inp = airline_map[form["airline"]]

        # Stops
        stops = int(form["stops"])

        # Features for model
        features = [[air_inp, source_inp, dest_inp, stops,
                     journey_month, journey_day, dep_hour, dep_min,
                     arr_hour, arr_min, dur_hours, dur_mins]]

        # Predict
        return float(model.predict(features)[0])  # Ensure regular float
        
    except Exception as e:
        raise ValueError(f"Prediction error: {str(e)}")
