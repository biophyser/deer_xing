from shapely.geometry import Point, LineString
import numpy as np


def split_line(line, max_line_units):
    """Split a shapely line into segments no longer that max_line units.
    
    Returns
    -------
    list of shapely line segments
    """
    
    # End early if the line is short enough
    if line.length <= max_line_units:
        return [line]

    # If line too long
    half_length = line.length / 2
    coords = list(line.coords)
    for idx, point in enumerate(coords):
        proj_dist = line.project(Point(point))
        if proj_dist == half_length:
            return [LineString(coords[:idx + 1]), LineString(coords[idx:])]

        if proj_dist > half_length:
            mid_point = line.interpolate(half_length)
            head_line = LineString(coords[:idx] + [(mid_point.x, mid_point.y)])
            tail_line = LineString([(mid_point.x, mid_point.y)] + coords[idx:])
            return split_line(head_line, max_line_units) + split_line(tail_line, max_line_units)
        
        
def process_coord_string(line_segment):
    """
    Take a coord string originally saved as a shapely line and spit out long/lat floats
    """
    path_points = list()
    #for i in df_traffic.loc[0, 'line'][12:-1].split(','):
    for i in line_segment[12:-1].split(','):
        lat, lon = [float(coord) for coord in i.strip().split(' ')]
        path_points.append(tuple([lat, lon]))
    return path_points


def process_lines(df):
    """Process placemark data from a KML file"""
    line_list, mid_list = list(), list()
    for index, row in df.iterrows():
        try:
            line = LineString(row['lat_lon_list'])
            line_list.append(line)
            mid_list.append(line.interpolate(0.5, normalized = True))
        except:
            print('no', end=' ')
            line_list = np.nan
            mid_list = np.nan
    df['line'] = line_list
    df['mid_point'] = mid_list
    
    
def make_feature_dict(df, features, prefix=None):
    """
    
    Parameters
    ----------
    df : geopandas.geodataframe.GeoDataFrame
        Dataframe containing features pulled from overpass API
        
    features : list
        List of column names associated with high-level feature names
        employed by overpass/OSM. Reference here:
        https://wiki.openstreetmap.org/wiki/Map_Features
        
    prefix : str
        Additional identifier placed before feature name.
        
    Returns
    -------
    dict
        Nested dictionary of features with value counts as eventual values.
        
    """
    
    if prefix!=None:
        pass
    else:
        prefix=''
        
    feature_dict = {}
    for feature in features:
        if feature in df.columns:
            series = df[feature].value_counts()
            feature_dict[prefix+feature] = { k:v for (k,v) in zip(series.index, series.values)}
        else:
            feature_dict[prefix+feature] = None
    return feature_dict