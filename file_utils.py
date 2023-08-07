import json, os

def append_to_json_file(filename, new_value):

    def is_json_compliant(value): return isinstance(value, (str, int, float, bool, list, dict))

    if os.path.exists(filename):
        # If the file exists, read the existing JSON data
        with open(filename, 'r') as file: data = json.load(file)
        
        # Ensure the new value is JSON-compliant
        if not is_json_compliant(new_value):
            print("Error: The new value is not JSON-compliant. It should be a string, number, boolean, array, or dictionary.")
            return
        
        # Append the new value to the existing JSON array
        data.append(new_value)
    else:
        if not is_json_compliant(new_value):
            print("Error: The new value is not JSON-compliant. It should be a string, number, boolean, array, or dictionary.")
            return
        data = [new_value]
    
    # Write the updated JSON data to the file
    with open(filename, 'w') as file: json.dump(data, file, indent=4)
    