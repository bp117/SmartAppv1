import json

def parse_json_content(json_string):
    """Parses a JSON string and extracts the content value.

    Args:
        json_string: The JSON string to parse.

    Returns:
        The content value from the JSON string, or None if it cannot be extracted.
    """

    try:
        data = json.loads(json_string)
        if 'choices' in data and isinstance(data['choices'], list) and len(data['choices']) > 0:
            choice = data['choices'][0]
            if 'message' in choice and isinstance(choice['message'], dict) and 'content' in choice['message']:
                return choice['message']['content']
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return None

# Example usage:
json_string = '{"choices": [{"finish_reason": "stop", "index": 0, "logprobs": None, "message": {"content": "The capital of India is New Delhi.", "role": "assistant"}}], "created": 1728917016, "id": "2024-10-14 07:43:36.993018-07)44.14.0)-201175817", "model": "meta/llama-3.2-90b-vision-instruct-mags", "object": "chat.completion", "system_fingerprint": "", "usage": {"completion_tokens": 8, "prompt_tokens": 7, "total_tokens": 15}}'

content = parse_json_content(json_string)
print(content)  # Output: The capital of India is New Delhi.

