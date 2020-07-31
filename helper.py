import json
import os


# Writes specified data to the specified file
def write_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
