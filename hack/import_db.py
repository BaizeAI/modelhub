# run sql: select a.*, b.name from model as a left join provider as b on a.provider_id=b.id
# to get the raw data
import os
import yaml
import json
import requests


orgs = json.load(open('hack/orgs.json', 'r', encoding='utf-8'))
suggests = json.load(open('hack/suggests.json', 'r', encoding='utf-8'))


def parse_resource_requirements(resource_requirements, runtime_image, custom_deploy_args_str):
    requirements = []
    if not resource_requirements:
        return requirements
    # 10.17.8.11/docker.io/vllm/vllm-openai:v0.6.5
    tag = runtime_image.split(':')[-1]
    custom_deploy_args = []
    if custom_deploy_args_str != None:
        try:
            custom_deploy_args = json.loads(custom_deploy_args_str)
        except:
            print(f"Error loading custom_deploy_args: {custom_deploy_args_str}")
    spec = json.loads(resource_requirements)
    for gpu_spec in spec["gpu"]:
        requirements.append({
            'runtime': 'vllm',
            'versionRequired': f">={tag}",
            'resourceRequirements': {
                'gpuType': 'nvidia-gpu' if gpu_spec['gpuType'] == 'gpu' else 'nvidia-vgpu', #?
                'gpuCount': gpu_spec['count'],
                'perGPUMemoryGB': gpu_memory_to_gb(gpu_spec['perGPUMemory']),
                'cpu': spec['cpu'],
                'memory': memory_to_gb(spec['memory'])
            },
            'customRuntimeArgs': custom_deploy_args
        })
    return requirements

# MB to GB
def memory_to_gb(memory):
    return int(memory/1024)

# Mi to Gi
def gpu_memory_to_gb(gpu_memory):
    return int(gpu_memory/1000)

def get_source(model_path):
    return {
        'modelscope': {
            'name': use_suggests("modelscope", model_path)
        },
        'huggingface': {
            'name': use_suggests("huggingface", model_path)
        }
    }


def create_yaml(model_data):
    model_id = model_data['model_id']
    model_name = model_data['model_name']
    model_description = yaml.safe_load(model_data['model_description'])
    resource_requirements = parse_resource_requirements(model_data['resources_requirements'], model_data['model_image'], model_data['custom_deploy_args'])
    provider_name = json.loads(model_data['provider'])
    provider_id = str.lower(provider_name['enUS'])
    model_path = f'{provider_id}/{model_id}'
    source = get_source(model_path)

    yaml_content = {
        'apiVersion': 'model.hydra.io/v1alpha1',
        'kind': 'ModelSpec',
        'metadata': {
            'name': model_id
        },
        'spec': {
            'source': source,
            'deployments': resource_requirements,
            'descriptor': {
                'display': model_name,
                'links': links(source),
                'description': model_description,
                'icon': {
                    'src': model_data['model_avatar'],
                    'type': 'image/svg'
                },
                'provider': {
                    'id': provider_id,
                    'name': provider_name,
                },
                'tags': json.loads(model_data['model_support_feature'])
            }
        }
    }
    
    return yaml_content



def use_suggests(platform, model_path):
    _, model_name = get_org_and_model_id(model_path)
    suggest = suggests.get(model_name)
    if suggest:
        if platform == 'modelscope':
            if not suggest.get('modelscope'):
                return model_path
            if model_path != suggest['modelscope']:
                print(f'{model_path} is not {suggest["modelscope"]}, there must be something wrong')
                return model_path
            if suggest['modelscope-suggest']:
                return suggest['modelscope-suggest']
            else:
                print(f'{model_path} has no suggestion about modelscope')
                return model_path
        elif platform == 'huggingface':
            if not suggest.get('huggingface'):
                return model_path
            if model_path != suggest['huggingface']:
                print(f'{model_path} is not {suggest["huggingface"]}, there must be something wrong')
                return model_path
            if suggest['huggingface-suggest']:
                return suggest['huggingface-suggest']
            else:
                print(f'{model_path} has no suggestion about huggingface')
                return model_path
        
    return model_path


def get_org_and_model_id(model_path):
    parts = model_path.split('/') 
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        print(f"Invalid model ID format {model_path}")
        return "", model_path

def links(source):
    for fn in [add_modelscope_about]:
        link = fn(source)
        if link:
            return [link]
    return []


# {
#     "Code": 200,
#     "Data": {
#         "Avatar": "https://resouces.modelscope.cn/avatar/6c8d6d52-b760-4538-9b32-35dd5ebecc68.jpg",
#         "DatasetNum": 0,
#         "Description": "[\"root\",{},[\"p\",{},[\"span\",{\"data-type\":\"text\"},[\"span\",{\"data-type\":\"leaf\"},\"\"]]]]",
#         "Email": "service@deepseek.com",
#         "FullName": "deepseek",
#         "GithubAddress": " https://www.deepseek.com/",
#         "IsSubscribe": false,
#         "Members": 6,
#         "ModelNum": 69,
#         "Name": "deepseek-ai",
#         "Stars": 633,
#         "StudioNum": 0
#     },
#     "Message": "success",
#     "RequestId": "8eec43d7-c448-4020-a807-df904f9b6c1a",
#     "Success": true
# }
def add_modelscope_about(source):
    org, _ = get_org_and_model_id(source['modelscope']['name'])
    if org == "LLM-Research":   # LLM-Research is a common org name
        org, _ = get_org_and_model_id(source['huggingface']['name'])

    if org in orgs:
        return {
            "description": "About",
            "url": orgs[org]['link']
        }
    url = f"https://www.modelscope.cn/api/v1/organizations/{org}/brief"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'Data' in data and 'GithubAddress' in data['Data']:
            link = data['Data']['GithubAddress']
            orgs[org] = {
                "link": link,
            }
            return {
                "description": "About",
                "url": link
            }
    print(f"Failed to fetch organization information for {org}.")
    return None

def main():
    json_file = 'models.json'
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    models = data['results']['B']['frames'][0]['data']['values']
    keys = ['model_id', 'model_name', 'model_description', 'model_avatar', 'provider_id', 'model_image', 'source', 'stop', 'stop_token_ids', 'host_path', 'finetune', 'model_support_feature', 'resources_requirements', 'create_time', 'update_time', 'end_time', 'update_by', 'create_by', 'del_flag', 'custom_deploy_args', 'public_endpoint_enabled', 'public_endpoint_base_url', 'public_access_model_name', 'provider']
    
    for model in zip(*models):
        model_data = dict(zip(keys, model))
        yaml_content = create_yaml(model_data)
        output_dir = os.path.join('models', yaml_content['spec']['descriptor']['provider']['id'], yaml_content['metadata']['name'])
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'metadata.yaml')
        with open(output_file, 'w', encoding='utf-8') as yamlfile:
            yaml.dump(yaml_content, yamlfile, allow_unicode=True)

    json.dump(orgs, open('hack/orgs.json', 'w', encoding='utf-8'), indent=4)

if __name__ == '__main__':
    main()

