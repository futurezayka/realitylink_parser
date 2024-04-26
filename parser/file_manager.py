import json
import time


class FileManager:
    @staticmethod
    def write_to_json(residences, file_path=f'residences_{int(time.time())}.json'):
        with open(file_path, 'w') as json_file:
            json.dump([residence.dict() for residence in residences], json_file, indent=2)
        print(f"Data successfully written to {file_path}")
