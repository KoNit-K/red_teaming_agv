#!/usr/bin/env python
import json
import logging
from red_teaming_agv.schemas import InputSchema, SystemPromptSchema
from naptha_sdk.schemas import AgentDeployment
from naptha_sdk.inference import InferenceClient

logger = logging.getLogger(__name__)

class ChatAgent:

    def __init__(self, deployment: AgentDeployment):
        self.deployment = deployment
        if deployment.config.persona_module and deployment.config.system_prompt["persona"]:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"], persona=deployment.config.system_prompt["persona"])
        else:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"])
        self.node = InferenceClient(self.deployment.node)

    async def chat(self, inputs: InputSchema):
        if isinstance(inputs.tool_input_data, list):
            messages = [msg for msg in inputs.tool_input_data if msg["role"] != "system"]
        elif isinstance(inputs.tool_input_data, str):
            messages = [{"role": "user", "content": inputs.tool_input_data}]
        messages.insert(0, {"role": "system", "content": json.dumps(self.deployment.config.system_prompt)})

        response = await self.node.run_inference({"model": self.deployment.config.llm_config.model,
                                                    "messages": messages,
                                                    "temperature": self.deployment.config.llm_config.temperature,
                                                    "max_tokens": self.deployment.config.llm_config.max_tokens})

        if isinstance(response, dict):
            response = response['choices'][0]['message']['content']
        else:
            response = response.choices[0].message.content
        logger.info(f"Response: {response}")

        messages.append({"role": "assistant", "content": response})

        messages = [msg for msg in messages if msg["role"] != "system"]

        return messages

