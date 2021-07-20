import configparser
from news_parser.settings import BASE_DIR

config = configparser.ConfigParser()
config.read(f"{BASE_DIR}/PARSER_CONFIG_FILE.ini")

CLUSTERS_QTY_LIMITER: int = int(config['APP OPERATION CONFIG']['CLUSTERS_QTY_LIMITER'])
CATEGORIES_FOR_PARSING: list[int] = [int(cat_id) for cat_id in config['APP OPERATION CONFIG']['CATEGORIES_FOR_PARSING'].split(',')]
BROWSER_HEADLESS: bool = config['APP OPERATION CONFIG'].getboolean('BROWSER_HEADLESS_LAUNCH')
