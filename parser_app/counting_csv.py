import csv
import os

from parser_app.decorators.decorators import count_processed_file_path, count_created_file_path


# Count number of NewsId in a csv count-files
def count_csv_values(file_count_type=""):
    if file_count_type.lower() == "processed":
        with open(count_processed_file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            lines = len(list(csv_reader))
        return lines
    if file_count_type.lower() == "created":
        with open(count_created_file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            lines = len(list(csv_reader))
        return lines


def clean_csv_count_files():
    if os.path.isfile(count_processed_file_path):
        try:
            with open(count_processed_file_path, "w+"):
                print(f"\tA 'processed' count file cleaned.")
        except Exception as e:
            print(f"Got an ERROR while a 'processed' count file cleaning.\nDescription:{e}")

    if os.path.isfile(count_created_file_path):
        try:
            with open(count_created_file_path, "w+"):
                print(f"\tA 'created' count file cleaned.\n")
        except Exception as e:
            print(f"Got an ERROR while a 'created' count file cleaning.\nDescription:{e}")