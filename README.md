# RedTeaming Simulation using Naptha SDK

## Overview
This project is a **Red Teaming AI Simulation** built using the **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)**. The goal is to simulate adversarial attacks on AI agents to evaluate their robustness and response mechanisms. The system involves an **attacker agent** and a **target agent**, where the attacker attempts to exploit vulnerabilities while the target agent defends.

## Features
- **Multi-Agent Simulation**: Implements attacker and target agents.
- **Naptha SDK Integration**: Uses **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)** for agent management.
- **Automated Red Teaming Rounds**: Simulates up to 10 rounds per attack session.
- **Evaluation System**: Integrates an evaluator to determine if the attack was successful.
- **Asynchronous Execution**: Utilizes `asyncio` for efficient execution.

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed and the required dependencies:


# Deployment Guide

## 1. Set Up a Local Virtual Environment

### Option 1: Using Poetry
```sh
poetry new test-env
source .venv/bin/activate
```

### Option 2: Using an IDE's Built-in Virtual Environment
For example, in **PyCharm**:
1. Navigate to **Python Interpreter** → **Local Interpreter**
2. Select **Python 3.8+**
3. Activate the environment:
   ```sh
   source .venv/bin/activate
   ```

## 2. Install Naptha SDK
```sh
pip install naptha-sdk
```

## 3. Install OpenAI Library
```sh
poetry add openai
```

## 4. Prepare the `.env` File
```sh
cp .env.example .env
```

## 5. Let's Go!
```sh
poetry run python red_teaming_agv/run.py
```

## 5. Try with different target 
```sh
category [category] --index [index] --target [target_agent]
```
such as: 
```sh
category financial --index 0 --target chatgpt
```



# Deployment Guide for Local Testing Environment

## Overview
This guide provides instructions on setting up a local testing environment for running the Red Teaming Agent.

## Prerequisites
- Ensure you have Git installed.
- A Unix-based environment (Linux/macOS) or Windows with WSL.

## Setting Up the Local Node

Follow these steps to clone and launch the required node:

```sh
git clone https://github.com/NapthaAI/naptha-node.git
cd naptha-node
bash launch.sh
```

If all checks are marked ✅ at the end of the execution, the local node is running successfully.

## Configuring Red Teaming Agent

Once the node is up and running, configure your Red Teaming Agent with the following settings in .env:

```sh
export NODE_URL=http://localhost:7001
export HUB_URL=wss://hub.naptha.ai/rpc
```

Your local testing environment is now ready to use!

## try with those command
```sh
poetry run python red_teaming_agv/run.py

```


## Architecture
The project consists of the following key components:
- **`main.py`**: Entry point for running simulations.
- **`agent_instance.py`**: Handles agent interactions.
- **`chat_agent.py`**: Implements a chat-based AI agent.
- **`evaluator.py`**: Evaluates attack success.
- **`schemas.py`**: Defines request/response schemas.
- **`configs/`**: Contains deployment configurations.

## Naptha SDK Integration
The system utilizes **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)** to manage AI agents. 

### Key SDK Features Used:
- `AgentRunInput`: Defines agent input structure.
- `sign_consumer_id()`: Authenticates users.
- `setup_module_deployment()`: Deploys agent models.
- `ChatAgent`: Manages chat-based AI interactions.
- `EvaluatorAgent`: Evaluates red teaming effectiveness.

## License
This project is licensed under the MIT License.

## Disclaimer
This project is strictly for **security research and AI robustness evaluation**. It must **not** be used for any unethical or illegal activities.

## Contributing
We welcome contributions! Feel free to submit issues or pull requests.

## Contact
For questions or collaborations, reach out via [team@naptha.ai](team@naptha.ai).

