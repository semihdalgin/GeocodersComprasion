import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import MarkerCluster

df = pd.read_csv('geocoded_add_clean.csv', delimiter=';')

Address = pd.DataFrame(data=df, index=range(len(df)), columns= ['lon','lat'])
Error=pd.DataFrame(data=df, index=range(len(df)), columns=['gerror','qerror','herror'])

pd.options.display.float_format = "{:.4f}".format
pd.set_option('display.max_columns', None)
#print(df.describe(include = 'all'))
df.describe().to_csv('stats.csv')
Latmean=np.mean(df['lat'])
Lngmean=np.mean(df['lon'])
print(df[df['Google Distance']==df['Google Distance'].max()])
length=len(Error)

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10,8))
sns.histplot(data=Error, x='gerror', color='blue', ax=axes[0])
axes[0].set_xlabel("Google Error")
axes[0].set_title("Google")
sns.histplot(data=Error, x='qerror', color='red', ax=axes[1])
axes[1].set_xlabel("Qgis Error")
axes[1].set_title("Qgis")
sns.histplot(data=Error, x='herror', color='magenta', ax=axes[2])
axes[2].set_xlabel("Here Error")
axes[2].set_title("Here")

plt.show()

#fig2, axes = plt.subplots(nrows=1, ncols=3, figsize=(10,8))
f = plt.figure(2)
sns.boxplot(data=Error, x='gerror', color='blue')
plt.xlabel("Google Error")
plt.title("Google")
plt.show()

f = plt.figure(3)
sns.boxplot(data=Error, x='qerror', color='red')
plt.xlabel("Qgis Error")
plt.title("Qgis")
plt.show()

f = plt.figure(4)
sns.boxplot(data=Error, x='herror', color='magenta')
plt.xlabel("Here Error")
plt.title("Here")
plt.show()

map_center = [Latmean, Lngmean]  # Provide the latitude and longitude of the center point
map_zoom = 5  # Adjust the zoom level as needed
map_obj = folium.Map(location=map_center, zoom_start=map_zoom)



for index, row in df.iterrows():
    loc=(df['lat'][index],df['lon'][index])
    locg=(df['Google Latitude'][index],df['Google Longitude'][index])
    locq =(df['Qgis Lat'][index], df['Qgis Lng'][index])
    loch =(df['Here Lat'][index], df['Here Lng'][index])

    marker  = folium.Marker(location=loc, icon=folium.Icon(color='blue'))
    marker1 = folium.Marker(location=locg, icon=folium.Icon(color='red'))
    marker2 = folium.Marker(location=locq, icon=folium.Icon(color='black'))
    marker3 = folium.Marker(location=loch, icon=folium.Icon(color='orange'))
    map_obj.add_child(marker)
    map_obj.add_child(marker1)
    map_obj.add_child(marker2)
    map_obj.add_child(marker3)

# Add a legend to the map
legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 150px; height: 150px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white;
                ">
        <div style="text-align: left;">
            <i> </i> Legend <br>
            <i class ="fa fa-map-marker fa-2x" style="color:blue"> </i> True Location <br>
            <i class ="fa fa-map-marker fa-2x" style="color:red"> </i> Google <br>
            <i class ="fa fa-map-marker fa-2x" style="color:black"> </i> Qgis <br>
            <i class ="fa fa-map-marker fa-2x" style="color:orange"></i> Here
        </div>
    </div>
'''


map_obj.get_root().html.add_child(folium.Element(legend_html))

map_obj.save("map.html")