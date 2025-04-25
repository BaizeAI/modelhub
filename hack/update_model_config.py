# update models to add maxTokens and TOOLS tag
import os

import requests
import yaml

def update_model_config(models_path):
    for root, dirs, files in os.walk(models_path):
        for file in files:
            if file == 'metadata.yaml':
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                    model_id = metadata.get('metadata', {}).get('name')
                    hf_name = metadata.get('spec', {}).get('source', {}).get('huggingface', {}).get('name')
                    if hf_name:
                        url = f"https://huggingface.co/{hf_name}/resolve/main/tokenizer_config.json"
                        response = requests.get(url)
                        if response.status_code != 200:
                            print(f"Failed to fetch tokenizer_config.json for {hf_name}.")
                            continue
                        tokenizer_config = response.json()
                        chat_template = tokenizer_config.get('chat_template')
                        if '{%- if tools %}' or 'custom_tools' in chat_template:
                            metadata.setdefault('spec', {}).setdefault('descriptor', {}).setdefault('tags', [])
                            if 'TOOLS' not in metadata['spec']['descriptor']['tags']:
                                metadata['spec']['descriptor']['tags'].append('TOOLS')
                        maxTokens = tokenizer_config.get('model_max_length', 0)
                        if maxTokens > 0:
                            metadata.setdefault('spec', {}).setdefault('config', {})
                            if 'maxTokens' not in metadata['spec']['config']:
                                metadata['spec']['config']['maxTokens'] = maxTokens
                        print(f"Model {model_id} maxTokens: {maxTokens}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            yaml.dump(metadata, f)
                        print(f"Updated {file_path} with TOOLS tag.")

if __name__ == '__main__':
    models_path = '../models'
    update_model_config(models_path)
