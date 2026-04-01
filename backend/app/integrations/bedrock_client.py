"""Thin wrapper over AWS Bedrock — supports both Anthropic and Amazon Nova models."""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_client = None
_executor = ThreadPoolExecutor(max_workers=3)


def _get_client():
    global _client
    if _client is None:
        kwargs = {
            "region_name": settings.AWS_REGION,
            "config": BotoConfig(read_timeout=10, connect_timeout=5, retries={"max_attempts": 1}),
        }
        if settings.AWS_ACCESS_KEY_ID:
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        if settings.AWS_SECRET_ACCESS_KEY:
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        _client = boto3.client("bedrock-runtime", **kwargs)
    return _client


def _is_nova(model_id: str) -> bool:
    return "nova" in model_id.lower()


def _build_body(model: str, prompt: str, system: str, max_tokens: int, temperature: float) -> dict:
    """Build request body — different format for Anthropic vs Nova."""
    if _is_nova(model):
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        body: dict = {
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system:
            body["system"] = [{"text": system}]
        return body

    # Anthropic format
    messages = [{"role": "user", "content": prompt}]
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system:
        body["system"] = system
    return body


def _parse_response(model: str, result: dict) -> str:
    """Extract text from response — different structure for Anthropic vs Nova."""
    if _is_nova(model):
        return result["output"]["message"]["content"][0]["text"]
    return result["content"][0]["text"]


async def invoke_model(
    prompt: str,
    system: str = "",
    model_id: str | None = None,
    max_tokens: int = 200,
    temperature: float = 0.8,
) -> str | None:
    """Invoke a Bedrock model. Returns response text or None on failure."""
    model = model_id or settings.BEDROCK_NARRATION_MODEL
    body = _build_body(model, prompt, system, max_tokens, temperature)

    def _sync_invoke():
        client = _get_client()
        response = client.invoke_model(
            modelId=model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())
        return _parse_response(model, result)

    try:
        loop = asyncio.get_event_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(_executor, _sync_invoke),
            timeout=15,
        )
    except asyncio.TimeoutError:
        logger.error("BEDROCK TIMEOUT [model=%s]: exceeded 15s", model)
        return None
    except (ClientError, KeyError, json.JSONDecodeError) as e:
        logger.error("BEDROCK FAILED [model=%s]: %s", model, e)
        return None
