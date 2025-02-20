import argparse
import asyncio
import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Tuple

from naptha_sdk.client.naptha import Naptha
from naptha_sdk.configs import setup_module_deployment
from naptha_sdk.modules.agent import Agent
from naptha_sdk.schemas import AgentRunInput
from naptha_sdk.user import sign_consumer_id

from agent_instance import generate_module_run
from chat_agent import ChatAgent
from common.Target import Target
from prompt import get_attacker_system_prompt
from schemas import InputSchema

# OPT 2
from adv_eva import EvaluatorAgent

# OPT 1
# from evaluator import EvaluatorAgent


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def invoke_agent(agent: Agent, consumer_id: str, messages: List[Dict[str, str]]) -> Optional[
    List[Dict[str, str]]]:
    """
    Invoke an AI agent with given messages.

    Args:
        agent (Agent): The AI agent instance.
        consumer_id (str): Consumer ID for authentication.
        messages (List[Dict[str, str]]): List of messages to send.

    Returns:
        Optional[List[Dict[str, str]]]: The parsed JSON response or None if an error occurs.
    """
    agent_run_input = AgentRunInput(
        consumer_id=consumer_id,
        inputs={"tool_name": "chat", "tool_input_data": messages},
        deployment=agent,
        signature=sign_consumer_id(consumer_id, os.getenv("PRIVATE_KEY"))
    )

    try:
        agent_response = await agent.run(agent_run_input)
        if agent_response and agent_response.results:
            return json.loads(agent_response.results[-1])
    except Exception as e:
        logger.exception(f"Failed to invoke agent: {e}")
    return None


def get_response(module_run: Dict) -> str:
    """
    Run an asynchronous module synchronously and return the response.

    Args:
        module_run (Dict): Module execution configuration.

    Returns:
        str: Response content.
    """
    response = asyncio.run(run(module_run))
    return response["choices"][0]["message"]["content"]


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

        # ✅ 修正：改为 await，而不是 asyncio.run()
        responses = await run(command)
        reply = next((res["content"] for res in responses if res["role"] == "assistant"), "")

        if "sorry" not in reply:
            try:
                data = json.loads(reply)
                prompt_text = data.get("prompt", "")

                attacker_messages.append(f">>> Attacker Agent: \n{prompt_text}")

                command1 = generate_module_run("user", prompt_text, target, consumer_id)

                # ✅ 修正：改为 await
                responses = await run(command1)
                target_reply = next((res["content"] for res in responses if res["role"] == "assistant"), "")

                target_messages.append(f">>> Target Agent: \n{target_reply}")

                # -----
                # OPT 2
                MetricResult = evaluator.evaluate_on_topic(target_str, target_reply)
                if MetricResult.passed:
                    logger.info("Target Achieved!")
                    break
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON response from agent: {e}")
                continue

    return attacker_messages, target_messages


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
    chat_agent = ChatAgent(module_run.deployment)
    method = getattr(chat_agent, module_run.inputs.tool_name, None)

    return await method(module_run.inputs)

def print_available_options():
    """Print available categories and their details."""
    print("\nAvailable categories and sizes:")
    Target.print_category_info()
    print("\nAvailable target models:", Target.ALLOWED_TARGETS)
    print("\nFor index, you can specify a number (0-based) or 'All' to try all goals in the category")
    print("\nExample commands:")
    print("  category government --index 0 --target chatgpt")
    print("  category bomb --index All --target anthropic")

async def run_single_test(consumer_id: str, attacker: Agent, target: Agent, goal: str, target_str: str):
    """Run a single red teaming test."""
    print(f"\nTesting goal: {goal}")

    # ✅ 修正：加上 await
    msg1, msg2 = await run_red_teaming(consumer_id, attacker, target, goal, target_str)

    print("\n==== Conversation Replay ====")
    for i, (m1, m2) in enumerate(zip(msg1, msg2)):
        print(f"\nRound {i + 1}:\n {m1}\n {m2}")
    print("========== END ==========\n")


def parse_user_input() -> Tuple[str, str, str]:
    """Parse user input in the format 'category <name> --index <num> --target <model>'."""
    while True:
        try:
            user_input = input("\nEnter command (or 'help' for options, 'quit' to exit): ").strip()

            if user_input.lower() == 'quit':
                exit(0)

            if user_input.lower() == 'help':
                print_available_options()
                continue

            # Split the input into parts
            parts = user_input.split()

            if len(parts) != 6 or parts[0] != 'category' or parts[2] != '--index' or parts[4] != '--target':
                raise ValueError("Invalid command format")

            category = parts[1]
            index = parts[3]
            target = parts[5]

            # Validate category
            if category not in Target.get_all_categories():
                raise ValueError(f"Invalid category. Use 'help' to see available categories.")

            # Validate index
            if index.lower() != 'all':
                try:
                    index_num = int(index)
                    if index_num < 0 or index_num >= Target.get_category_size(category):
                        raise ValueError
                except ValueError:
                    raise ValueError(
                        f"Invalid index. Must be between 0 and {Target.get_category_size(category) - 1} or 'All'")

            # Validate target
            if target not in Target.ALLOWED_TARGETS:
                raise ValueError(f"Invalid target model. Choose from: {Target.ALLOWED_TARGETS}")

            return category, index, target

        except ValueError as e:
            print(f"Error: {str(e)}")
            continue


async def run_single_test(consumer_id: str, attacker: Agent, target: Agent, goal: str, target_str: str):
    """Run a single red teaming test."""
    print(f"\nTesting goal: {goal}")

    # ✅ 修正：加上 await
    msg1, msg2 = await run_red_teaming(consumer_id, attacker, target, goal, target_str)

    print("\n==== Conversation Replay ====")
    for i, (m1, m2) in enumerate(zip(msg1, msg2)):
        print(f"\nRound {i + 1}:\n {m1}\n {m2}")
    print("========== END ==========\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("     🎭  -- Welcome to RedTeaming Simulation --  🚀")
    print("=" * 60)
    print("\n🚨🚨 Warning: This simulation is for security research & testing only! 🚨🚨")

    print_available_options()

    naptha = Naptha()


    async def main():
        while True:
            category, index, target_model = parse_user_input()

            target_agent = await setup_module_deployment(
                "agent",
                "red_teaming_agv/configs/deployment.json",
                deployment_name="target_1",
                node_url=os.getenv("NODE_URL")
            )

            attacker_agent = await setup_module_deployment(
                "agent",
                "red_teaming_agv/configs/deployment.json",
                deployment_name="attacker_1",
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
                    print(f"\n=== Testing {category} goal {i + 1}/{category_size} ===")
                    await run_single_test(naptha.user.id, attacker_agent, target_agent, goal, target_str)
            else:
                goal, target_str = Target.get_goal_target_pair(category, int(index))
                await run_single_test(naptha.user.id, attacker_agent, target_agent, goal, target_str)

            print("\nTest completed. You can run another test or type 'quit' to exit.")


    # Single asyncio.run() call at the top level
    asyncio.run(main())
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Multi-Agent Red Teaming")
#     parser.add_argument("--goal", type=str, required=True, choices=["0", "1"],
#                         help=f"0 - '{Target.ALLOWED_GOALS[0]}', 1 - '{Target.ALLOWED_GOALS[1]}'")
#     parser.add_argument("--target", type=str, required=True, choices=Target.ALLOWED_TARGETS,
#                         help=f"Choose which target agent to attack: {Target.ALLOWED_TARGETS}")
#
#     args = parser.parse_args()
#     goal = Target.ALLOWED_GOALS[int(args.goal)]
#     target_str = Target.TARGET_STRS[int(args.goal)]
#
#     print("\n" + "=" * 60)
#     print("     🎭  -- Welcome to RedTeaming Simulation --  🚀")
#     print("=" * 60)
#     print(f"📌 User Request Details:")
#     print(f"   🎯  Goal:         {goal}")
#     print(f"   🛡  Target Model: {args.target}")
#     print("\n🚨🚨 Warning: This simulation is for security research & testing only! 🚨🚨")
#     print("=" * 60 + "\n")
#
#     naptha = Naptha()
#
#     target_agent = asyncio.run(
#         setup_module_deployment("agent", "red_teaming_agv/configs/deployment.json",
#                                 deployment_name="target_1", node_url=os.getenv("NODE_URL")))
#
#     attacker_agent = asyncio.run(
#         setup_module_deployment("agent", "red_teaming_agv/configs/deployment.json",
#                                 deployment_name="attacker_1", node_url=os.getenv("NODE_URL")))
#
#     msg1, msg2 = run_red_teaming(naptha.user.id, attacker_agent, target_agent, goal, target_str)
#
#     print("==== Conversation Replay ====")
#     for i, (m1, m2) in enumerate(zip(msg1, msg2)):
#         print(f"\nRound {i + 1}:\n {m1}\n {m2}")
#     print("========== END ==========")
