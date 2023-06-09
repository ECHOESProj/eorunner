# NOT IN USE - Keeping as reference

# from app.init import get_env, get_path
# from app.utils.geo_server import publish_timeseries_or_add_granule
# from app.utils.db import select
# import logging
# from ctypes import Array
# from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta
# from websocket import create_connection
# import json
# import re
# import uuid
# from app.utils.s3 import bucket
# from .eom_processes import eom_processes 

# temp_path = get_env('Temp_Dir')
# geoserver_workspace_name = get_env('GeoServer_Workspace')
# geoserver_layer_name_prefix = get_env('GeoServer_Layer_Name_Prefix')
# websockets_url = get_env('WebSockets_Url')
# websockets_api_key = get_env('WebSockets_Api_Key')

# def get_subdivided_region():
#     return select(f'''
#             WITH grid AS (
#             SELECT (ST_SquareGrid(.1, "Polygon")).*
#                 FROM public.regions
#             )
#             SELECT ST_AsText(GEOM) as "Polygon"
#             FROM grid
#             INNER JOIN public.regions ON ST_Intersects(grid.geom, public.regions."Polygon")
#             WHERE "IsDeleted" = false
#             Group By grid.geom
#         ''')

# def eom_processing_runner(sites: Array, start: date, end: date):  
#     for site in sites:
#         polygon = site['Polygon']

#         for process in eom_processes:
#             json_str = f'''{{
#                 "image": "eo-custom-scripts",
#                 "instrument": "{process['args']['instrument']}",
#                 "processing_module": "{process['args']['processing_module']}",
#                 "polygon": "{str(polygon)}",
#                 "start": "{start:%Y-%m-%d}",
#                 "end": "{end:%Y-%m-%d}"
#             }}'''
            
#             logging.info(f'Creating websockets connection to {websockets_url}')
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

# def eom_region(start_date = None, end_date = None):
#     logging.info('Getting subdivided region of interest')
#     try:
#         areas = get_subdivided_region()
#     except Exception:
#         logging.exception('Error getting region')
#         return

#     start = None
#     end = None

#     if start_date is not None and end_date is not None:
#         start = datetime.strptime(start_date, '%Y-%m-%d').date()
#         end = datetime.strptime(end_date, '%Y-%m-%d').date()
#     else:
#         today = datetime.strptime('2021-06-16', '%Y-%m-%d').date()
#         #today = date.today()
#         month = datetime(today.year, today.month, 1)
#         # minus 2 months for now, passing a range of exactly one month returns no results
#         start = month + relativedelta(months=-2) 
#         end = month

#     #areas = areas[0:4]
#     for result in eom_processing_runner(areas, start, end):
#         if 'output' not in result:
#             logging.error('Error in previous run, skipping to next')
#             continue

#         output = result['output']

#         tiffs_list = [x for x in output if '.tiff' in x['key']]
#         for tiff in tiffs_list:
#             parsed_date = re.search('(\d{8})-\d{8}', tiff['key']).group(1)
#             uid = str(uuid.uuid5(uuid.NAMESPACE_URL, result['polygon']))
#             file_basename = f'{parsed_date}_{uid}'
#             logging.info('Downloading tiff from bucket')
#             bucket.download_file(tiff['key'], f'{temp_path}/{file_basename}.tif')

#             logging.info(f'Publishing to GeoServer: {file_basename}')
#             layer_name = geoserver_layer_name_prefix + '_' + result['process']['name'] + '_region'

#             try:
#                 publish_timeseries_or_add_granule(
#                     workspace_name = geoserver_workspace_name,
#                     coverage_name = layer_name,
#                     full_filename = f'{temp_path}/{file_basename}.tif'
#                 )
#             except Exception:
#                 logging.exception('Error publishing to GeoServer')