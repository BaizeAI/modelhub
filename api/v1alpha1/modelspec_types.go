/*
Copyright 2025.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type ModelSpecGPUType string

const (
	NvidiaGPU  ModelSpecGPUType = "gpu"
	NvidiavGPU ModelSpecGPUType = "vgpu"
)

// TODO: uses quantity.Quantity instead of int
type ResourceRequirements struct {
	CPU            int              `json:"cpu"`
	GPUCount       int              `json:"gpuCount"`
	GPUType        ModelSpecGPUType `json:"gpuType"`
	Memory         int              `json:"memory"`
	PerGPUMemoryGB int              `json:"perGPUMemoryGB"`
}

type DeploymentRuntime string

const (
	RuntimeVLLM   DeploymentRuntime = "vllm"
	RuntimeSGLang DeploymentRuntime = "sglang"
)

type Deployment struct {
	// customRuntimeArgs is a list of custom runtime arguments to pass to the runtime
	CustomRuntimeArgs []string `json:"customRuntimeArgs,omitempty"`
	// resourceRequirements contains the resource requirements for the model
	ResourceRequirements ResourceRequirements `json:"resourceRequirements"`
	// runtime is the runtime to use for the model, eg. vllm, sglang, triton etc.
	Runtime DeploymentRuntime `json:"runtime"`
	// versionRequired is the version of the runtime required to run the model
	VersionRequired string `json:"versionRequired"`
}

type Description struct {
	EnUS string `json:"enUS"`
	ZhCN string `json:"zhCN"`
}

type Icon struct {
	Src  string `json:"src"`
	Type string `json:"type"`
}

type Link struct {
	Description string `json:"description"`
	URL         string `json:"url"`
}

type ProviderName struct {
	EnUS string `json:"enUS"`
	ZhCN string `json:"zhCN"`
}

type Provider struct {
	ID   string       `json:"id"`
	Name ProviderName `json:"name"`
}

type ModelSpecTag string

const (
	TextGeneration ModelSpecTag = "TEXT_GENERATION"
	VideoToText    ModelSpecTag = "VIDEO_TO_TEXT"
	TextToVideo    ModelSpecTag = "TEXT_TO_VIDEO"
	ImageToImage   ModelSpecTag = "IMAGE_TO_IMAGE"
	ImageToText    ModelSpecTag = "IMAGE_TO_TEXT"
	TextToImage    ModelSpecTag = "TEXT_TO_IMAGE"
	Embedding      ModelSpecTag = "EMBEDDING"
	RerankModel    ModelSpecTag = "RERANK_MODEL"
	AudioToAudio   ModelSpecTag = "AUDIO_TO_AUDIO"
	AudioToText    ModelSpecTag = "AUDIO_TO_TEXT"
)

type Descriptor struct {
	Description Description    `json:"description"`
	Display     string         `json:"display"`
	Icon        Icon           `json:"icon"`
	Links       []Link         `json:"links"`
	Provider    Provider       `json:"provider"`
	Tags        []ModelSpecTag `json:"tags"`
}

type Huggingface struct {
	// name is the path to the model on hugging face
	Name string `json:"name"`
}

type Modelscope struct {
	// name is the path to the model on model scope
	Name string `json:"name"`
}

type Source struct {
	Huggingface Huggingface `json:"huggingface"`
	Modelscope  Modelscope  `json:"modelscope"`
}

type ModelSpecSpec struct {
	// deployment contains information about deploying model to a runtime
	Deployments []Deployment `json:"deployments"`
	// descriptor contains metadata about the model
	Descriptor Descriptor `json:"descriptor"`
	// source indicates where to get the model weights
	Source Source `json:"source"`
}

// +kubebuilder:object:root=true

// ModelSpec is the Schema for the modelspecs API.
type ModelSpec struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec ModelSpecSpec `json:"spec,omitempty"`
}

// +kubebuilder:object:root=true

// ModelSpecList contains a list of ModelSpec.
type ModelSpecList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []ModelSpec `json:"items"`
}

func init() {
	SchemeBuilder.Register(&ModelSpec{}, &ModelSpecList{})
}
