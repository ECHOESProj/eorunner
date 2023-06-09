from app.init import get_env
from app.utils.eom_utils import has_serch_term_match, is_already_captured, is_empty_already_attempted, parse_dates
from app.utils.geo_server import get_granules, publish_timeseries_or_add_granule
from app.utils.db import get_empty_earth_observations, get_empty_earth_observations_by_instrument, get_sites, insert_earth_observation
from ctypes import Array
import json
from datetime import datetime, date, timedelta
from websocket import create_connection
import logging
from app.utils.s3 import s3_bucket
from .eom_processes import eom_processes 
import pandas as pd
from shapely import wkt, geometry
from app.utils.interval_names import interval_names

temp_path = get_env('Temp_Dir')
geoserver_workspace_name = get_env('GeoServer_Workspace')
geoserver_layer_name_prefix = get_env('GeoServer_Layer_Name_Prefix')
websockets_url = get_env('WebSockets_Url')
websockets_api_key = get_env('WebSockets_Api_Key')
polygons_too_big = {}

def eom_process_runner(process, sites: Array, start: date, end: date, backdate = False):
    #sites = sites[0:1]
    layer_name = geoserver_layer_name_prefix + '_' + process['name'] + '_' + process['frequency']
    logging.info(f'Getting granules for {geoserver_workspace_name}:{layer_name}')
    granules = get_granules(geoserver_workspace_name, layer_name, layer_name)
    #empty_earth_observation_results = get_empty_earth_observations(layer_name)

    if granules == None:
        granules = {'features': []}

    # For all existing granules in GeoServer, convert the geometries of each to Polygons for later comparison
    for feature in granules['features']:
        p = geometry.Polygon(feature['geometry']['coordinates'][0][0])
        feature['polygon'] = p

    for instrument in process['instruments']:
        empty_earth_observation_results = get_empty_earth_observations_by_instrument(instrument['args']['instrument'], process['frequency'])        

        start_date = start
        end_date = end
        # if backdate is true, determine start and end from start and end defined in instrument config
        if backdate:
            logging.info('Backdate option enabled, getting start and end dates from config')
            start_date = instrument['start']
            if instrument['end'] is not None:
                end_date = instrument['end']
            else:
                if process['frequency'] == 'daily':
                     # For daily frequency use yesterday as the end date
                    end_date = date.today() - timedelta(days=1)
                else:
                    # For monthly or yearly, last day of previous month
                    end_date = date.today().replace(day=1) - timedelta(days=1)
        else:
            # backdate is false. check if supplied start and end dates are within the range of the source data
            if start_date < instrument['start']:
                start_date = instrument['start']
                logging.info(f'Supplied start date is less than instrument: {instrument["name"]} supports. New start date is {start_date}')
            if instrument['end'] is not None and end_date > instrument['end']:
                end_date = instrument['end']
                logging.info(f'Supplied end date is greater than instrument: {instrument["name"]} supports. New end date is {end_date}')

        # protect against running days in the future
        if end_date > date.today():
            end_date = date.today()

        # create an array of months in the date range
        # intervals will be an empty array if the date range is invalid           
        logging.info(f'Start date {start_date}, End date: {end_date}')
        if start_date > end_date:
            logging.info(f'Date range invalid, skipping to next instrument')
            continue

        intervals = pd.interval_range(start=pd.Timestamp(start_date - timedelta(days=1)), end=pd.Timestamp(end_date), freq=interval_names[process['frequency']])
        intervals = [(pd.to_datetime(i.left + pd.DateOffset(days=1)).date(), pd.to_datetime(i.right).date())
                    for i in intervals]
        
        # reverse dates so that newest dates get processes first
        intervals = intervals[::-1]

        # loop throught dates first so that each site will get populated equally
        for start, end in intervals:
            for site in sites:
                polygon = str(site['Polygon'])
                site_polygon = wkt.loads(polygon)
                granule_filename = f'{start:%Y%m%d}_{polygon}_{instrument["name"]}.tif'
                # check if the granule already exists, if it does, skip to next
                if is_already_captured(site_polygon, granules['features'], start):
                    logging.info(f'Granule {granule_filename} already exists, skipping to next')
                    continue

                if is_empty_already_attempted(site_polygon, empty_earth_observation_results, start):
                    logging.info(f'{instrument["args"]["instrument"]} at start date {start:%Y-%m-%d} was previously empty at this location, skipping to next')
                    continue

                # check if this polygon has previously returned a size error
                if polygon in polygons_too_big:
                    logging.info(f'{polygon} was previously too big, skipping to next')
                    continue
                
                frequency='''{"--frequency":"''' + f'''{process['frequency']}''' + '''"}'''
                json_str = f'''{{
                    "image": "eo-custom-scripts",
                    "instrument": "{instrument['args']['instrument']}",
                    "processing_module": "{instrument['args']['processing_module']}",
                    "polygon": "{polygon}",
                    "start": "{start:%Y-%m-%d}",
                    "end": "{end:%Y-%m-%d}",
                    "optional": {frequency}
                }}'''

                logging.info(f'Creating websockets connection to {websockets_url}')
                try:
                    ws = create_connection(f'{websockets_url}?token={websockets_api_key}')
                    logging.info(f'Sending JSON: {json_str}')
                    ws.send(json_str)
                    result = json.loads(ws.recv())
                    logging.info(f'Recieved response: {result}')
                    ws.close()

                    # assuming COMMON_BAD_PAYLOAD is requested area is too big
                    if 'stderr' in result and 'COMMON_BAD_PAYLOAD' in result['stderr']:
                        polygons_too_big[polygon] = True

                    if 'output' in result:
                        yield {
                            'output': result['output'],
                            'layer_name': layer_name,
                            'granule_filename': granule_filename,
                            'polygon': polygon,
                            'instrument': instrument['args']['instrument'],
                            'processing_module': instrument['args']['processing_module'],
                            'start': f'{start:%Y-%m-%d}',
                            'end': f'{end:%Y-%m-%d}'
                        }
                    else:
                        raise ValueError('Output key not in result object, see above for error in remote container')

                except Exception as e:       
                    logging.exception('\n'.join(list(map(str, e.args))))
                    yield {}

def eom(start_date = None, end_date = None, backdate = False, process_filter = None):
    '''
    Run eo-mosaics for each site and each process for a series of dates

    :param start_date: Start date string
    :param end_date: End date string
    :param backdate: Start/End date will be ignored and dates taken from process config
    '''
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
        start, end = parse_dates(start_date, end_date, process['frequency'])

        for result in eom_process_runner(process, sites, start, end, backdate):

            if 'output' not in result:
                logging.error('Error in previous run, skipping to next')
                continue

            output = result['output']
            if len(output):                   
                filename = result['granule_filename']
                key = output[0]['key']
                logging.info('Downloading files from bucket')
                s3_bucket.download_file(key, f'{temp_path}/{filename}')
                s3_bucket.delete_objects(
                    Delete={
                    'Objects': [
                        {
                            'Key': key,
                        },
                        {
                            'Key': key.replace('.tiff', '.json'),
                        }
                    ]
                })

                logging.info(f'Publishing to GeoServer: {filename}')
                try:
                    publish_timeseries_or_add_granule(
                        workspace_name = geoserver_workspace_name,
                        coverage_name = result['layer_name'],
                        full_filename = f'{temp_path}/{filename}',
                        # style_data = style_data
                    )

                    # logging.info(f'Inserting db record with granule_name: {filename}')
                    # insert_earth_observation(
                    #     layer_name=result['layer_name'],
                    #     polygon=result['polygon'],
                    #     date=result['start'],
                    #     granule_name=result['granule_filename'],
                    #     instrument=result['instrument'],
                    #     processing_module=result['processing_module'],
                    #     is_empty=False
                    # )

                except Exception:
                    logging.exception('Error publishing to GeoServer')
            else:
                try:
                    end_date = datetime.strptime(result['end'], '%Y-%m-%d').date()
                    if process['frequency'] == 'daily':
                        # For daily the tolerance is yesterday
                        days_delta = 1
                    else:
                        # For monthly or yearly, the tolerance today - 10 days
                        days_delta = 10

                    if end_date >= (date.today() - timedelta(days=days_delta)):
                        logging.info(f'Skipping inserting is_empty record because imagery may not be ready even with the valid date range')
                    else:
                        logging.info(f'Inserting is_empty db record with granule_name: {result["granule_filename"]}')
                        insert_earth_observation(
                            layer_name=result['layer_name'],
                            polygon=result['polygon'],
                            date=result['start'],
                            granule_name=result['granule_filename'],
                            instrument=result['instrument'],
                            processing_module=result['processing_module'],
                            is_empty=True
                        )
                except Exception:
                    logging.exception('Error inserting empty earth observation result into DB')