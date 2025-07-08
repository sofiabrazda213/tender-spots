import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the dataset — update the file name if needed
df = pd.read_csv("Registered_Business_Locations_-_San_Francisco_20250707.csv")
print(df.columns)

# Drop rows with missing locations or inactive businesses
df = df[df['Location Id'].notnull()]
df = df[df['Business End Date'].isnull()]

# Extract lat/lon from the Location column
df[['Longitude', 'Latitude']] = df['Location Id'].str.extract(r"\(([^,]+), ([^)]+)\)").astype(float)

# Filter to relevant businesses
categories = ['COFFEE', 'CAFE', 'TEA', 'SALON', 'RESTAURANT', 'MATCHA', 'BAR', 'SEX']
df = df[df['NAICS Code Description'].str.contains('|'.join(categories), case=False, na=False)]

# Tag simplified categories
def tag_category(desc):
    desc = desc.lower()
    if 'matcha' in desc or 'tea' in desc or 'coffee' in desc or 'cafe' in desc:
        return 'tea/coffee'
    elif 'salon' in desc:
        return 'salon'
    elif 'bar' in desc:
        return 'bar'
    elif 'sex' in desc:
        return 'sex shop'
    elif 'restaurant' in desc:
        return 'restaurant'
    else:
        return 'other'

df['category'] = df['NAICS Code Description'].apply(tag_category)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df['Longitude'], df['Latitude'])],
    crs="EPSG:4326"
)

# Export to GeoJSON for your interactive map
gdf[['DBA Name', 'Street Address', 'category', 'geometry']].to_file("cleaned_sf_businesses.geojson", driver="GeoJSON")

print("✅ Cleaned data exported to cleaned_sf_businesses.geojson")