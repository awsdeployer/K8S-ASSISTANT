import boto3
import json
import logging
import subprocess

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# AWS Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Claude model
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


def get_kubectl_from_llm(question: str) -> str:
    """Ask Claude to generate a kubectl command for a natural language question."""
    logger.debug(f"Asking Claude with question: {question}")

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a Kubernetes assistant.\n"
                            "Convert natural language questions into valid kubectl commands.\n"
                            "Rules:\n"
                            "- Return ONLY the kubectl command.\n"
                            "- Do NOT use grep, awk, sed, or shell pipes.\n"
                            "- Always use kubectl flags instead of extra tools.\n"
                            "- Do not add explanations.\n\n"
                            f"Question: {question}\n\n"
                            "Output: only the kubectl command."
                        ),
                    }
                ],
            }
        ],
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
    )

    result = json.loads(response["body"].read())
    logger.debug(f"Claude raw response: {result}")

    command = result["content"][0]["text"].strip()

    # ✅ Ensure only kubectl commands are returned
    if not command.startswith("kubectl"):
        raise ValueError(f"Invalid command generated: {command}")

    # ✅ Add --no-headers when it's safe
    if "--no-headers" not in command and "-o" in command:
        command += " --no-headers"

    logger.info(f"Generated kubectl command: {command}")
    return command


def run_kubectl(command: str) -> str:
    """Run kubectl command and return its output or error."""
    try:
        logger.debug(f"Running command: {command}")
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, check=False
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            logger.error(f"Kubectl error: {error}")
            return f"❌ Error running command:\n{error or output}"

        if not output:
            logger.info("No output from kubectl command")
            return "⚠️ No results found"

        logger.debug(f"Command output: {output}")
        return output

    except Exception as e:
        logger.exception("Exception running kubectl command")
        return f"❌ Exception: {str(e)}"


def ask_k8s_bot(question: str) -> str:
    """Main entry: take natural language, convert to kubectl, run, return result."""
    try:
        kubectl_cmd = get_kubectl_from_llm(question)
        output = run_kubectl(kubectl_cmd)
        logger.debug(f"Command: {kubectl_cmd}\nOutput: {output}")
        return output
    except Exception as e:
        logger.exception("Error while processing question")
        return f"❌ Failed to process question: {str(e)}"

