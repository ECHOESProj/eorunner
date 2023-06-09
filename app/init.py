import sys
import pathlib
import os
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler

temp_foldername = '.temp'
log_filename = 'log'
log_arg = [arg for arg in sys.argv if '--log=' in arg]
if (len(log_arg)):
   log_filename = log_arg[0].replace('--log=', '')
   temp_foldername = '.temp/' + log_filename

file_handler = TimedRotatingFileHandler(f'logs/{log_filename}.txt', when='midnight', interval=1)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)

args = ''.join(sys.argv)
config_folder = os.path.join(os.path.dirname(__file__), 'config') # f'{base_dir}/config'

is_dev = '--env=dev' in args
is_qa = '--env=qa' in args
is_production = '--env=production' in args
is_staging = '--env=staging' in args

# Local overrides
load_dotenv(f'{config_folder}/overrides.env')
load_dotenv(f'{config_folder}/local.env')

if is_production:
  logging.info('env: Production')
  load_dotenv(f'{config_folder}/production.env')
elif is_staging:
  logging.info('env: Staging')
  load_dotenv(f'{config_folder}/staging.env')
elif is_qa:
  logging.info('env: QA')
  load_dotenv(f'{config_folder}/qa.env')
elif is_dev:
  logging.info('env: DEV')
  load_dotenv(f'{config_folder}/dev.env')
else:
  logging.info('env: NONE')

load_dotenv(f'{config_folder}/base.env')

def get_env(key):
    if(key == 'Temp_Dir'):
       return os.path.join(os.path.dirname(__file__), temp_foldername)
    return os.getenv(key)

def get_path(path):
    return os.path.join(os.path.dirname(__file__), path)

# Workaround for snappy
sys.path.append(get_path('../.venv/Lib'))
