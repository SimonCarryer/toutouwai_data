from clean_waimapihi.read_sheets_data import get_latest_data
from clean_waimapihi.clean_sightings import clean_data, add_coords
from clean_waimapihi.df_wrangler import DFWrangler


values = get_latest_data()

df = clean_data(values)
df = add_coords(df)

df.to_csv("data/waimapihi_observation_data.csv", index=False)