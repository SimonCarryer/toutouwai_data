import json
import pandas as pd
import re
from collections import Counter


def clean_text(name):
    return name.lower().strip()


def clean_trap(n):
    if "lone pine" in n.lower():
        return "62"
    n = str(n).lstrip("0").strip()
    if re.match("[0-9]{3}[-/][0-9]{1,3}", n):
        n = re.split("[-/]", n)[0]
    elif re.search("[0-9]{3}", n):
        n = re.search("[0-9]{3}", n)[0]
    elif re.match("[0-9]{2}[-/][0-9]{1,2}", n):
        n = re.split("[-/]", n)[0]
    elif re.search("[0-9]{2}", n):
        n = re.search("[0-9]{2}", n)[0]

    return n



def clean_data(values):
    """takes data from the "get values" method in the 'read_sheets_data' module"""
    df = pd.DataFrame(values[3:], columns=values[0])
    df.columns = [clean_text(c) for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df["volunteer"] = df["volunteer"].apply(clean_text)
    df["trap"] = df["closest trap/tracking tunnel"].apply(clean_trap)
    df["band"] = df["band"].replace("U", None).replace("", None).combine_first(df["new bands"])
    return df


class LatLongifer:
    def __init__(self, traps_gps):
        self.traps_gps = traps_gps
        self.missing_coords = Counter()

    def lat_long(self, track, trap):
        try:
            coords = self.traps_gps[track][trap]
        except KeyError:
            coords = {"lat": None, "lng": None}
            self.missing_coords["|".join([track, trap])] += 1
        return coords


def add_coords(df):
    with open("data/trap_gps.json") as f:
        traps_gps = json.loads(f.read())
        longifer = LatLongifer(traps_gps)
    coords = pd.DataFrame(
        [longifer.lat_long(lat, lng) for lat, lng in df[["track", "trap"]].values]
    )
    print("Added coordinates. The following entries could not be located:")
    for k, v in longifer.missing_coords.items():
        print(k, ":", v)
    return pd.concat([df, coords], axis=1)
