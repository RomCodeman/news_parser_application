from functools import wraps

import os
from news_parser.settings import BASE_DIR

import csv

count_proj_files_folder_path = "parser_app/counting"
count_abs_files_folder_path = os.path.join(BASE_DIR, count_proj_files_folder_path)
count_processed_file_path = f"{count_abs_files_folder_path}/counting_processed_items.csv"
count_created_file_path = f"{count_abs_files_folder_path}/counting_created_items.csv"


def add_processed_newsid_to_csv(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for cluster in func(*args, **kwargs):
            with open(count_processed_file_path, "a") as file_csv:
                # create a csv writer object
                csvwriter = csv.writer(file_csv, delimiter=',')
                news_id = str(cluster.get('NewsId'))
                # write the data in to a row
                csvwriter.writerow([news_id])
            yield cluster
    return wrapper


def add_created_newsid_to_csv(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            item_object, item_created = func(*args, **kwargs)
        except Exception as e:
            raise e
        if item_created:
            with open(count_created_file_path, "a") as file_csv:
                # create a csv writer object
                csvwriter = csv.writer(file_csv, delimiter=',')
                news_id = str(item_object.news_id)
                # write the data in to a row
                csvwriter.writerow([news_id])
        return item_object, item_created
    return wrapper
