import os
import yaml
import requests
import tqdm
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def check_model_existence(platform, model_name):
    if platform == 'huggingface':
        url = f"https://huggingface.co/api/models/{model_name}"
    elif platform == 'modelscope':
        url = f"https://www.modelscope.cn/api/v1/models/{model_name}"
    else:
        return False

    response = requests.get(url)
    return response.status_code == 200

def check_metadata_files(directory):
    modelmeta_files = []
    exists_models_report = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file == 'metadata.yaml':
                file_path = os.path.join(root, file)
                modelmeta_files.append(file_path)
    
    for file_path in tqdm.tqdm(modelmeta_files):
        with open(file_path, 'r') as f:
            metadata = yaml.safe_load(f)
            model_id = metadata.get('metadata', {}).get('name')
            hf_name = metadata.get('spec', {}).get('source', {}).get('huggingface', {}).get('name')
            ms_name = metadata.get('spec', {}).get('source', {}).get('modelscope', {}).get('name')

            if hf_name:
                exists = check_model_existence('huggingface', hf_name)
                if not exists:
                    exists_models_report[model_id] = {"huggingface": hf_name}
                    suggest = show_suggests('huggingface', model_id)
                    if suggest:
                        exists_models_report[model_id]['huggingface-suggest'] = suggest

            if ms_name:
                exists = check_model_existence('modelscope', ms_name)
                if not exists:
                    exists_models_report[model_id] = {"modelscope": ms_name}
                    suggest = show_suggests('modelscope', model_id)
                    if suggest:
                        exists_models_report[model_id]['modelscope-suggest'] = suggest
            if exists_models_report.get(model_id):
                print(exists_models_report[model_id])
    print(json.dumps(exists_models_report, indent=4))


# {
#     "Code": 200,
#     "Data": {
#         "Model": {
#             "Suggests": [
#                 {
#                     "ChineseName": "DeepSeek-R1-Distill-Qwen-14B",
#                     "Id": 413161,
#                     "Name": "DeepSeek-R1-Distill-Qwen-14B",
#                     "Path": "deepseek-ai"
#                 },
#                 {
#                     "ChineseName": "DeepSeek-R1-Distill-Qwen-14B-GGUF",
#                     "Id": 413488,
#                     "Name": "DeepSeek-R1-Distill-Qwen-14B-GGUF",
#                     "Path": "unsloth"
#                 },
#             ],
#         },
#     },
# }
def get_model_info_from_modelscope(model_name):
    url = f"https://modelscope.cn/api/v1/dolphin/model/suggestv2"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json={"PageSize":30,"PageNumber":1,"SortBy":"Default","Target":"","SingleCriterion":[],"Name":model_name})
    if response.status_code == 200:
        data = response.json()
        if data['Code'] == 200 and 'Model' in data['Data'] and 'Suggests' in data['Data']['Model']:
            suggests = data['Data']['Model']['Suggests']
            if len(suggests) >0 :
                return suggests[0]['Path']+"/"+suggests[0]['Name']
    return ""

# {
#     "models": [
#         {
#             "_id": "676ca1388118866906abbd7c",
#             "id": "hexgrad/Kokoro-82M"
#         },
#         {
#             "_id": "67a3b00e3cd25f353c561af8",
#             "id": "kudzueye/boreal-hl-v1"
#         },
#         {
#             "_id": "67b3e0fc5e13a2d1f85a6389",
#             "id": "Kijai/SkyReels-V1-Hunyuan_comfy"
#         },
#         {
#             "_id": "67831f6d63ffb0435b3e62ca",
#             "id": "onnx-community/Kokoro-82M-ONNX"
#         },
#         {
#             "_id": "668c08386feb1daa9556d41d",
#             "id": "KwaiVGI/LivePortrait"
#         },
#         {
#             "_id": "674f2f8f51a64ee560f8ae65",
#             "id": "Kijai/HunyuanVideo_comfy"
#         }
#     ],
#     "modelsCount": 0
# }
def get_model_info_from_huggingface(model_name):
    url = f"https://huggingface.co/api/quicksearch?type=model&q={model_name}"
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'models' in data and len(data['models']) > 0:
            return data['models'][0]['id']
    return ""


def show_suggests(platform, model_name):
    if platform == 'huggingface':
        return get_model_info_from_huggingface(model_name)
    elif platform == 'modelscope':
        return get_model_info_from_modelscope(model_name)
    else:
        return ""

if __name__ == "__main__":
    directory = './'
    check_metadata_files(directory)