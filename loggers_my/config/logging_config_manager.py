# Import Required modules
import os
import logging
import logging.config
import sys
import yaml

from news_parser.settings import BASE_DIR

path_config_standard = f"{BASE_DIR}/loggers_my/config"
logs_folder = "loggers_my/logs"
logs_path = os.path.join(BASE_DIR, logs_folder)

"""
This function is used to setup root logging configuration,
* If LOG_CFG variable is set, then use it for logging configuration path
* Since we are using yaml configuration, we need yaml module to load configuration file
* Set Root logger configuration using `logging.config.dictConfig()`
* Any exception results in setting up root logger in default configuration. 
"""


# Function to configure logger
def setup_logging(default_path=f'{path_config_standard}/logging_config_preset.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """    
    | Logging Setup |
    :param default_path: Logging configuration path
    :param default_level: Default logging level
    :param env_key: Logging config path set in environment variable
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    if not os.path.exists(logs_path):
        try:
            os.makedirs(logs_path)
            print(f'\tLog files directory successfully created: {logs_path}')
        except Exception as e:
            print(f'Log files directory creating FAILED.\nDescription:{e}')
    else:
        print(f'\tLog files directory: {logs_path}\n')

    if os.path.exists(path):

        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                print(f'\tCustom logger settings successfully loaded.')
                print(f'\tYaml settings file directory: {path}\n')

            except Exception as e:
                print(f'Error in Logging Configuration. Exception is:{e}')
                logging.basicConfig(level=default_level, stream=sys.stdout)                
    else:
        logging.basicConfig(level=default_level, stream=sys.stdout)        
        print('Failed to load configuration file. Using default configs')
