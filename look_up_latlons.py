import pandas as pa
import sys, time, urllib2
import numpy as np
import matplotlib.pyplot as plt

def find_lat_lons(Counts,counts_csv_file,API_KEY,dt):
   """
      loops through a csv, pulls out city names and finds corresponding latitude/longitude
      uses OpenStreetMap API Nomatim via MapQuest. 

      find_lat_lons(counts_csv_file,API_KEY)
        counts_csv_file = string, file name of csv database
        API_KEY = string, the api key for MapQuest
        dt = float, time between api calls
   """

   
   osm='http://open.mapquestapi.com/nominatim/v1/search.php?key='+API_KEY+'&format=xml&q='

   # loop  over cities in crowd counts, find Lat/Lon
   Lon=np.zeros(len(Counts))
   Lat=np.zeros(len(Counts))

   NewCounts=Counts.copy()
   NewCounts['lon']=Lon
   NewCounts['lat']=Lat
   for index, row in Counts.iterrows():

        srch=osm+str(row['City']).replace(' ','+')

        print '\n\nLooking up lat/lon for',row['City'],index
        time.sleep(dt) 
        response = urllib2.urlopen(srch)
        the_page = response.read().split()
         
        for iel in range(0,len(the_page)):
            if 'lon=' in the_page[iel] and NewCounts['lon'][index]==0.0:
                NewCounts['lon'][index]=float(the_page[iel].split("'")[1])
            if 'lat=' in the_page[iel] and NewCounts['lat'][index]==0.0:
                NewCounts['lat'][index]=float(the_page[iel].split("'")[1])

        print row['City'],NewCounts['lon'][index],NewCounts['lat'][index]

   return NewCounts

def fill_in_missing(CrowdCounts):
   """
      some of the initial city names had errors, manually edited those then 
      re-ran with this function to only re-process those points with missing
      lat/lon points
   """
   Missing=CrowdCounts[CrowdCounts['lon']==0]
   NewCounts=find_lat_lons(Missing.copy(),csv_file,str(sys.argv[1]),1)
   for index, row in NewCounts.iterrows():
       CrowdCounts['lat'][index]=NewCounts['lat'][index]
       CrowdCounts['lon'][index]=NewCounts['lon'][index]

if __name__=='__main__':
   
   # read in the data frames
   csv_file='./data/crowd_counts_jan_24_noon_usonly.csv'
   CrowdCounts=pa.read_csv(csv_file)

   # geocode time!
   find_lat_lons(CrowdCounts,csv_file,str(sys.argv[1]),1)
   
   # write it out
   CrowdCounts.to_csv(csv_file.replace('.csv','_geocoded.csv'),index=False)



