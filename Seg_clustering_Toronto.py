#!/usr/bin/env python
# coding: utf-8

# <h2> Segmenting and Clustering Neighbourhood in Toronto </h2>

# Using the Notebook to build the code to scrape the following Wikipedia page, https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M, in order to obtain the data 

# <h2> Solutions to Questions </h2>

# In[28]:


import sys
get_ipython().system('{sys.executable} -m pip install geocoder')
get_ipython().system('{sys.executable} -m pip install folium')

print('Packages installed.')


# In[31]:


pip install BeautifulSoup4


# In[32]:


import numpy as np # library to handle data in a vectorized manner
import pandas as pd # library for data analsysis
import geocoder # import geocoder
import requests 
from bs4 import BeautifulSoup 

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# <b> Organize the Data to Scrap page for more exploration </b>

# In[33]:


URL = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
r = requests.get(URL) 
  
soup = BeautifulSoup(r.content, 'html5lib') 
table = soup.find('div', attrs = {'id':'container'}) 

# print(soup.prettify()) 
print('Page Scrapped.')


# <b>Colleting Data</b>

# In[34]:


postalCodes = [];
boroughs= [];
neighborhoods = [];
columnNum = 1;
passVal = False

for row in soup.find_all('td'):
    for cell in row:
        if cell.string and cell.string[0].isalpha() and len(cell.string) > 2:
            passVal = False
            if columnNum == 1:
                if passVal == False and cell.string[1].isdigit():
                    postalCodes.append(cell.string);   
                    columnNum = 2
                else:
                    continue
            elif columnNum == 2 :
                if cell.string == 'Not assigned':
                    passVal = True
                    del postalCodes[-1]
                    columnNum = 1
                    continue
                else:
                    boroughs.append(cell.string);      
                    columnNum = 3
            elif columnNum == 3 :
                if cell.string == 'Not assigned\n':
                    neighborhoods.append(boroughs[-1])
                else:
                    neighborhoods.append(cell.string); 
                columnNum = 1
                
print('Data Collected.')


# <b> Define the Data Frame columns we shall use</b>

# In[35]:


# define the dataframe columns
column_names = ['PostalCode', 'Borough', 'Neighborhood'] 

# instantiate the dataframe
neighbors = pd.DataFrame(columns=column_names)

neighbors


# <b> Initilization of Variables  & Checking the shapes</b>

# In[ ]:





# In[39]:



lat_lng_coords = None

for data in range(0, len(postalCodes)-1):
    code = postalCodes[data]
    borough = boroughs[data]
    neighborhood_name = neighborhoods[data]
    
    g = geocoder.arcgis('{}, Toronto, Ontario'.format(code))
    lat_lng_coords = g.latlng

    neighbors = neighbors.append({ 'PostalCode': code,
                                   'Borough': borough,
                                   'Neighborhood': neighborhood_name,
                                   'Latitude': lat_lng_coords[0],
                                   'Longitude': lat_lng_coords[1]}, ignore_index=True)
    
neighbors


# In[40]:


neighbors.shape


# In[38]:


VERSION = '20180605' # Foursquare API version

neighborhood_name = neighbors.loc[0, 'Neighborhood'] # neighborhood name
neighborhood_latitude = neighbors.loc[0, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = neighbors.loc[0, 'Longitude'] # neighborhood longitude value

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))

radius = 500 # define radius
LIMIT = 100 # limit of number of venues returned by Foursquare API

# url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
#     CLIENT_ID, 
#     CLIENT_SECRET, 
#     VERSION, 
#     43.67635739999999, 
#     79.2930312, 
#     radius, 
#     LIMIT)

url = 'https://api.foursquare.com/v2/venues/explore?&client_id=NEV1SHCVX1CYKBXU0OO22DMSNMRBEFT2C00HM1LXCICNKHGM&client_secret=TNJTVRJDTVWYJ0LJSUPHV3LHKDPGQZADLWORB2FMULAEICBC&v=20180605&ll=43.67635739999999,-79.2930312&radius=500&limit=100'

results = requests.get(url).json()

results


# In[ ]:





# <b> Using iformation from Four Square </b>

# In[41]:



def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[42]:


from pandas.io.json import json_normalize

venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[74]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# In[47]:


def getNearbyVenues(names, latitudes, longitudes):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)

        # create the API request URL
#         url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
#             CLIENT_ID, 
#             CLIENT_SECRET, 
#             VERSION, 
#             lat, 
#             lng, 
#             radius, 
#             LIMIT)
        
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[46]:


toronto_venues = getNearbyVenues(names=neighborhoods,
                                 latitudes=neighbors['Latitude'],
                                 longitudes=neighbors['Longitude'])


# <b> What is the Size of the Data Frame output? </b>

# In[45]:


print(toronto_venues.shape)
toronto_venues.head()


# <b> Numbers of Venues returned for each Neighbourhood </b>

# In[78]:


toronto_venues.groupby('Neighborhood').count()


# <b> No of Unique Categories  that can be curated from all the returned venues</b>

# In[48]:



print('There are {} uniques categories.'.format(len(toronto_venues['Venue Category'].unique())))


# In[49]:


# one hot encoding
toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighborhood'] = toronto_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

toronto_onehot.head()


# In[81]:


# examine the new dataframe size.

toronto_onehot.shape


# <b> Group rows by neighborhood and by taking the mean of the frequency of occurrence of each category</b>

# In[50]:


toronto_grouped = toronto_onehot.groupby('Neighborhood').mean().reset_index()
toronto_grouped


# <b> What is the new size? </b>

# In[51]:


toronto_grouped.shape


# <b> Print each neighborhood along with the top 5 most common venues</b>

# In[52]:



num_top_venues = 5

for hood in toronto_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = toronto_grouped[toronto_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# <b> Sort Venues in Descending Order </b>

# In[53]:



def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# <b> Display the 10 top venues for each Neighbourhood </b>

# In[54]:


num_top_venues = 3

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = toronto_grouped['Neighborhood']

for ind in np.arange(toronto_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# <b> Use  k-means to cluster the neighborhood into 5 clusters</b>

# In[55]:


# set number of clusters
kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]


# In[56]:


# create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood.

# add clustering labels
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

toronto_merged = neighbors

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

toronto_merged.head() # check the last columns!


# <b>Lastly, we visualize the resulting clusters <b>

# In[57]:


# create map
map_clusters = folium.Map(location=[43.67635739999999, -79.2930312], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Neighborhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# <h2> Cluster 1  </h2>

# In[58]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 0, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# <h2> Cluster 2 </h2>

# In[59]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 1, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[ ]:




