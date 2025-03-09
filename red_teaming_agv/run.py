import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Tuple


from naptha_sdk.inference import InferenceClient
from naptha_sdk.modules.agent import Agent
from naptha_sdk.schemas import AgentRunInput, AgentDeployment
from naptha_sdk.user import sign_consumer_id

from agent_instance import generate_module_run
from chat_agent import ChatAgent
from common.Target import Target
from prompt import get_attacker_system_prompt
from red_teaming_agv.helper.input_parse import print_available_options, parse_user_input
from schemas import InputSchema, SystemPromptSchema, ChatInputSchema

from adv_eva import EvaluatorAgent


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

                    attacker_messages.append(f">>> Attacker Agent: \n{prompt_text}")

                    command1 = generate_module_run("user", prompt_text, target, consumer_id)

                    responses = await chat_run(command1)
                    target_reply = next((res["content"] for res in responses if res["role"] == "assistant"), "")

                    target_messages.append(f">>> Target Agent: \n{target_reply}")

                    MetricResult = evaluator.evaluate_on_topic(target_str, target_reply)
                    if MetricResult.passed:
                        logger.info("Target Achieved!")
                        break
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response from agent: {e}")
                    continue

        return attacker_messages, target_messages

    async def run_single_test(consumer_id: str, attacker: Agent, target: Agent, goal: str, target_str: str):
        """Run a single red teaming test."""
        print(f"\nTesting goal: {goal}")

        msg1, msg2 = await RedTeamingAgent.run_red_teaming(consumer_id, attacker, target, goal, target_str)

        print("\n==== Conversation Replay ====")
        for i, (m1, m2) in enumerate(zip(msg1, msg2)):
            print(f"\nRound {i + 1}:\n {m1}\n {m2}")
        print("========== END ==========\n")

    async def teaming(self, target_agent: str):
        print("\n" + "=" * 60)
        print("     🎭  -- Welcome to RedTeaming Simulation --  🚀")
        print("=" * 60)
        print("\n🚨🚨 Warning: This simulation is for security research & testing only! 🚨🚨")

        print_available_options()

        naptha = Naptha()

        selected_config = target_agent if Target.ALLOWED_TARGETS.__contains__(target_agent) else "gpt-4o-mini"
        print(f"\nSelected config: {selected_config}")
        async def input_desk():
            while True:
                category, index, target_model = parse_user_input()

                target_agent = await setup_module_deployment(
                    "agent",
                    "red_teaming_agv/configs/deployment.json",
                    deployment_name=selected_config,
                    node_url=os.getenv("NODE_URL")
                )

                attacker_agent = await setup_module_deployment(
                    "agent",
                    "red_teaming_agv/configs/deployment.json",
                    deployment_name="red_teaming",
                    node_url=os.getenv("NODE_URL")
                )

                print(f"\n📌 Starting tests:")
                print(f"   📂  Category:     {category}")
                print(f"   🎯  Index:        {index}")
                print(f"   🛡  Target Model: {target_model}")

                if index.lower() == 'all':
                    category_size = Target.get_category_size(category)
                    for i in range(category_size):
                        goal, target_str = Target.get_goal_target_pair(category, i)
                        await RedTeamingAgent.run_single_test(naptha.user.id, attacker_agent, target_agent, goal,
                                                              target_str)
                else:
                    goal, target_str = Target.get_goal_target_pair(category, int(index))
                    print(f"\n=== Testing {goal} goal /{target_str} ===")
                    await RedTeamingAgent.run_single_test(naptha.user.id, attacker_agent, target_agent, goal,
                                                          target_str)

                print("\nTest completed. You can run another test or type 'quit' to exit.")

        await input_desk()


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
    chat_agent = RedTeamingAgent(module_run.deployment)
    method = getattr(chat_agent, module_run.inputs.tool_name, None)
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
        "tool_input_data": "gpt-4o-mini",
    }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(module_run))

    print("Response: ", response)