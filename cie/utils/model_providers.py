"""
Model provider implementations for CIE.
"""

import json
import os
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Protocol

from cie.config.settings import get_config


class ModelProvider(Protocol):
    """Protocol for model providers."""

    name: str
    model_name: str

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using the model."""
        ...

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings for text."""
        ...

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model."""
        ...


class BaseModelProvider(ABC):
    """Base class for model providers."""

    name: str = "base"  # Default name, should be overridden by subclasses

    def __init__(self, model_name: str, api_key: str | None = None, **kwargs: Any):
        self.model_name = model_name
        self.api_key = api_key
        self.kwargs = kwargs
        self.config = get_config()

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using the model."""
        pass

    @abstractmethod
    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings for text."""
        pass

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model."""
        return {
            "name": self.name,
            "model_name": self.model_name,
            "provider": self.__class__.__name__,
        }


class OpenAIProvider(BaseModelProvider):
    """OpenAI model provider."""

    name = "openai"

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str | None = None, **kwargs: Any):
        super().__init__(model_name, api_key, **kwargs)
        self._client: Any = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai

            if self.api_key:
                self._client = openai.OpenAI(api_key=self.api_key)
            else:
                # Try to get API key from environment
                self._client = openai.OpenAI()
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            self._client = None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI API."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an optimization expert. Respond with valid JSON when requested.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=kwargs.get("temperature", self.config.model.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.model.max_tokens),
                timeout=kwargs.get("timeout", self.config.model.timeout),
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Warning: OpenAI generation failed: {e}")
            # Return a fallback response
            if "format" in kwargs and kwargs["format"] == "json":
                return '{"error": "generation_failed", "fallback": true}'
            return f"Error: Generation failed - {str(e)}"

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings using OpenAI API."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
        try:
            response = self._client.embeddings.create(model="text-embedding-3-small", input=text)
            return response.data[0].embedding
        except Exception as e:
            print(f"Warning: OpenAI embedding failed: {e}")
            # Return a fallback embedding
            return [random.random() for _ in range(1536)]


class KimiProvider(BaseModelProvider):
    """Kimi model provider (using OpenAI-compatible API)."""

    name = "kimi"

    def __init__(self, model_name: str = "kimi", api_key: str | None = None, **kwargs: Any):
        super().__init__(model_name, api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.moonshot.cn/v1")
        self._client: Any = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Kimi client."""
        try:
            import openai

            if self.api_key:
                self._client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                # Try to get API key from environment
                api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
                if api_key:
                    self._client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
                else:
                    raise ValueError("No API key provided for Kimi provider")
        except Exception as e:
            print(f"Warning: Failed to initialize Kimi client: {e}")
            self._client = None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Kimi API."""
        if not self._client:
            raise RuntimeError("Kimi client not initialized")
        try:
            # Map Kimi model names to actual model names
            model_mapping = {
                "kimi": "moonshot-v1-8k",
                "kimi-8k": "moonshot-v1-8k",
                "kimi-32k": "moonshot-v1-32k",
                "kimi-128k": "moonshot-v1-128k",
            }
            actual_model = model_mapping.get(self.model_name, self.model_name)
            response = self._client.chat.completions.create(
                model=actual_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an optimization expert. Respond with valid JSON when requested.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=kwargs.get("temperature", self.config.model.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.model.max_tokens),
                timeout=kwargs.get("timeout", self.config.model.timeout),
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Warning: Kimi generation failed: {e}")
            # Return a fallback response
            if "format" in kwargs and kwargs["format"] == "json":
                return '{"error": "generation_failed", "fallback": true}'
            return f"Error: Generation failed - {str(e)}"

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings using Kimi API."""
        if not self._client:
            raise RuntimeError("Kimi client not initialized")
        try:
            response = self._client.embeddings.create(model="moonshot-v1-embedding", input=text)
            return response.data[0].embedding
        except Exception as e:
            print(f"Warning: Kimi embedding failed: {e}")
            # Return a fallback embedding
            return [random.random() for _ in range(1024)]


class MockModelProvider(BaseModelProvider):
    """Mock model provider for testing."""

    name = "mock"

    def __init__(self, model_name: str = "mock-model", api_key: str | None = None, **kwargs: Any):
        # Mock provider works offline, so fall back to a fake key when none supplied.
        super().__init__(model_name, api_key or "mock-key", **kwargs)
        self.call_count = 0

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate mock text response."""
        self.call_count += 1
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.3))
        # Generate different responses based on prompt content
        if "JSON" in prompt or "json" in prompt:
            return self._generate_json_response(prompt, kwargs)
        else:
            return self._generate_text_response(prompt, kwargs)

    def _generate_json_response(self, prompt: str, kwargs: dict[str, Any]) -> str:
        """Generate a JSON response."""
        # Simple heuristic to generate relevant JSON
        if "policy" in prompt.lower():
            return json.dumps(
                {
                    "artifact": f"mock-artifact-{self.call_count}",
                    "temperature": random.uniform(0.1, 1.0),
                    "max_tokens": random.randint(100, 2000),
                    "strategy": random.choice(["few_shot", "zero_shot", "chain_of_thought"]),
                    "confidence": random.uniform(0.5, 0.95),
                }
            )
        elif "optimization" in prompt.lower():
            return json.dumps(
                {
                    "algorithm": random.choice(
                        ["gradient_descent", "genetic", "simulated_annealing"]
                    ),
                    "learning_rate": random.uniform(0.001, 0.1),
                    "iterations": random.randint(10, 100),
                    "convergence_threshold": random.uniform(0.0001, 0.01),
                }
            )
        else:
            return json.dumps(
                {
                    "response": f"Mock response {self.call_count}",
                    "confidence": random.uniform(0.5, 0.95),
                    "timestamp": time.time(),
                }
            )

    def _generate_text_response(self, prompt: str, kwargs: dict[str, Any]) -> str:
        """Generate a text response."""
        responses = [
            "Based on the analysis, I recommend optimizing the following parameters...",
            "The optimal configuration appears to be...",
            "Consider these adjustments for better performance...",
            "The data suggests that...",
            "I would suggest trying...",
        ]
        return random.choice(responses) + f" (Mock response #{self.call_count})"

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate mock embeddings."""
        self.call_count += 1
        # Generate consistent but random embeddings
        embedding_size = kwargs.get("embedding_size", 768)
        # Seed based on text content for consistency
        random.seed(hash(text) % (2**32))
        # Generate embedding with some structure
        embedding = []
        for _ in range(embedding_size):
            # Create a somewhat structured embedding
            base = random.uniform(-1, 1)
            noise = random.gauss(0, 0.1)
            embedding.append(base + noise)
        # Reset seed
        random.seed()
        return embedding


def get_model_provider(
    provider: str = "openai",
    model_name: str | None = None,
    api_key: str | None = None,
    **kwargs: Any,
) -> ModelProvider:
    """
    Get a model provider instance.
    Args:
        provider: Provider name (openai, kimi, mock)
        model_name: Model name to use
        api_key: API key for the provider
        **kwargs: Additional arguments
    Returns:
        Model provider instance
    """
    config = get_config()
    # Use defaults if not provided
    if not model_name:
        model_name = config.model.model_name
    if not api_key:
        api_key = config.model.api_key
    provider_map = {
        "openai": OpenAIProvider,
        "kimi": KimiProvider,
        "mock": MockModelProvider,
    }
    provider_class = provider_map.get(provider.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider}")
    return provider_class(model_name=model_name, api_key=api_key, **kwargs)
