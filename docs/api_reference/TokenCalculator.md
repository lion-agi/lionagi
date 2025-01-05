# Token Calculator API Reference

## Overview

The Token Calculator module calculates and tracks token usage in LLM requests, handling text, images, and embeddings.

## Constants

```python
GPT4O_IMAGE_PRICING = {
    "base_cost": 85,      # Base tokens for any image
    "low_detail": 0,      # Additional cost for low detail
    "max_dimension": 2048,  # Maximum image dimension
    "min_side": 768,      # Minimum side length
    "tile_size": 512,     # Size of each tile
    "tile_cost": 170,     # Tokens per tile
}

GPT4O_MINI_IMAGE_PRICING = {
    "base_cost": 2833,
    "tile_cost": 5667
}

O1_IMAGE_PRICING = {
    "base_cost": 75,
    "tile_cost": 150
}
```

## TokenCalculator Class

*class* `TokenCalculator`

```python
@staticmethod
def calculate_message_tokens(
    messages: list[dict],
    /,
    **kwargs
) -> int:
    """Calculate total tokens for chat messages.
    
    Args:
        messages: List of message dictionaries
        **kwargs: Additional options (model, encoding)
    
    Returns:
        int: Total token count including base tokens, content, and images
    """

@staticmethod
def calcualte_embed_token(
    inputs: list[str],
    /,
    **kwargs
) -> int:
    """Calculate tokens for embedding requests.
    
    Args:
        inputs: List of strings to embed
        **kwargs: Additional options (model, encoding)
    
    Returns:
        int: Total token count
    """

@staticmethod
def tokenize(
    s_: str = None,
    /,
    encoding_name: str | None = None,
    tokenizer: Callable | None = None,
    return_tokens: bool = False,
) -> int | list[int]:
    """Convert text to tokens or count.
    
    Args:
        s_: Input text
        encoding_name: Name of tiktoken encoding
        tokenizer: Optional custom tokenizer
        return_tokens: Whether to return token list
    
    Returns:
        int | list[int]: Token count or list
    """
```

## Utility Functions

```python
def get_encoding_name(value: str) -> str:
    """Get tiktoken encoding for model.
    
    Args:
        value: Model name or encoding identifier
        
    Returns:
        str: Encoding name (model-specific, base, or fallback)
    """

def calculate_image_token_usage_from_base64(
    image_base64: str,
    detail: str,
    image_pricing: dict
) -> int:
    """Calculate token usage for base64 images.
    
    Args:
        image_base64: Base64 encoded image
        detail: Detail level ('low', 'high', 'auto')
        image_pricing: Pricing configuration
        
    Returns:
        int: Total token cost
    """
```
