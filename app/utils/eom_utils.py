from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from shapely import wkb
import re

def parse_dates(start_date: str, end_date: str, frequency: str):
    '''
    Parse date strings if they exist.
    If not, return start and end depending on frequency

    :param start_date: Start date string
    :param end_date: End date string
    '''
    if start_date is not None and end_date is not None:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        today = date.today()
        if frequency == 'daily':
            start = today - timedelta(days=10) # go 7 days back
            end = today           
        elif frequency == 'yearly':
            start = date(today.year - 1, 1, 1)
            end = date(today.year, 1, 1) - timedelta(days=1)
        else:
            month = datetime(today.year, today.month, 1)
            start = (month + relativedelta(months=-1)).date()
            end = month.date()
    
    return (start, end)

def parse_datesx(start_date: str, end_date: str):
    '''
    Parse date strings if they exist.
    If not, return start of this month and one month previous

    :param start_date: Start date string
    :param end_date: End date string
    '''
    if start_date is not None and end_date is not None:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        today = date.today()
        month = datetime(today.year, today.month, 1)
        start = (month + relativedelta(months=-1)).date()
        end = month.date()
    
    return (start, end)

def is_already_captured(site_polygon, existing_geoserver_features, start: date):
    # If the site polygon shares the same centroid and area for the current start date 
    # to one already in GeoServer, then this area has already been captured
    # Check centroid distance and area with 99% accuracy to account for decimal 
    # point accuracy of coordinates returned from GeoServer vs Postgres
    for feature in existing_geoserver_features:
        feature_polygon = feature['polygon']

        if (
            f'{start:%Y%m%d}' in feature['properties']['location'] and
            site_polygon.centroid.distance(feature_polygon.centroid) < 0.009 and
            (site_polygon.intersection(feature_polygon).area/site_polygon.area)*100 > 99
        ):
            return True

def is_empty_already_attempted(site_polygon, existing_db_features, start: date):
    # Check if empty response exists in the db set for this layer
    for row in existing_db_features:
        feature_polygon = wkb.loads(row['Polygon'], hex=True)
        
        if (
            f'{start:%Y%m%d}' == f'{row["Timestamp"]:%Y%m%d}' and
            site_polygon.centroid.distance(feature_polygon.centroid) < 0.009 and
            (site_polygon.intersection(feature_polygon).area/site_polygon.area)*100 > 99
        ):
            return True           

def has_serch_term_match(searh_terms, string):
    is_found = False
    for search_term in searh_terms:
        if re.search(search_term, string) != None:
            is_found = True
    return is_found