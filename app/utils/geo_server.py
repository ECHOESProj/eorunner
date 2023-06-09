from app.init import get_env, get_path
from geoserver.catalog import Catalog
from geoserver.support import DimensionInfo
from app.utils.fs import ensure_folder, clear_folder, copy_folder, copy_files
import requests
import shutil
import ntpath
import logging

rest_url = get_env('GeoServer_RestUrl')
username = get_env('GeoServer_Username')
password = get_env('GeoServer_Password')
temp_path = get_env('Temp_Dir')

def get_catalog():
    return Catalog(rest_url, username=username, password=password)

def ensure_workspace(catalog: Catalog, name: str):
    workspace = catalog.get_workspace(name)

    if workspace == None:
        workspace = catalog.create_workspace(name, f'http://{name}.com/{name}')

    return workspace

def create_timeseries_store(catalog: Catalog, store_name: str, zip_path: str, workspace=None, layer_name=None, srs=None, footprint='Transparent'):
    if layer_name == None:
        layer_name = store_name

    logging.info(f'Creating ImageMosaic store')
    store = catalog.create_imagemosaic(
        name = store_name, 
        data = zip_path,
        workspace = workspace,
        coverageName = layer_name
    )
    # store = catalog.create_coveragestore(
    #     name=store_name,
    #     type='ImageMosaic',
    #     path=path,
    #     workspace=workspace,
    #     overwrite=True,
    #     create_layer=True,
    #     layer_name=layer_name
    # )

    # enable layer
    layer = catalog.get_layer(f'{workspace.name}:{layer_name}')
    layer.enabled=True
    catalog.save(layer)
    catalog.reload()

    # Update layer metadata to enable Time dimension using REST - not supported in python library
    logging.info(f'Updating layer metadata to enable Time dimension')
    url = f'{rest_url}/workspaces/{store.workspace.name}/coveragestores/{store_name}/coverages/{layer_name}'
    response = requests.get(
        url,
        auth=(username, password),
        headers={'Accept': 'application/json'}
    )

    metadata = response.json()['coverage']['metadata']

    # metadata.entry might be an object, not an array
    # Convert to array if it is an object
    if isinstance(metadata['entry'], list) == False:
        metadata['entry'] = [metadata['entry']]

    timeEntry = list(filter(lambda entry: entry['@key'] == 'time', metadata['entry']))

    if len(timeEntry) == 1:      
        timeEntry[0]['dimensionInfo']['enabled'] = True
        timeEntry[0]['dimensionInfo']['presentation'] = 'LIST'
        timeEntry[0]['dimensionInfo']['nearestMatchEnabled'] = True
    else:
        metadata['entry'].append({
            '@key': 'time',
            'dimensionInfo': {
                'enabled': True,
                'presentation': 'LIST',
                'units': 'ISO8601',
                'defaultValue': '',
                'nearestMatchEnabled': True,
                'rawNearestMatchEnabled': False
            }
        })
    
    requests.put(
        url,
        auth=(username, password),
        json={'coverage': { 'metadata': metadata }}
    )

    if srs != None:
        requests.put(
            url,
            auth=(username, password),
            json={'coverage': { 'srs': srs, 'projectionPolicy': 'FORCE_DECLARED' }}
        )

    if footprint != None:
        logging.info(f'Setting FootprintBehavior to {footprint}')
        parameters = response.json()['coverage']['parameters']

        # remove an entry which is just a string. 
        # With this string present, the update to parameters will fail
        # Seems to be an issue with GeoServer REST API
        badEntry = list(filter(lambda entry: isinstance(entry, str), parameters['entry']))   
        if(len(badEntry)):
            parameters['entry'].remove(badEntry[0])

        footprintEntry = list(filter(lambda entry: entry['string'][0] == 'FootprintBehavior', parameters['entry']))[0]
        footprintEntry['string'][1] = footprint

        requests.put(
            url,
            auth=(username, password),
            json={'coverage': { 'parameters': parameters }}
        ) 

    return store


def create_geotiff_store(catalog: Catalog, store_name: str, path: str, workspace=None, layer_name=None, srs=None):
    if layer_name == None:
        layer_name = store_name

    logging.info(f'Creating GeoTIFF store')
    store = catalog.create_coveragestore(
        name=store_name,
        type='GeoTIFF',
        path=path,
        workspace=workspace,
        overwrite=True,
        create_layer=True,
        layer_name=layer_name,
        upload_data=True
    )

    # enable layer
    layer = catalog.get_layer(f'{workspace.name}:{layer_name}')
    layer.enabled=True
    catalog.save(layer)
    catalog.reload()

    url = f'{rest_url}/workspaces/{store.workspace.name}/coveragestores/{store_name}/coverages/{layer_name}'

    if srs != None:
        requests.put(
            url,
            auth=(username, password),
            json={'coverage': { 'srs': srs, 'projectionPolicy': 'FORCE_DECLARED' }}
        )

    return store


def create_and_set_style(catalog: Catalog, workspace_name=None, layer_name=None, style_name=None, style_data=None, clear=True):
    logging.info(f'Creating style and setting as layer default')
    style = catalog.create_style(style_name, style_data, overwrite=True, workspace=workspace_name)
    layer = catalog.get_layer(f'{workspace_name}:{layer_name}')
    layer.default_style = style
    catalog.save(layer)

def set_style(catalog: Catalog, workspace_name=None, layer_name=None, style_name=None):
    logging.info(f'Getting style and setting as layer default')
    style = catalog.get_style(style_name, workspace=workspace_name)
    layer = catalog.get_layer(f'{workspace_name}:{layer_name}')
    layer.default_style = style
    catalog.save(layer)

def publish_timeseries(workspace_name, store_name, layer_name, zip_path, style_data = None, srs = None, footprint = 'Transparent', style_name = None, overwrite = True):
    catalog = get_catalog()
    workspace = ensure_workspace(catalog, workspace_name)

    layer = catalog.get_layer(f'{workspace_name}:{layer_name}')
    store = catalog.get_store(store_name, workspace)    

    # if layer and store exsit, and overwrite is false, exit
    if (overwrite == False and (layer != None and store != None)):
        return None

    # delete existing layer and store if they exist
    if layer != None:
        logging.info(f'Deleting existing layer {layer}')
        catalog.delete(layer)
        catalog.reload()
    
    if store != None:
        logging.info(f'Deleting existing store and files {store}')
        catalog.delete(store)
        catalog.reload()
        url = f'{rest_url}/resource/data/{workspace_name}/{store_name}'
        requests.delete(
            url,
            auth=(username, password)
        )
    
    store = create_timeseries_store( 
        catalog = catalog,
        store_name = store_name,
        zip_path = zip_path,
        workspace = workspace,
        layer_name = layer_name,
        srs = srs,
        footprint = footprint
    )

    if(style_name != None and style_data == None):
        set_style(
            catalog = catalog, 
            workspace_name = workspace_name, 
            layer_name = layer_name, 
            style_name = style_name
        )

    if(style_data != None and style_name == None):
        create_and_set_style(
            catalog = catalog, 
            workspace_name = workspace_name, 
            layer_name = layer_name, 
            style_data = style_data, 
            style_name= layer_name + '_style'
        )

    logging.info(f'Created timeseries store, layer and style. Workspace: {workspace_name}, Store: {store_name}, Layer: {layer_name}')
    return store


def add_timeseries_granule(workspace_name, store_name, path):
    catalog = get_catalog()

    catalog.add_granule(
        data = path, 
        store = store_name, 
        workspace = workspace_name
    )

    logging.info(f'Added grandule to Workspace: {workspace_name}, Store: {store_name}')


def publish_geotiff(workspace_name, store_name, layer_name, path, style_data = None, srs = None):
    catalog = get_catalog()
    workspace = ensure_workspace(catalog, workspace_name)

    # delete existing layer and store if they exist
    layer = catalog.get_layer(f'{workspace_name}:{layer_name}')
    if layer != None:
        logging.info(f'Deleting existing layer {layer}')
        catalog.delete(layer)
        catalog.reload()
    
    store = catalog.get_store(store_name, workspace)    
    if store != None:
        logging.info(f'Deleting existing store {store}')
        catalog.delete(store)
        catalog.reload()
    
    create_geotiff_store( 
        catalog = catalog,
        store_name = store_name,
        path = path,
        workspace = workspace,
        layer_name = layer_name,
        srs = srs
    )

    if(style_data != None):
        create_and_set_style(
            catalog = catalog, 
            workspace_name = workspace_name, 
            layer_name = layer_name, 
            style_data = style_data, 
            style_name= layer_name + '_style'
        )

    logging.info(f'Created timeseries store, layer and style. Workspace: {workspace_name}, Store: {store_name}, Layer: {layer_name}')

def check_exists(workspace_name, store_name, layer_name):
    catalog = get_catalog()
    layer = catalog.get_layer(f'{workspace_name}:{layer_name}')
    store = catalog.get_store(store_name, workspace_name)
    return (layer != None) and (store != None)


def create_timeseries_zip(file_name, path):
    temp_timeseries_path = ensure_folder(temp_path + '/timeseries')
    # clear any previous files
    clear_folder(temp_timeseries_path)
  
    file_path = f'{get_path(path)}/{file_name}'

    # copy single file
    copy_files(file_path, temp_timeseries_path)
    # copy timeseries files
    copy_folder(get_path('assets/timeseries_files'), temp_timeseries_path)

    zip_path = shutil.make_archive(f'{temp_timeseries_path}', 'zip', temp_timeseries_path)
    clear_folder(temp_timeseries_path)
    return zip_path


def create_single_granule_zip(file_name, path):
    # zip a single file, first argument is the full path of the zip file to
    # create
    # path is the directory to look in to find files to add to the zip
    # filename is the specifc file to zip
    zip_path = shutil.make_archive(f'{temp_path}/{file_name}', 'zip', path, file_name)
    return zip_path


def publish_timeseries_or_add_granule(workspace_name, coverage_name, full_filename, style_data = None):
    exists = check_exists(workspace_name, coverage_name, coverage_name)

    base_path, filename = ntpath.split(full_filename)

    # if the coverage already exists, just add a granule to it, otherwise
    # create the coverage
    if exists:
        logging.info('Coverage already exists, adding a granule to it')
        add_timeseries_granule(workspace_name = workspace_name, 
            store_name = coverage_name,
            path = create_single_granule_zip(file_name = filename,
                path = base_path 
            ))
    else:
        logging.info('Coverage does not exist, creating it with new granules')
        publish_timeseries(workspace_name = workspace_name, 
            store_name = coverage_name, 
            layer_name = coverage_name, 
            zip_path =  create_timeseries_zip(file_name = filename,
                path = base_path
            ), 
            style_data = style_data)


def get_granule_filenames(workspace_name, store_name, layer_name):
    try:
        catalog = get_catalog()
        granules = catalog.list_granules(layer_name, store_name, workspace_name)
        filenames = list(map(lambda x: x['properties']['location'], granules['features']))
        return filenames
    except:
        #logging.exception('Error getting granules')
        return []


def get_granules(workspace_name, store_name, layer_name):
    try:
        catalog = get_catalog()
        granules = catalog.list_granules(layer_name, store_name, workspace_name)
        return granules
    except:
        #logging.exception('Error getting granules')
        return None

