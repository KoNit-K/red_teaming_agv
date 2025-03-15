import json
import logging
import os
import uuid
from typing import Dict, List, Tuple


from naptha_sdk.inference import InferenceClient
from naptha_sdk.modules.agent import Agent
from naptha_sdk.schemas import AgentRunInput, AgentDeployment
from naptha_sdk.user import sign_consumer_id

from red_teaming_agv.chat_agent import ChatAgent
from red_teaming_agv.common.Target import Target
from red_teaming_agv.prompt import get_attacker_system_prompt
from red_teaming_agv.schemas import InputSchema, SystemPromptSchema, ChatInputSchema

from red_teaming_agv.adv_eva import EvaluatorAgent


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RedTeamingAgent(Agent):
    def __init__(self, deployment: AgentDeployment):
        self.deployment = deployment
        if deployment.config.persona_module and deployment.config.system_prompt["persona"]:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"], persona=deployment.config.system_prompt["persona"])
        else:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"])
        self.node = InferenceClient(self.deployment.node)

    async def run_red_teaming(consumer_id: str, attacker: Agent, target: Agent, goal: str, target_str: str) -> Tuple[
        List[str], List[str]]:
        """
        Simulates a red teaming scenario between an attacker and a target agent.
        """
        run_id = str(uuid.uuid4())
        logger.info(f"Starting RedTeaming session with run_id={run_id}")

        attacker_messages = []
        target_messages = []
        evaluator = EvaluatorAgent()

        for round_num in range(10):
            attacker_prompt = get_attacker_system_prompt(goal, target_str)
            command = generate_module_run("user", attacker_prompt, attacker, consumer_id)

            responses = await chat_run(command)
            reply = next((res["content"] for res in responses if res["role"] == "assistant"), "")

            if "sorry" not in reply:
                try:
                    data = json.loads(reply)
                    prompt_text = data.get("prompt", "")

                    attacker_messages.append(f">>> Attacker Agent: \n{prompt_text}\n")

                    command1 = generate_module_run("user", prompt_text, target, consumer_id)

                    responses = await chat_run(command1)
                    target_reply = next((res["content"] for res in responses if res["role"] == "assistant"), "")

                    target_messages.append(f">>> Target Agent: \n{target_reply}\n")

                    MetricResult = evaluator.evaluate_on_topic(target_str, target_reply)
                    if MetricResult.passed:
                        target_messages.append("\n--- Target Achieved! ---\n")
                        break
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response from agent: {e}")
                    continue

        return attacker_messages, target_messages

    async def run_single_test(consumer_id: str, attacker: Agent, target: Agent, goal: str, target_str: str):
        """Run a single red teaming test."""

        msg1, msg2 = await RedTeamingAgent.run_red_teaming(consumer_id, attacker, target, goal, target_str)

        response = ""
        response += "\n" + "=" * 60 +"\n"
        response += "     🎭  -- Welcome to RedTeaming Simulation --  🚀\n"
        response += "=" * 60 + "\n"
        response += "\n🚨🚨 Warning: This simulation is for security research & testing only! 🚨🚨\n"
        response += "\n==== Conversation Replay ====\n"
        for i, (m1, m2) in enumerate(zip(msg1, msg2)):
            response += f"\nRound {i + 1}:\n {m1}\n {m2}\n"
        response += "\n========== END ==========\n"
        return response

    async def teaming(self, inputs: InputSchema) -> str:
        naptha = Naptha()
        response_ = ""

        category, index, target_model = inputs.category, inputs.index, inputs.target

        target_agent = await setup_module_deployment(
            "agent",
            "red_teaming_agv/configs/deployment.json",
            deployment_name=target_model,
            node_url=os.getenv("NODE_URL")
        )

        attacker_agent = await setup_module_deployment(
            "agent",
            "red_teaming_agv/configs/deployment.json",
            deployment_name="red_teaming_agv",
            node_url=os.getenv("NODE_URL")
        )

        response_ += f"\n📌 Starting tests:\n"
        response_ += f"   📂  Category:     {category}\n"
        response_ += f"   🎯  Index:        {index}\n"
        response_ += f"   🛡  Target Model: {target_model}\n"

        if index.lower() == 'all':
            category_size = Target.get_category_size(category)
            for i in range(category_size):
                goal, target_str = Target.get_goal_target_pair(category, i)
                response_ += await RedTeamingAgent.run_single_test(naptha.user.id, attacker_agent, target_agent, goal,
                                                      target_str)
        else:
            goal, target_str = Target.get_goal_target_pair(category, int(index))
            response_ += f"\n=== Testing {goal} goal /{target_str} ===\n"
            response_ += await RedTeamingAgent.run_single_test(naptha.user.id, attacker_agent, target_agent, goal,
                                                  target_str)

        return response_

def generate_module_run(role: str, message: str, deployment, naptha_id):
    input_params = {
        "tool_name": "chat",
        "tool_input_data": [{"role": role, "content": message}],
    }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha_id,
        "signature": sign_consumer_id(naptha_id, os.getenv("PRIVATE_KEY"))
    }

    return module_run

async def run(module_run: Dict, *args, **kwargs):
    """
    Execute a module run asynchronously.

    Args:
        module_run (Dict): Configuration for module execution.

    Returns:
        Response from the executed module.
    """
    module_run = AgentRunInput(**module_run)
    module_run.inputs = InputSchema(**module_run.inputs)
    red_teaming_agv = RedTeamingAgent(module_run.deployment)
    method = getattr(red_teaming_agv, module_run.inputs.tool_name, None)
    print(f"method: {method}, inputs: {module_run.inputs}")
    return await method(module_run.inputs)


async def chat_run(module_run: Dict, *args, **kwargs):
    """
    Execute a module run asynchronously.

    Args:
        module_run (Dict): Configuration for module execution.

    Returns:
        Response from the executed module.
    """
    module_run = AgentRunInput(**module_run)
    module_run.inputs = ChatInputSchema(**module_run.inputs)
    chat_agent = ChatAgent(module_run.deployment)
    method = getattr(chat_agent, module_run.inputs.tool_name, None)

    return await method(module_run.inputs)





if __name__ == "__main__":
    import asyncio
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment

    naptha = Naptha()

    deployment = asyncio.run(setup_module_deployment("agent", "red_teaming_agv/configs/deployment.json", node_url = os.getenv("NODE_URL"), load_persona_data=False))

    input_params = {
        "tool_name": "teaming",
        "category": "financial",
        "index": "0",
        "target": "gpt-4o-mini",
    }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(module_run))

    print("Response: ", response)