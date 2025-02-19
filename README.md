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

```sh
pip install -r requirements.txt
```

You will also need a valid Naptha SDK account. Sign up at **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)** and obtain your API credentials.

## Usage
To start a Red Teaming attack simulation, run:

```sh
python run.py --category government --goal 0 --target target
```

### Arguments
| Argument | Type | Description |
|----------|------|-------------|
| `--category` | str | Red-teaming goal category |        
| `--goal` | int  | Attack goal (0: Bomb-making, 1: Software key retrieval) (more will be added...) |
| `--target` | str  | Target AI agent name("chatgpt", "anthropic", "gemini") |

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

