import json, metadata_utils, selenium
import file_utils
    
metadata_file_name = "metadata_results.json"

def merge_lists (list1, list2):
    merged_lists = []
    for item1 in list1:
        for item2 in list2:
            merged_lists.append(item1 + item2)
    return merged_lists

common_typos = json.loads(open("common_typos.json", "r").read())
homoglyphed_words = json.loads(open("homoglyphed_words.json", "r").read())
visual_typos = json.loads(open("visual_typos.json", "r").read())
popular_tlds = json.loads(open("popular_tlds.json", "r").read())

homoglyphed_domains = merge_lists (homoglyphed_words, popular_tlds)
common_typos = merge_lists (common_typos, popular_tlds)
visual_typos = merge_lists (visual_typos, popular_tlds)

final_list = homoglyphed_domains + common_typos + visual_typos

urlified_list = []
for item in final_list: urlified_list.append ("http://" + item)

for item in urlified_list:
    try:
        result = metadata_utils.get_page_metadata(item)
        print (json.dumps (result, indent=4))
        file_utils.append_to_json_file(metadata_file_name, result)
    except selenium.common.exceptions.WebDriverException: pass