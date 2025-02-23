import os
import pytz
import pyowm
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# API key
owm = pyowm.OWM('17c7cbcd02672ee31ac30fbf5d66f014')
mgr = owm.weather_manager()

# Frontend
st.title("Weather Forecast for 5 Days! 🌦")
st.write("### Enter a city, select the temperature unit and graph type from the sidebar.")

# Input city name
place = st.text_input("NAME OF THE CITY:", "")

if not place:
    st.write("Please enter a city name!")

# Selection forms
Temp_Unit = st.selectbox("Select Temperature Unit", ("Celsius", "Fahrenheit"))
Graph_type = st.selectbox("Select Graph Type", ("Line Graph", "Bar Graph"))

# Submit button
if st.button("Submit") and place:
    try:
        # Fetch the 5-day forecast (3-hour interval)
        forecast = mgr.forecast_at_place(place, '3h').forecast

        # Extract data
        dates_dict = {}

        for weather in forecast:
            timestamp = weather.reference_time()
            dt_object = datetime.utcfromtimestamp(timestamp).date()  # Keep only date

            temp_kelvin = weather.temperature('kelvin')
            temp_min = temp_kelvin.get("temp_min", None)
            temp_max = temp_kelvin.get("temp_max", None)

            if temp_min is None or temp_max is None:
                continue  # Skip if temperature data is missing

            # Convert temperature
            if Temp_Unit == "Celsius":
                temp_min = round(temp_min - 273.15, 1)
                temp_max = round(temp_max - 273.15, 1)
            else:
                temp_min = round((temp_min - 273.15) * 9/5 + 32, 1)
                temp_max = round((temp_max - 273.15) * 9/5 + 32, 1)

            # Initialize the date dictionary entry if it doesn't exist
            if dt_object not in dates_dict:
                dates_dict[dt_object] = {"min": float("inf"), "max": float("-inf")}

            # Update min/max temperatures for the date
            dates_dict[dt_object]["min"] = min(dates_dict[dt_object]["min"], temp_min)
            dates_dict[dt_object]["max"] = max(dates_dict[dt_object]["max"], temp_max)

        # Ensure data is available
        if not dates_dict:
            st.write("No temperature data available for this city. Try another one!")
            st.stop()

        # Prepare final data
        dates_list = list(dates_dict.keys())
        temp_min_list = [dates_dict[d]["min"] for d in dates_list]
        temp_max_list = [dates_dict[d]["max"] for d in dates_list]

        # Generate numeric positions for the x-axis
        x = np.arange(len(dates_list))  

        # Plot the data
        fig, ax = plt.subplots(figsize=(6, 4))

        if Graph_type == "Line Graph":
            ax.plot(x, temp_min_list, marker="o", linestyle="-", color="darkblue", label="Min Temp")
            ax.plot(x, temp_max_list, marker="o", linestyle="-", color="orange", label="Max Temp")

        else:  # Bar Graph
            width = 0.35  # Adjusted width for spacing

            ax.bar(x - width/2, temp_min_list, width, color="darkblue", label="Min Temp")
            ax.bar(x + width/2, temp_max_list, width, color="orange", label="Max Temp")
        
            # Add temperature labels on top of bars (slightly higher)
            for i in range(len(dates_list)):
                ax.text(i - width/2, temp_min_list[i] + 1, f"{temp_min_list[i]}°", 
                ha='center', color="white", fontsize=10, fontweight="bold")
        
                ax.text(i + width/2, temp_max_list[i] + 1, f"{temp_max_list[i]}°", 
                ha='center', color="black", fontsize=10, fontweight="bold")

        # Formatting
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime("%m/%d") for d in dates_list], rotation=0, fontsize=10)
        plt.xlabel("Date", fontsize=8)
        plt.ylabel(f"Temperature ({Temp_Unit})", fontsize=8)
        plt.title(f"Temperature Forecast for {place}", fontsize=12, pad=20)
        plt.legend(loc='upper left', bbox_to_anchor=(1,1))
        plt.grid(False)  # No grid to match your SS

        # Show the plot in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.write("Error fetching weather data. Please check the city name and try again!")
        st.write(f"Error details: {e}")


    # getting the current weather data
    current_weather = mgr.weather_at_place(place).weather

    # additional weather updates 
    st.subheader("Additional Weather Details :D")

    #checking for certain weather conditions
    forecaster = mgr.forecast_at_place(place, '3h')
    weather_conditions = {
        "Rain": forecaster.will_have_rain(),
        "Clear_skies": forecaster.will_have_clear(),
        "Fog": forecaster.will_have_fog(),
        "Clouds": forecaster.will_have_clouds(),
        "Snow": forecaster.will_have_snow(),
        "Storm": forecaster.will_have_storm(),
        "Tornado": forecaster.will_have_tornado(),
        "Hurricane": forecaster.will_have_hurricane()
    }    


    #display upcoming weather conditions
    st.write("### Impending Weather Changes:")
    for condition, will_happen in weather_conditions.items():
        if will_happen:
            st.write(f" ✅ {condition} expected in the next 5 days.")
        else:
            st.write(f"❌ No {condition} expected in the next 5 days.")



    #cloud coverage, wind speed, and humidity
    cloud_coverage = current_weather.clouds
    wind_speed = current_weather.wind()["speed"]
    humidity = current_weather.humidity


    st.write(f"☁ **Cloud Coverage:** {cloud_coverage}%")
    st.write(f"💨 **Wind Speed:** {wind_speed} m/s")
    st.write(f"💧 **Humidity:** {humidity}%")

    #sunrise and sunset times
    sunrise_time = datetime.utcfromtimestamp(current_weather.sunrise_time()).strftime('%Y-%m-%d %H:%M:%S GMT')
    sunset_time = datetime.utcfromtimestamp(current_weather.sunset_time()).strftime('%Y-%m-%d %H:%M:%S GMT')

    st.write(f"🌅 **Sunrise Time:** {sunrise_time}")
    st.write(f"🌇 **Sunset Time:** {sunset_time}")




 










