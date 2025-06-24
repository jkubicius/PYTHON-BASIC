import os
import json
from statistics import mean
from lxml import etree

source_dir = "parsing_serialization_task/source_data"
city_stats = []

for city in os.listdir(source_dir):
    city_dir = os.path.join(source_dir, city)
    for filename in os.listdir(city_dir):
        file_path = os.path.join(city_dir, filename)
        with open(file_path, "r") as f:
            data = json.load(f)

        hourly = data["hourly"]
        temps = [h["temp"] for h in hourly]
        winds = [h["wind_speed"] for h in hourly]

        stats = {
            "city": city,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "temp_mean": round(mean(temps), 2),
            "wind_min": min(winds),
            "wind_max": max(winds),
            "wind_mean": round(mean(winds), 2)
        }
        city_stats.append(stats)

# Mean for all cities in Spain
country_temp_mean = round(mean([c["temp_mean"] for c in city_stats]), 2)
country_wind_mean = round(mean([c["wind_mean"] for c in city_stats]), 2)

coldest_city = min(city_stats, key=lambda x: x["temp_mean"])["city"]
warmest_city = max(city_stats, key=lambda x: x["temp_mean"])["city"]
windiest_city = max(city_stats, key=lambda x: x["wind_mean"])["city"]

weather = etree.Element("weather", country="Spain", date="2021-09-25")
etree.SubElement(weather, "summary",
                 mean_temp=str(country_temp_mean),  # XML requires strings
                 mean_wind_speed=str(country_wind_mean),
                 coldest_place=coldest_city,
                 warmest_place=warmest_city,
                 windiest_place=windiest_city
                 )

cities = etree.SubElement(weather, "cities")
for city in city_stats:
    tag = city["city"].replace(" ", "_")  # XML tags can't contain spaces
    etree.SubElement(cities, tag,
                     mean_temp=str(city["temp_mean"]),
                     max_temp=str(city["temp_max"]),
                     min_temp=str(city["temp_min"]),
                     mean_wind_speed=str(city["wind_mean"]),
                     max_wind_speed=str(city["wind_max"]),
                     min_wind_speed=str(city["wind_min"])
                     )

xml_string = etree.tostring(weather, pretty_print=True, encoding="unicode")

with open("result.xml", "w", encoding="utf-8") as f:
    f.write(xml_string)
