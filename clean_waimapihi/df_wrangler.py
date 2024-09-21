import pandas as pd
import re
import datetime
import random



def to_name(track, trap):
    return f"Trap {trap}, {track}" if trap.isnumeric() else f"{trap}, {track}"


class DFWrangler():
    def __init__(self, df, as_of_date=None):
        bands = [b for b in df["band"].unique() if re.fullmatch("[A-Z]{2}-[A-Z]{2}u?", str(b)) and "WM" in str(b)]
        self.df = df.loc[df["band"].isin(bands)]

    def last_seen(self, df):
        return (
        df
            .groupby("band")
            ["date"].max()
            .dt.strftime('%d-%m-%Y')
            .rename("last_seen")
        )
    
    def first_seen_date(self, df):
        return (
        df
            .groupby("band")
            ["date"].min()
        )
    
    def first_seen(self, df):
        return (
        self.first_seen_date(df)
            .dt.strftime('%d-%m-%Y')
            .rename("first_seen")
        )

    def is_missing(self, df, as_of_date):
        return (
        df
            .groupby("band")
            ["date"].max()
            .rename("last_seen")
            .sub(as_of_date)
            .abs()
            .dt.days
            .gt(31)
            .rename("is_missing")
        )
        
    def latest_sightings(self, df):
        return (
        df
            .groupby("band")
            ["date"]
            .nlargest(5)
            .index
            .get_level_values(1)
        )

    def lat_long(self,df):
        return (
        df
            .loc[self.latest_sightings(df)]
            .dropna(subset=["lat", "lng"])
            .groupby("band")
            [["lat", "lng"]]
            .mean()
        )
    
    def territory_name(self, df): 
        return (
        df
            .sort_values('date', ascending=False)
            .dropna(subset=["trap"])
            .groupby("band")
            .nth(0)
            .set_index("band")
            [["track", "trap"]]
            .apply(lambda row: to_name(*row), axis=1)
            .rename("territory_name")
        )
    
    def summary_data(self, as_of_date=None):
        as_of_date = datetime.datetime.today() if as_of_date is None else as_of_date
        df = self.df.loc[self.df["date"] <= as_of_date]
        latest = pd.concat([self.first_seen_date(df), 
                            self.last_seen(df), 
                            self.first_seen(df),
                            self.is_missing(df, as_of_date), 
                            self.territory_name(df), 
                            self.lat_long(df)], axis=1)
        return latest.sort_values("date").reset_index()