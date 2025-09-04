import sys
import json
import yaml
import jsonschema
from jsonschema import validate

def load_schema():
    with open('docs/model.jsonschema', 'r') as schema_file:
        return json.load(schema_file)
    
def load_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)
    
def validate_metadata(schema, metadata_file):
    try:
        metadata = load_yaml(metadata_file)
        validate(instance=metadata, schema=schema)
        print(f"✅ {metadata_file} - Valid")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ {metadata_file} - Invalid")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {metadata_file} - Error loading or parsing")
        print(f"Error: {e}")
        return False

def main():
    schema = load_schema()
    files = sys.argv[1:]
    
    all_valid = True
    for file in files:
        if not validate_metadata(schema, file):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
