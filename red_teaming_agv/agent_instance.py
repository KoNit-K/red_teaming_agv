import os

from naptha_sdk.user import sign_consumer_id


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