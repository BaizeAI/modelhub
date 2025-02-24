import os
import yaml
import time

output_file = 'merged/index.yaml'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

merged_data = {
    'apiVersion': 'v1',
    'entries': [],
    'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
}

for root, _, files in os.walk('models'):
    for file in files:
        if file.endswith('metadata.yaml'):
            with open(os.path.join(root, file), 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    print(f"Error loading {file}, skipping")
                    continue
                merged_data["entries"].append(data)

merged_data["entries"].sort(key=lambda x: x['metadata']['name'])

with open(output_file, 'w') as f:
    yaml.dump(merged_data, f)