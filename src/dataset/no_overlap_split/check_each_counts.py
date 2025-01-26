import os
import json
import pandas as pd

def load_files_for_lang(input_data_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(input_data_path):
        for filename in filenames:
            if "json" in filename:
                files.append(os.path.join(dirpath, filename))
    return files

def loads_json(load_file_name):
    with open(load_file_name, "r", encoding="utf-8") as stream:
        data = json.load(stream)
    return data


if __name__=="__main__":
    
    languages = ["english", "french", "italian", "romanian", "russian", "turkish", "ukrainian"]
    file_list = []
    for language in languages:
        folder = f"/home/upadro/code/thesis/output/dataset_outputs/{language}/done"
        files = load_files_for_lang(folder)
        total_number_of_data = 0
        
        for file in files:
            json_data = loads_json(file)
            
            total_number_of_data += len(json_data)
        json_data_lang = {
                "language": language
            }
        for file in files:
            print(file)
            json_data = loads_json(file)
            
            query_set = set()
            for item in json_data:
                query_set.add(" ".join(item["query"]))
            
            query_list = list(query_set)
            percentage = len(json_data)/total_number_of_data if total_number_of_data!=0 else 0
            # json_data_lang[f"{'_'.join(file.split('.')[0].split('/')[-1].split('_')[:-2])}_unique_query_counts"] = str(len(query_list))
            if len(json_data) != 0:
                # json_data_lang[f"{'_'.join(file.lower().split('.')[0].split('/')[-1].split('_relevant')[0].split('_')[:-1])}"] = f"total : {len(json_data)}; unique_query : {len(query_list)}; percentage_of_total : {percentage}"
                json_data_lang[f"{'_'.join(file.lower().split('.')[0].split('/')[-1].split('_relevant')[0].split('_')[:-1])}"] = percentage
            # json_data_lang[f"{'_'.join(file.split('.')[0].split('/')[-1].split('_')[:-2])}_percentage"] = str(len(json_data)/total_number_of_data if total_number_of_data!=0 else 0)
            
        file_list.append(
            json_data_lang
        )
        
    df = pd.DataFrame(file_list)

    df.to_csv("output/new_split_info/split_info_output_file.csv", index=False)

    print("Data successfully saved to output_file.csv")