import sys
import os
import re

def validate_directory_structure(file_path):
    # Expected pattern: models/{provider}/{model_id}/metadata.yaml
    pattern = r'^models/[a-z0-9-_]+/[a-z0-9-_.]+/metadata\.yaml$'
    if not re.match(pattern, file_path):
        print(f"❌ {file_path} - Invalid directory structure")
        print(f"   Expected pattern: models/{{provider}}/{{model_id}}/metadata.yaml")
        return False
    
    # Validate that model_id in path matches metadata.name
    import yaml
    try:
        with open(file_path, 'r') as f:
            metadata = yaml.safe_load(f)
            
        path_parts = file_path.split('/')
        provider_dir = path_parts[1]
        model_dir = path_parts[2]
        
        metadata_name = metadata.get('metadata', {}).get('name')
        metadata_provider = metadata.get('spec', {}).get('descriptor', {}).get('provider', {}).get('id')
        
        if model_dir != metadata_name:
            print(f"❌ {file_path} - Directory name ({model_dir}) doesn't match metadata.name ({metadata_name})")
            return False
            
        if provider_dir != metadata_provider:
            print(f"❌ {file_path} - Provider directory ({provider_dir}) doesn't match spec.descriptor.provider.id ({metadata_provider})")
            return False
            
        print(f"✅ {file_path} - Valid directory structure")
        return True
    except Exception as e:
        print(f"❌ {file_path} - Error checking directory structure: {e}")
        return False

def main():
    files = sys.argv[1:]
    all_valid = True
    
    for file in files:
        if not validate_directory_structure(file):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)

if __name__ == "__main__":
    main()
