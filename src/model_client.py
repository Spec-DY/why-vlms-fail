"""
Model client interfaces for querying VLMs
"""

from abc import ABC, abstractmethod
from typing import Optional
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelClient(ABC):
    """Base class for model clients"""

    def __init__(self, model_name: str = "test_model"):
        self.model_name = model_name

    @abstractmethod
    def query(self, prompt: str, image_path: str) -> str:
        """
        Query the model with text and image

        Args:
            prompt: Text prompt
            image_path: Path to image file

        Returns:
            Model response as string
        """
        pass


class DummyModelClient(ModelClient):
    """Dummy model client for testing the framework"""

    def __init__(self):
        super().__init__(model_name="dummy_model")

    def query(self, prompt: str, image_path: str) -> str:
        """Return random answer for testing"""
        import random
        answers = ["yes", "no", "unknown"]
        return random.choice(answers)


class NovitaModelClient(ModelClient):
    """Novita AI model client using OpenAI-compatible API with default settings"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs  # Accept any additional parameters
    ):
        """
        Initialize Novita AI client with minimal configuration

        Args:
            api_key: Novita API key (if None, reads from NOVITA_API_KEY env var)
            base_url: API base URL (if None, reads from NOVITA_BASE_URL env var)
            model_name: Model name (if None, reads from NOVITA_MODEL env var)
            **kwargs: Any additional parameters to pass to the API
                     (e.g., temperature, max_tokens, stream, etc.)
        """
        # Get configuration from env vars if not provided
        self.api_key = api_key or os.getenv("NOVITA_API_KEY")
        self.base_url = base_url or os.getenv(
            "NOVITA_BASE_URL", "https://api.novita.ai/openai")
        model = model_name or os.getenv(
            "NOVITA_MODEL", "qwen/qwen3-vl-30b-a3b-thinking")

        if not self.api_key:
            raise ValueError(
                "Novita API key not found. Please set NOVITA_API_KEY environment variable "
                "or pass api_key parameter."
            )

        super().__init__(model_name=model)

        # Store any additional parameters
        self.extra_params = kwargs

        # Initialize OpenAI client with Novita's base URL
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            print(f"✓ Novita client initialized")
            print(f"  Model: {self.model_name}")
            if self.extra_params:
                print(f"  Extra params: {self.extra_params}")
        except ImportError:
            raise ImportError(
                "openai package is required. Install it with: pip install 'openai>=1.0.0'"
            )

    def query(self, prompt: str, image_path: str) -> str:
        """
        Call Novita AI API with image using default settings

        Args:
            prompt: Text prompt
            image_path: Path to image file

        Returns:
            Model response
        """
        # Read and encode image as base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # Determine image media type
        if image_path.lower().endswith('.png'):
            media_type = "image/png"
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        else:
            media_type = "image/png"  # default

        # Construct data URL
        image_url = f"data:{media_type};base64,{image_data}"

        try:
            # Prepare base parameters
            params = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            # Add any extra parameters if provided
            params.update(self.extra_params)

            # Call API
            chat_completion_res = self.client.chat.completions.create(**params)

            # Handle streaming vs non-streaming responses
            if self.extra_params.get('stream', False):
                # Collect streamed response
                response_text = ""
                for chunk in chat_completion_res:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                return response_text
            else:
                # Return non-streaming response
                return chat_completion_res.choices[0].message.content

        except Exception as e:
            raise Exception(f"Novita API call failed: {str(e)}")


class ClaudeModelClient(ModelClient):
    """Claude model client using Anthropic API"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model_name: Claude model name
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        super().__init__(model_name=model_name)
        self.api_key = api_key

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install it with: pip install anthropic"
            )

    def query(self, prompt: str, image_path: str) -> str:
        """Call Claude API with image"""
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.standard_b64encode(
                image_file.read()).decode("utf-8")

        # Determine image type
        if image_path.lower().endswith('.png'):
            media_type = "image/png"
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        else:
            media_type = "image/png"

        # Call API
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        return message.content[0].text
