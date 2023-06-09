import logging

from app.init import get_env, get_path
from app.processes.eom import eom
# from app.processes.eom_region import eom_region
# from app.processes.eo import eo
from app.utils.fs import clear_folder, ensure_folder
import click
from enum import Enum
from app.processes.eom_cleanup import eom_cleanup
temp_path = get_env('Temp_Dir')

ensure_folder(temp_path)

class Processor(Enum):
    #eo = 'eo'
    eom = 'eom'
    #eom_region = 'eom_region'

@click.command(context_settings=dict(
     ignore_unknown_options=True,
     allow_extra_args=True
))
@click.argument('processor')
@click.option('--start')
@click.option('--end')
@click.option('--backdate', '-b', is_flag=True)
@click.option('--module', '-m', multiple=True)
@click.option('--cleanup', is_flag=True)
def cli(processor, start, end, backdate, module, cleanup):
    """Program to run EO processing and publish the outputs."""

    # dev overrides
    # processor = 'eom'
    # start = '2021-04-01'
    # end = '2021-05-01'

    logging.info(f'Arguments: processor: {processor}, start: {start}, end: {end}, module list: {module}, backdate: {backdate}, cleanup: {cleanup}')
    clear_folder(temp_path)

    if processor == Processor.eom.name:
        if cleanup:
            eom_cleanup(process_filter = module)
        eom(
            start_date = start,
            end_date = end,
            process_filter = module,
            backdate = backdate
        )
        if cleanup:
            eom_cleanup(process_filter = module)
    # elif processor == Processor.eo.name:
    #     eo(start, end)
    # elif processor == Processor.eom_region.name:
    #     eom_region(start, end)
    else:
        logging.error(f'Processor "{processor}" does not exist')

    clear_folder(temp_path)

if __name__ == "__main__":

    logging.info('PostgreSQL_Hostname: ' + get_env('PostgreSQL_Hostname'))
    logging.info('PostgreSQL_Database: ' + get_env('PostgreSQL_Database'))
    logging.info('GeoServer_RestUrl: ' + get_env('GeoServer_RestUrl'))
    logging.info('GeoServer_Workspace: ' + get_env('GeoServer_Workspace'))
    logging.info('WebSockets_Url: ' + get_env('WebSockets_Url'))

    cli()

    # Run for today
    # eom()

    # Run for a specific month with a select filter
    #eom('2018-01-01', '2018-02-01', process_filter = ['ndvi']) 

    # Run for a range of months
    #eom('2017-01-01', '2020-12-31', process_filter = ['vpp-amplitude-ampl'])
    #eom('2017-01-01', '2020-12-31', process_filter = ['^vpp-'])

    #eom('2023-03-01', '2023-05-1', process_filter = ['barren_soil'])

    #eom(backdate=True) 
    #eom(backdate=True, process_filter = ['^vpp-', '^global_surface'])


    # eom_region
    # eom_region('2019-06-01', '2019-07-01')
    clear_folder(temp_path)