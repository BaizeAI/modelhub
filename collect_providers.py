import os
import yaml
import json
import glob

def collect_providers_info():
    """
    Collect provider information, icons, and links from existing model metadata files.
    """
    providers_info = {}
    model_mappings = {}
    
    # Find all metadata.yaml files
    metadata_files = glob.glob("models/**/metadata.yaml", recursive=True)
    print(f"Found {len(metadata_files)} metadata files")
    
    for file_path in metadata_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
                
            if not metadata:
                print(f"Warning: Empty metadata file: {file_path}")
                continue
            
            # Extract provider information
            provider_id = metadata.get('spec', {}).get('descriptor', {}).get('provider', {}).get('id')
            provider_name = metadata.get('spec', {}).get('descriptor', {}).get('provider', {}).get('name', {})
            icon = metadata.get('spec', {}).get('descriptor', {}).get('icon', {})
            links = metadata.get('spec', {}).get('descriptor', {}).get('links', [])
            
            # Get model sources
            hf_name = metadata.get('spec', {}).get('source', {}).get('huggingface', {}).get('name')
            
            # Determine model name for mapping
            if hf_name:
                parts = hf_name.split('/')
                if len(parts) == 2:
                    model_org, model_name = parts
                    
                    # Record the mapping from huggingface org to provider id
                    org_key = model_org.lower()
                    model_mappings[org_key] = provider_id
            
            if provider_id:
                # Initialize provider entry if it doesn't exist
                if provider_id not in providers_info:
                    providers_info[provider_id] = {
                        'icon': '',
                        'links': [],
                        'name': {'enUS': '', 'zhCN': ''}
                    }
                
                # Update provider info if not already set
                if not providers_info[provider_id]['icon'] and icon.get('src'):
                    providers_info[provider_id]['icon'] = icon['src']
                
                if not providers_info[provider_id]['links'] and links:
                    providers_info[provider_id]['links'] = links
                
                if not providers_info[provider_id]['name']['enUS'] and provider_name.get('enUS'):
                    providers_info[provider_id]['name'] = provider_name
        
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Compile the final result
    result = {
        'providers': providers_info,
        'mappings': model_mappings
    }
    
    return result

if __name__ == "__main__":
    providers_info = collect_providers_info()
    
    # Save to JSON file
    with open('providers_info.json', 'w', encoding='utf-8') as f:
        json.dump(providers_info, f, indent=2, ensure_ascii=False)
    
    print("Provider information saved to providers_info.json")
