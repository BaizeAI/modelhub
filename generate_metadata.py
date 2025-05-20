import os
import yaml
import json
import requests
from huggingface_hub import HfApi

def get_readme_content(model_name):
    """
    Try to get the README.md content from the Hugging Face model repository.
    """
    print(f"Attempting to fetch README for {model_name}")
    
    try:
        # Try to directly get the README content from the repository
        readme_url = f"https://huggingface.co/{model_name}/raw/main/README.md"
        response = requests.get(readme_url, timeout=10)
        
        if response.status_code == 200:
            return response.text
        
        # If that fails, try alternate filenames
        for filename in ["README.md", "readme.md", "Readme.md", "README", "readme"]:
            try:
                readme_url = f"https://huggingface.co/{model_name}/raw/main/{filename}"
                response = requests.get(readme_url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except Exception:
                continue
        
        # Try the API to get the card data
        api_url = f"https://huggingface.co/api/models/{model_name}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            card_data = response.json()
            if "cardData" in card_data and card_data["cardData"]:
                return card_data["cardData"]
            
        return ""
    except Exception as e:
        print(f"Error fetching README content: {e}")
        return ""

def generate_description_from_readme(readme_content, model_name, max_length=500):
    """
    Generate a concise description from the README content.
    This is a simple extraction method that grabs the first few paragraphs.
    
    In a production environment, you'd use an LLM API like OpenAI to generate a better summary.
    """
    import re
    
    if not readme_content:
        return f"A large language model from {model_name.split('/')[0]}."
    
    # Remove HTML tags and URLs
    readme_content = re.sub(r'<[^<]+?>', ' ', readme_content)  # Remove HTML tags
    readme_content = re.sub(r'http[s]?://\S+', ' ', readme_content)  # Remove URLs
    readme_content = re.sub(r'\[.*?\]\(.*?\)', ' ', readme_content)  # Remove markdown links
    readme_content = re.sub(r'!\[.*?\]\(.*?\)', ' ', readme_content)  # Remove markdown images
    
    # Remove license information and other common non-description content
    readme_content = re.sub(r'license_link:.*', '', readme_content)
    readme_content = re.sub(r'License:.*', '', readme_content)
    
    # Simple extraction of the first few paragraphs without code blocks
    paragraphs = []
    in_code_block = False
    
    for line in readme_content.split('\n'):
        # Skip code blocks and tables
        if '```' in line:
            in_code_block = not in_code_block
            continue
        if in_code_block or line.startswith('|') or '---' in line:
            continue
            
        # Skip headers, badges, and empty lines
        if (line.strip().startswith('#') or 
            '![' in line or 
            line.strip() == '' or
            'badge' in line.lower()):
            continue
            
        # Clean the line of any remaining markdown artifacts
        line = line.strip()
        line = re.sub(r'[*_`]', '', line)  # Remove markdown formatting
        
        # Keep paragraphs of text that are reasonably sized and don't look like metadata
        if len(line) > 30 and not re.match(r'^[A-Za-z]+:\s', line) and line not in paragraphs:
            paragraphs.append(line)
            
        # If we have enough content, stop
        description = ' '.join(paragraphs)
        if len(description) >= max_length:
            break
    
    # If we have a description, format it and return
    if paragraphs:
        description = ' '.join(paragraphs)
        # Clean up any extra whitespace
        description = re.sub(r'\s+', ' ', description).strip()
        if len(description) > max_length:
            # Try to break at a sentence boundary
            sentences = re.split(r'(?<=[.!?])\s+', description[:max_length+30])
            if len(sentences) > 1:
                description = ' '.join(sentences[:-1])
            else:
                description = description[:max_length] + '...'
        return description
    else:
        # Fallback
        return f"A large language model from {model_name.split('/')[0]}."

def get_model_info_from_huggingface(model_name):
    print(f"Fetching info for {model_name} from Hugging Face")
    
    try:
        api = HfApi()
        description = ""
        tags = ["TEXT_GENERATION"]  # Default tag
        
        # Try to get the model info directly
        try:
            model_info = api.model_info(model_name)
            
            # Extract tags
            if model_info.tags:
                tags = model_info.tags
            
            # Do NOT use model_info.description directly as it might be a Python object
        except Exception as e:
            print(f"Error fetching model directly: {e}")
        
        # Try to get README content as our primary source of description
        readme_content = get_readme_content(model_name)
        if readme_content:
            description = generate_description_from_readme(readme_content, model_name)
        
        # Ensure we have some description, even if minimal
        if not description:
            description = f"A large language model from {model_name.split('/')[0]}."
            
        # Make sure description is a string, not an object
        if not isinstance(description, str):
            description = f"A large language model from {model_name.split('/')[0]}."
            
        return {
            "description": description,
            "tags": tags
        }
            
    except Exception as e:
        print(f"Error fetching model info: {e}")
        return {
            "description": f"A large language model from {model_name.split('/')[0]}.",
            "tags": ["TEXT_GENERATION"]  # Default tag
        }

def format_description(description):
    # Format the description for both English and Chinese
    return {
        "enUS": description,
        "zhCN": description  # In a real implementation, you would use translation API
    }
    
def get_provider_mapping(model_org):
    """Get provider ID from the organization name using collected mappings"""
    try:
        with open('providers_info.json', 'r', encoding='utf-8') as f:
            providers_info = json.load(f)
        
        mappings = providers_info.get('mappings', {})
        org_key = model_org.lower()
        
        if org_key in mappings:
            return mappings[org_key]
    except Exception as e:
        print(f"Error reading provider mappings: {e}")
    
    return model_org.lower()

def get_provider_info(provider_id):
    """Get provider information from the collected providers data"""
    try:
        with open('providers_info.json', 'r', encoding='utf-8') as f:
            providers_info = json.load(f)
        
        providers = providers_info.get('providers', {})
        if provider_id in providers:
            return providers[provider_id]
    except Exception as e:
        print(f"Error reading provider info: {e}")
    
    return {
        "icon": "",
        "links": [],
        "name": {"enUS": provider_id.capitalize(), "zhCN": provider_id.capitalize()}
    }
    
def create_metadata_yaml(model_name, output_path):
    # Extract provider and model ID from the model name
    parts = model_name.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid model name format: {model_name}, expected format: provider/model-id")
        
    model_org = parts[0]
    model_id = parts[1].lower().replace('.', '-')
    
    # Get model info from Hugging Face
    model_info = get_model_info_from_huggingface(model_name)
    
    # Get provider information from mappings
    provider_id = get_provider_mapping(model_org)
    provider_info = get_provider_info(provider_id)
    
    # Create the metadata structure
    metadata = {
        "apiVersion": "model.hydra.io/v1alpha1",
        "kind": "ModelSpec",
        "metadata": {
            "name": model_id
        },
        "spec": {
            "deployments": [
                {
                    "customRuntimeArgs": [],
                    "resourceRequirements": {
                        "cpu": 8,
                        "gpuCount": 8,
                        "gpuType": "nvidia-vgpu",
                        "memory": 640,
                        "perGPUMemoryGB": 80
                    },
                    "runtime": "vllm",
                    "versionRequired": ">=0.8.5"
                }
            ],
            "descriptor": {
                "description": format_description(model_info["description"]),
                "display": model_name.split('/')[-1],
                "icon": {
                    "src": provider_info.get("icon") or f"https://public-resources.d.run/models/logos/{provider_id.lower()}-model-logo.svg",
                    "type": "image/svg"
                },
                "links": provider_info.get("links") or [
                    {
                        "description": "About",
                        "url": f"https://github.com/{model_org}"
                    }
                ],
                "provider": {
                    "id": provider_id,
                    "name": provider_info.get("name") or {
                        "enUS": model_org,
                        "zhCN": model_org
                    }
                },
                "tags": model_info["tags"] if model_info["tags"] else ["TEXT_GENERATION"]
            },
            "source": {
                "huggingface": {
                    "name": model_name
                },
                "modelscope": {
                    "name": model_name
                }
            }
        }
    }
    
    # Write the metadata to a YAML file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return output_path

if __name__ == "__main__":
    import sys
    
    model_name = os.environ.get("MODEL_NAME")
    provider_name = os.environ.get("PROVIDER_NAME", "").lower()
    model_id = os.environ.get("MODEL_ID", "").lower()
    
    if not model_name:
        print("MODEL_NAME environment variable is required")
        sys.exit(1)
        
    output_path = f"models/{provider_name}/{model_id}/metadata.yaml"
    create_metadata_yaml(model_name, output_path)
    print(f"Metadata file created at {output_path}")
