# NOT IN USE - Keeping as reference

# from app.init import get_env, get_path
# from app.utils.geo_server import publish_timeseries_or_add_granule
# from app.utils.db import get_sites
# from ctypes import Array
# import json
# from datetime import date, datetime, timedelta
# import uuid
# from websocket import create_connection
# import re
# import logging
# from app.utils.s3 import bucket

# temp_path = get_env('Temp_Dir')
# geoserver_workspace_name = get_env('GeoServer_Workspace')
# geoserver_layer_name_prefix = get_env('GeoServer_Layer_Name_Prefix')
# websockets_url = get_env('WebSockets_Url')
# websockets_api_key = get_env('WebSockets_Api_Key')

# eo_processes = [
#     {
#         'name': 'ndvi',
#         'platform': 'Sentinel-2',
#         'args' : {
#             'instrument': 'sentinel2_l1c',
#             'processing_module': 'ndvi_s2',
#             'cloud_cover': 30
#         }
#     }
# ]

# def eo_processing_runner(sites: Array, start: date, end: date):  
#     for site in sites:
#         polygon = site['Polygon']

#         for process in eo_processes:
#             json_str = f'''{{
#                 "image": "eo-custom-scripts",
#                 "instrument": "{process['args']['instrument']}",
#                 "processing_module": "{process['args']['processing_module']}",
#                 "polygon": "{str(polygon)}",
#                 "start": "{start}",
#                 "end": "{end}",

#             }}'''

#             logging.info(f'Creating websockets connection to {websockets_url}?token={websockets_api_key}')
#             try:
#                 ws = create_connection(f'{websockets_url}?token={websockets_api_key}')
#                 logging.info(f'Sending JSON: {json_str}')
#                 ws.send(json_str)
#                 result = json.loads(ws.recv())
#                 logging.info(f'Recieved response: {result}')
#                 ws.close()
#                 yield {
#                     'process': process,
#                     'site': site,
#                     'polygon': str(polygon),
#                     'output': result['output']
#                 }
#             except Exception:
#                 logging.exception('Websockets error')
#                 yield {}

# def eo(start_date = None, end_date = None):
#     logging.info('Getting sites')
#     try:
#         sites = get_sites()
#     except Exception:
#         logging.exception('Error getting sites')
#         return

#     start = None
#     end = None

#     if start_date is not None and end_date is not None:
#         start = datetime.strptime(start_date, '%Y-%m-%d').date()
#         end =  datetime.strptime(end_date, '%Y-%m-%d').date()
#     else:
#         today = date.today()
#         start = today - timedelta(days=1)
#         end = today

#     for result in eo_processing_runner(sites, start, end):
#         if 'output' not in result:
#             logging.error('Error in previous run, skipping to next')
#             continue

#         # uid is a combination of the polygon and run date and layername
#         uid = str(uuid.uuid5(uuid.NAMESPACE_URL, result['polygon'] + str(start) + result['process']['name']))
#         file_basename = f'{start.year}{start.month:02}{start.day:02}_{uid}'

#         output = result['output']
#         if len(output):
#             logging.info('Downloading files from bucket')
#             # assuming tif is always first and json second
#             bucket.download_file(output[0]['key'], f'{temp_path}/{file_basename}.tif')
#             bucket.download_file(output[1]['key'], f'{temp_path}/{file_basename}.json')

#             logging.info(f'Publishing to GeoServer: {file_basename}')
#             layer_name = geoserver_layer_name_prefix + '_' + result['process']['name']
            
#             try:
#                 publish_timeseries_or_add_granule(
#                     workspace_name = geoserver_workspace_name,
#                     coverage_name = layer_name,
#                     full_filename = f'{temp_path}/{file_basename}.tif',
#                     style_data = open(get_path(f'assets/styles/{result["process"]["name"]}.sld'))
#                 )
#             except Exception:
#                 logging.exception('Error publishing to GeoServer')