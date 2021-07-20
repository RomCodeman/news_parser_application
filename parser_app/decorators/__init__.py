import os
from news_parser.settings import BASE_DIR

count_proj_files_folder_path = "parser_app/counting"
count_abs_files_folder_path = os.path.join(BASE_DIR, count_proj_files_folder_path)
count_processed_file_path = f"{count_abs_files_folder_path}/counting_processed_items.csv"
count_created_file_path = f"{count_abs_files_folder_path}/counting_created_items.csv"

# A count files directory check and create if not exist
if not os.path.exists(count_abs_files_folder_path):
    try:
        os.makedirs(count_abs_files_folder_path)
        print(f"\tA count files folder created: {count_abs_files_folder_path}")
    except Exception as e:
        print(f'Got an ERROR while a count files folder creating\nDescription:{e}')
else:
    print(f"\tA count files folder directory: {count_abs_files_folder_path}\n")

# A 'processed' count file check and create if not exist
if not os.path.isfile(count_processed_file_path):
    try:
        with open(count_processed_file_path, "w+"):
            pass
        print(f"\tA count 'processed' file successfully created: {count_processed_file_path}")
    except Exception as e:
        print(f"Got an ERROR while a count file creating.\nDescription:{e}")
else:
    print(f'\tA count file is: {count_processed_file_path}\n')

# A 'created' count file check and create if not exist
if not os.path.isfile(count_created_file_path):
    try:
        with open(count_created_file_path, "w+"):
            pass
        print(f"\tA count 'created' file successfully created: {count_created_file_path}\n")
    except Exception as e:
        print(f"Got an ERROR while a count file 'created' creating.\nDescription:{e}")
else:
    print(f'\tA count file is: {count_created_file_path}\n')
