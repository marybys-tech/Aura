"""Thin wrapper over AWS Bedrock for Claude model invocations."""

import json
import logging

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        kwargs = {"region_name": settings.AWS_REGION}
        if settings.AWS_ACCESS_KEY_ID:
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        if settings.AWS_SECRET_ACCESS_KEY:
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        _client = boto3.client("bedrock-runtime", **kwargs)
    return _client


async def invoke_model(
    prompt: str,
    system: str = "",
    model_id: str | None = None,
    max_tokens: int = 200,
    temperature: float = 0.8,
) -> str | None:
    """Invoke a Bedrock Claude model. Returns response text or None on failure."""
    model = model_id or settings.BEDROCK_NARRATION_MODEL
    messages = [{"role": "user", "content": prompt}]
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system:
        body["system"] = system

    try:
        client = _get_client()
        response = client.invoke_model(
            modelId=model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    except (ClientError, KeyError, json.JSONDecodeError) as e:
        logger.warning("Bedrock invocation failed: %s", e)
        return None
