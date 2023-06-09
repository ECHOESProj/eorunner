from pathlib import Path
import psycopg2
import psycopg2.extras
from app.init import get_env
import logging
import uuid
from datetime import date, datetime, timezone, timedelta
import logging

hostname = get_env('PostgreSQL_Hostname')
username = get_env('PostgreSQL_Username')
password = get_env('PostgreSQL_Password')
database = get_env('PostgreSQL_Database')
tenantId = get_env('PostgreSQL_TenantId')

def select(selectQuery):
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cursor.execute(selectQuery)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# ST_AsText(ST_Envelope(ST_Buffer(ST_Centroid(unnest(ST_ClusterWithin(ST_Centroid("Polygon"),.08)))::geography, 10000)::geometry)) As "Polygon"
# ST_AsText(ST_Envelope(ST_Buffer(unnest(ST_ClusterWithin("Polygon",.05))::geography, 8000)::geometry)) As "Polygon"

def get_sites():
    # Group close sites together using ST_ClusterWithin (center point of sites within ~8km of each other are grouped)
    # Expand the area to 10km radius around the center of group of sites using ST_Buffer
    # Use ST_Envelope to convert the circle into a square (bbox) 
    return select(f'''
        WITH 
        grid AS ( -- create a grid of Ireland and Britain
            SELECT (ST_SquareGrid(.025, ST_Envelope(ST_Buffer(ST_Union("Polygon")::geography, 5000)::geometry))).*	
            FROM public."EchoesSites"
            WHERE "IsDeleted"=false AND "TenantId" = {tenantId}
        ),
        clusteredSites AS ( -- Group sites close together and buffer them slightly
            SELECT
                (ST_Envelope(ST_Buffer(unnest(ST_ClusterWithin("Polygon",.04))::geography, 2500)::geometry)) As "Polygon"
            FROM
                public."EchoesSites"
            WHERE
                "IsDeleted"=false AND "TenantId" = {tenantId}
        )
        SELECT ST_ASTEXT(ST_Envelope(ST_UNION(geom)), 3) as "Polygon" -- Join the grid squares back together for each clustered site
        FROM grid
        INNER JOIN clusteredSites ON ST_Intersects(grid.geom, clusteredSites."Polygon")
        Group By clusteredSites."Polygon"
    ''')

def insert_earth_observation(layer_name, polygon, date, granule_name, instrument, processing_module, is_empty):
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = conn.cursor()

    logging.info('Checking for duplicate entries in EarthObservations table')
    result = select(f"""
        SELECT "Id" FROM external_data."EarthObservations" 
        WHERE ST_Equals("Polygon", ST_GeomFromText(\'{polygon}', 4326)) 
        AND "LayerName"='{layer_name}'
        AND "Timestamp"::date = date '{date}';
    """)
    if len(result) == 0:
        #logging.info(f'Inserting record with granule_name: {granule_name}')
        query = f"""
            INSERT INTO external_data."EarthObservations"("LayerName", "Polygon", "Timestamp", "GranuleName", "Instrument", "ProcessingModule", "IsEmpty")
            VALUES ('{layer_name}', ST_GeomFromText('{polygon}', 4326), '{date}', '{granule_name}', '{instrument}', '{processing_module}', '{is_empty}');
        """
        cursor.execute(query)
        conn.commit()
    else:
        logging.info('Duplicate db entry found, skipping insert')

    cursor.close()
    conn.close()

def delete_earth_observation(granule_name):
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = conn.cursor()
 
    logging.info(f'Deleting db record with granule_name: {granule_name}')
    query = f"""
        DELETE FROM external_data."EarthObservations"
        WHERE "GranuleName" ILIKE '{granule_name}';
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def get_empty_earth_observations(layer_name):
    return select(f"""
        SELECT "Id", "Polygon", "Timestamp" FROM external_data."EarthObservations" 
        WHERE "LayerName"='{layer_name}'
        AND "IsEmpty" IS TRUE;
    """)

def get_empty_earth_observations_by_instrument(instrument, frequency):
    return select(f"""
        SELECT "Id", "Polygon", "Timestamp" FROM external_data."EarthObservations" 
        WHERE "Instrument"='{instrument}' AND "LayerName" LIKE '%{frequency}'
        AND "IsEmpty" IS TRUE;
    """)

if __name__ == '__main__':
    #result = select('SELECT * FROM public."EchoesEarthObservations";')
    #logging.info(result)    
    get_sites()
