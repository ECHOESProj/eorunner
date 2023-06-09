import dateutil.parser
from geoserver.catalog import Catalog
from numpy.lib.function_base import append
from app.init import get_env, get_path
from app.utils.db import delete_earth_observation, get_sites
from app.utils.eom_utils import has_serch_term_match
from app.utils.geo_server import get_catalog, get_granules, publish_timeseries_or_add_granule, get_granule_filenames
from .eom_processes import eom_processes 
import logging
from shapely import geometry, wkt
import requests

temp_path = get_env('Temp_Dir')
rest_url = get_env('GeoServer_RestUrl')
username = get_env('GeoServer_Username')
password = get_env('GeoServer_Password')
geoserver_workspace_name = get_env('GeoServer_Workspace')
geoserver_layer_name_prefix = get_env('GeoServer_Layer_Name_Prefix')

# Find granules/features which are eclipsed / overlapped by others
# If the features are the same size, add the older one to the overlapped set
def find_overlapped_features(features):  
    overlapped = set([])

    for feature in features:
        ingestion = feature['properties']['ingestion']
        #ingestion_date = dateutil.parser.isoparse(ingestion)
        for f in features:
            if (
                feature['id'] != f['id'] and 
                f['properties']['ingestion'] == ingestion and 
                feature['polygon'].within(f['polygon'])# and
                # (
                #     #ingestion < f['properties']['ingestion']
                #     #ingestion_date < datetime.strptime(f['properties']['ingestion'], '%Y-%m-%d').date()
                #     feature['polygon'].area < f['polygon'].area or
                #     feature['id'] < f['id']
                # )
            ):
                # If one overlaps the other, delete the older one (size was resized smaller)                
                if int(feature['id'].split(".")[1]) > int(f['id'].split(".")[1]) :
                    overlapped.add(f['id'])
                else:
                    overlapped.add(feature['id'])

    return overlapped

# Find granules / features which are not contained within a site / roi
def find_redundant_features(features, sites):
    redundant = set([])
    site_polygons = list(map(lambda site: wkt.loads(site['Polygon']), sites))

    for feature in features:
        match = list(filter(lambda site: site.contains(feature['polygon'].buffer(-1.0e-9)), site_polygons))
        if len(match) == 0:
            redundant.add(feature['id'])

    return redundant

# Remove excess granules
def eom_cleanup(process_filter = None):
    catalog = get_catalog()
    logging.info('eom_cleanup')
    logging.info('Getting sites')
    try:
        sites = get_sites()
    except Exception:
        logging.exception('Error getting sites')
        return
    
    if process_filter == None or len(process_filter) == 0:
        # no filter means use all processes
        processes = eom_processes
    else:
        # otherwise select the processes to run
        processes = list(filter(lambda x: has_serch_term_match(process_filter, x['name']), eom_processes))
        logging.info('Filtered process names:')
        logging.info(', '.join(list(map(lambda p: p['name'], processes))))

    for process in processes:
        layer_name = geoserver_layer_name_prefix + '_' + process['name'] + '_' + process['frequency']
        logging.info(f'Get {geoserver_workspace_name}:{layer_name} granules')
        granules = get_granules(geoserver_workspace_name, layer_name, layer_name)

        if granules == None:
            logging.info(f'No excess granules to remove')
            continue

        # For all existing granules in GeoServer, convert the geometries of each to Polygons for later comparison
        features = granules['features']
        for feature in granules['features']:
            #print(feature['id'] + ':' + feature['properties']['location'])
            p = geometry.Polygon(feature['geometry']['coordinates'][0][0])
            feature['polygon'] = p

        overlapped_ids = find_overlapped_features(features)
        redundant_ids = find_redundant_features(features, sites)

        ids_to_remove = overlapped_ids | redundant_ids

        if len(ids_to_remove):
            for id in ids_to_remove:
                try:
                    logging.info(f'Deleting granule {id}')
                    catalog.delete_granule(layer_name, layer_name, id, geoserver_workspace_name)
                    feature = list(filter(lambda x: x['id'] == id, features))[0]
                    #delete_earth_observation(feature["properties"]["location"])
                    url = f'{rest_url}/resource/data/{geoserver_workspace_name}/{layer_name}/{feature["properties"]["location"]}'
                    requests.delete(
                        url,
                        auth=(username, password)
                    )
                except Exception:
                    logging.exception('Error removing granule from GeoServer or Database')
        else:
            logging.info(f'No excess granules to remove')
