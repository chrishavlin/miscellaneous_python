from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

def greatCirclePaths(start_point,end_point):
    # define start coordinates
    start_lon=start_point['lon']#-71.0589
    start_lat=start_point['lat']#42.3601
    end_lon=end_point['lon']#-122.4194
    end_lat=end_point['lat']#37.7749

    # get antipodes
    ant1lon=start_lon+180
    if ant1lon>360:
        ant1lon= ant1lon - 360
    ant1lat=-start_lat
    ant2lon=end_lon+180
    if ant2lon>360:
        ant2lon= ant2lon - 360
    ant2lat=-end_lat

    #
    paths={}
    paths['minor_arc']={'lon':[ start_lon, end_lon ],
                        'lat':[start_lat,end_lat], 'clr':'red','dash':None}
    paths['major_arc']={'lon':[ start_lon,ant2lon,ant1lon, end_lon ],
                        'lat':[start_lat,ant2lat,ant1lat,end_lat],'clr':'green','dash':None}
    paths['great_circle']={'lon':[ start_lon,ant2lon,ant1lon, end_lon,start_lon ],
                        'lat':[start_lat,ant2lat,ant1lat,end_lat,start_lat], 'clr':'blue',
                        'dash':'dash'}
    return paths

paths= greatCirclePaths({'lat':42.3601,'lon':-71.0589},
                        {'lat':37.7749,'lon':-122.4194})
                        
DataDict=list()
for path in ['minor_arc','major_arc']:
    DataDict.append(
        dict(
            type = 'scattergeo',
            lon = paths[path]['lon'],
            lat = paths[path]['lat'],
            name= path,
            mode = 'lines',
            line = dict(
                width = 2.5,
                color = paths[path]['clr'],
                dash=paths[path]['dash'],
            ),
            opacity = 1.0,
        )
    )

figdata={}
figdata['data']=DataDict

projs=['hammer','mercator','azimuthal equal area','orthographic']
projtype=projs[3]

figdata['layout'] = dict(
    title = 'Great Circle Segments',
    showlegend = True,
    geo = dict(
        scope='world',
        projection= dict(type=projtype,rotation = dict( lon = -100, lat = 40, roll = 0)),
        showland = True,
        showcountries=True,
        landcolor = 'rgb(243, 243, 243)',
        countrycolor = 'rgb(204, 204, 204)'
    ),
)

plot(figdata)
