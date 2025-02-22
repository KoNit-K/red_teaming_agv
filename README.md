# RedTeaming Simulation using Naptha SDK

## Overview
This project is a **Automatic Red-Teaming Framework** built using the **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)**.  The goal is to simulate adversarial attacks on AI agents to evaluate their robustness and response mechanisms. The system involves an **attacker agent** and a **target agent**, where the attacker attempts to exploit vulnerabilities by asking the target agent to respond to detrimental content. In addition to the two agents above, for each round of attack, we employ an **evaluator agent** to assess the attack prompt to guide the attacker for a more well-designed strategy in the next round. In most cases, our **attacker agent** successfully jailbreaks the **target agent** in less than 10 rounds of attack.
With **Naptha**’s decentralized execution model, this system can scale across distributed nodes, offering a **highly modular and extensible testing environment**.


## Key Features
✅ **Multi-Agent Red Teaming**: Attacker, Target, and Evaluator agents operate autonomously.

✅ **Naptha SDK Integration**: Enables modular AI model deployment and decentralized execution.

✅ **Adversarial Feedback Loop**: Attack prompts are refined across up to 10 iterations to optimize success rates.

✅ **Decentralized Asynchronous Execution**: Built on Naptha’s distributed framework, this system utilizes Python’s `asyncio` to efficiently manage AI-agent interactions across multiple Naptha nodes. Instead of running computations sequentially on a single machine, the Attacker, Target, and Evaluator agents operate in parallel across decentralized nodes, ensuring:

- Scalable execution of adversarial testing across different AI models.
- Non-blocking task management, allowing multiple attack iterations without bottlenecks.
- Seamless agent-to-agent communication over Naptha’s RPC-based node infrastructure.

✅ **Configurable LLM Backends**: Supports GPT-4o, Hermes3:8B, and Ollama models for diverse attack evaluations.

## Naptha SDK & Node Integration

### Naptha SDK – AI Agent Management
The Naptha SDK provides a modular framework for deploying and managing AI agents in a decentralized environment. This project integrates it to:

- Deploy attacker and target agents using setup_module_deployment().
- Authenticate API interactions via sign_consumer_id().
- Handle AI-generated responses asynchronously with AgentRunInput().

### Naptha Node – Decentralized Execution
To enhance scalability and security, this system is designed to run on Naptha nodes rather than a single machine. The node network ensures:

- Decentralized execution of red-teaming simulations.
- Flexible AI model hosting, with configurations stored in deployment.json.
- Efficient AI-agent communication managed via 'NODE_URL' and 'HUB_URL':
   ```sh
   export NODE_URL=http://localhost:7001  
   export HUB_URL=wss://hub.naptha.ai/rpc  
   ```
## Adversarial Red Teaming Process
This system follows a multi-step attack-evaluation cycle, refining adversarial prompts dynamically to bypass AI model safety mechanisms.

**1️⃣ Attack Initialization**
- Users specify a target category (e.g., misinformation, fraud, cybersecurity).

- The Attacker Agent generates an initial adversarial prompt.

**2️⃣ Attack Execution**
- The Target AI model processes the prompt and generates a response.

- If the response complies with safety constraints, the attack fails.

**3️⃣ Automated Attack Refinement**

The Evaluator Agent analyzes the response using:
- Subset matching (checks if restricted content is leaked).

- Hallucination detection (evaluates factual consistency).

- On-topic scoring (measures adversarial effectiveness).

A new adversarial prompt is generated based on this evaluation.

**4️⃣ Multi-Round Optimization**
- The attack process repeats across up to 10 iterations, dynamically improving the attacker’s approach.

- The system stops if the AI model is successfully jailbroken.





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

Your local testing environment is now ready to use! Run with the command below.


```sh
poetry run python red_teaming_agv/run.py

```



## Architecture
The project consists of the following key components:
- **`run.py`**: Entry point for running simulations.
- **`agent_instance.py`**: Handles agent interactions.
- **`chat_agent.py`**: Implements a chat-based AI agent.
- **`adv_eva.py`**: Evaluator that assesses attack and suggests modifications.
- **`schemas.py`**: Defines request/response schemas.
- **`configs/`**: Contains deployment configurations.

## Naptha SDK Integration
The system utilizes **[Naptha SDK](https://github.com/NapthaAI/naptha-sdk)** to manage AI agents. 

## Progress & Roadmap

### ✅ Done

- Developed multi-agent simulation framework.

- Integrated Naptha SDK for agent management.

- Implemented attack-evaluation feedback loop.

- Deployed local Naptha node for testing.

- Automated attack rounds up to 10 iterations.

## 🚀 To-Do

- Improve auto-evaluation mechanism for attacks.

- Introduce collaborative agents (attacker's co-pilot) to optimize strategies.

- Enhance the adversarial evaluator’s reviewer for better countermeasures.

- Expand attack categories and test cases.

We will also share our major updates and research on AI safety and mechanisms there. For the next version of the auto-red teaming project, we will focus on building a more robust automatic evaluation system so that collaborative (attacker's co-pilot) and adversarial (evaluator's reviewer) agents can emerge to help improve the success rate and efficiency of attacker agents.

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

## 📚 References
Zhang, W., Zang, C., & Kainz, B. (2024). **Truth or Deceit? A Bayesian Decoding Game Enhances Consistency and Reliability.** arXiv preprint arXiv:2410.01064. https://arxiv.org/abs/2410.01064

Mehrotra, A., et al. (2025). **Tree of Attacks: Jailbreaking Black-Box LLMs Automatically.** Advances in Neural Information Processing Systems, 37, 61065-61105.

Chao, P., et al. (2023). **Jailbreaking Black-Box Large Language Models in Twenty Queries.** arXiv preprint arXiv:2310.08419. https://arxiv.org/abs/2310.08419

Let me know if you need a different formatting style (e.g., APA, IEEE, Chicago).

