"""List affiliations of authors in citation.cff and locate them.

- read citation.cff
- list affiliations
- locate longitude and latitude of each affiliation
- write to file
- plot on map
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import ruamel.yaml
from geopy.geocoders import Nominatim
from rich import print


def root_dir():
    return Path(__file__).parent.resolve()


def main():
    with open(root_dir() / "bids_spec_citation.cff") as f:
        cff = ruamel.yaml.load(f, Loader=ruamel.yaml.RoundTripLoader)

    affiliations = [author["affiliation"] for author in cff["authors"] if "affiliation" in author]

    if Path("affiliations.tsv").exists():
        df = pd.read_csv("affiliations.tsv", sep="\t")

    else:
        columns = ["address", "city", "country", "longitude", "latitude"]
        df = {
            "affiliation": sorted(list(set(affiliations))),
            "address": [],
            "city": [],
            "country": [],
            "longitude": [],
            "latitude": [],
        }

        geolocator = Nominatim(user_agent="my_request")
        for affiliation_ in df["affiliation"]:
            print(f"\nLocating: {affiliation_}")
            location = get_location(geolocator, affiliation_)
            if location is None:
                print(f" could not locate: {affiliation_}")
                for column in columns:
                    df[column].append("n/a")
                continue
            print(" address: ", location.address)
            df["city"].append(location.raw["address"].get("city"))
            df["country"].append(location.raw["address"].get("country"))
            df["address"].append(location.address)
            df["longitude"].append(location.longitude)
            df["latitude"].append(location.latitude)

        df = pd.DataFrame(df)
        df.to_csv("affiliations.tsv", index=False, sep="\t")

    print(f"Number of affiliations: {len(affiliations)}")
    nb_without_affiliation = sum("affiliation" not in author for author in cff["authors"])
    nb_countries = len(set(df["country"]))
    print(f"Number of countries: {nb_countries}")
    print(f"Number of authors without affiliation: {nb_without_affiliation}")
    unknown_affiliations = df["address"].isna().sum()
    print(f"Number of unknown affiliations: {unknown_affiliations}")

    planet_slider_fig = px.scatter_geo(
        df, lat=df.latitude, lon=df.longitude, hover_name="address", projection="natural earth"
    )
    planet_slider_fig.write_image("affiliations.png", width=800, height=400, scale=2)


def get_location(geolocator, affiliation):
    location = geolocator.geocode(
        affiliation, language="english", namedetails=True, addressdetails=True
    )
    if location is not None:
        return location

    if "," not in affiliation:
        return None

    # parse country
    country = affiliation.split(",")[-1].strip()

    # parse city and avoid zip code
    if len(affiliation.split(",")) >= 2:
        city = affiliation.split(",")[-2].strip()
    if city and len(affiliation.split(",")) >= 3 and (city.isupper() or re.match("[0-9]", city)):
        city = affiliation.split(",")[-3].strip()

    address = f"{city}, {country}" if country else f"{city}"
    if address:
        print(f" using: {address}")
        location = geolocator.geocode(
            city, language="english", namedetails=True, addressdetails=True
        )
        if location is not None:
            return location

    return None


if __name__ == "__main__":
    main()
