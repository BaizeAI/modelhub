#!/bin/bash

# Input JSON
# json='{
#     "modelId": "deepseek-v3",
#     "modelAvatar": "https://public-resources.d.run/models/logos/deepseek-model-logo.svg",
#     "modelName": "DeepSeek-V3",
#     "providerId": "deepseek",
#     "providerName": {
#         "zhCn": "DeepSeek",
#         "enUs": "DeepSeek"
#     },
#     "modelDescription": {
#         "zhCn": "DeepSeek-V3 是一个拥有 6710 亿参数的专家混合语言模型，每个 token 激活 370 亿参数，在 14.8 万亿个 token 上训练，具备高级语言理解能力。",
#         "enUs": "DeepSeek-V3 is a 671B parameter Mixture-of-Experts language model, activating 37B parameters per token, trained on 14.8 trillion tokens for advanced language understanding."
#     },
#     "finetune": false,
#     "modelSupportFeature": [
#         "TEXT_GENERATION"
#     ],
#     "creationTimestamp": "2025-01-10T05:18:14Z",
#     "updateTimestamp": "2025-01-23T08:18:45Z",
#     "publicEndpointEnabled": true,
#     "publicEndpointBaseUrl": "https://cn-shanghai-a1.demo-dev-regions.daocloud.io",
#     "publicAccessModelName": "public/deepseek-v3",
#     "publicModelPrice": null,
#     "readme": null
# }'
root="/home/yang/workspace/hydra-io"

# Read JSON content from models.json
json=$(jq -c '.items[]' $root/modelhub/models/models.json)

# Convert each JSON item to YAML and output
echo "$json" | while read -r item; do
    yaml=$(echo "$item" | jq -r '
    {
        apiVersion: "model.hydra.io/v1alpha1",
        kind: "ModelSpec",
        metadata: {
            name: .modelId
        },
        spec: {
            install: {
                source: {
                    modelscope: {
                        name: (.providerId + "/" + .modelName),
                        git: ("https://www.modelscope.cn/" + .providerId + "/" + .modelName + ".git")
                    },
                    huggingface: {
                        name: (.providerId + "/" + .modelName),
                        git: ("https://huggingface.co/" + .providerId + "/" + .modelName)
                    },
                    registry: {
                        name: (.providerId + "/" + .modelName)
                    }
                },
                endpoint: {
                    enabled: .publicEndpointEnabled,
                    baseUrl: .publicEndpointBaseUrl,
                    accessName: .publicAccessModelName
                }
            },
            info: [
                {
                    name: "description.zhCn",
                    type: "Value",
                    value: .modelDescription.zhCn
                },
                {
                    name: "provider.zhCn",
                    type: "Value",
                    value: .providerName.zhCn
                }
            ],
            descriptor: {
                display: .modelName,
                links: [
                    {
                        description: "About",
                        url: "https://www.deepseek.com/"
                    }
                ],
                version: "4.9.4",
                description: .modelDescription.enUs,
                icons: [
                    {
                        src: .modelAvatar,
                        type: "image/svg",
                        size: "50x50"
                    }
                ],
                provider: [
                    {
                        name: .providerName.enUs,
                        url: "https://www.deepseek.com/"
                    }
                ]
            }
        }
    }' | yq e -P -)
    # echo "$yaml"
    filename="$root/modelhub/models/"$(echo "$item" | jq -r '(.providerId + "/" + .modelId + "/metadata.yaml")')
    mkdir -p $(dirname $filename)
    echo "$yaml" > $filename
done