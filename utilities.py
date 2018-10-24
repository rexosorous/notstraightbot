import json

def load_file(file_name: str) -> dict:
	with open(file_name) as file:
		return json.load(file)

def write_file(file_name: str, rewrite):
	with open(file_name, 'w') as file:
		json.dump(rewrite, file, indent=4)