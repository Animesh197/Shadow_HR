"""
Retry Handler

Handles LLM extraction retries when responses are invalid.
"""

import json
from pydantic import ValidationError


MAX_RETRIES = 2


def extract_with_retry(extract_func, text, schema_validator=None):
    """
    Execute LLM extraction with retry logic.
    
    Args:
        extract_func: Function to call for extraction (e.g., extract_experience)
        text: Input text to extract from
        schema_validator: Optional Pydantic model to validate response
    
    Returns:
        dict: Extracted data or empty structure on failure
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Call extraction function
            result = extract_func(text)
            
            # Validate structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            # If schema validator provided, validate
            if schema_validator:
                # Try to validate each entry
                if "experience" in result:
                    validated = []
                    for entry in result["experience"]:
                        try:
                            schema_validator(**entry)
                            validated.append(entry)
                        except ValidationError as e:
                            print(f"[retry_handler] Validation failed for entry: {e}")
                            continue
                    result["experience"] = validated
                
                elif "education" in result:
                    validated = []
                    for entry in result["education"]:
                        try:
                            schema_validator(**entry)
                            validated.append(entry)
                        except ValidationError as e:
                            print(f"[retry_handler] Validation failed for entry: {e}")
                            continue
                    result["education"] = validated
            
            return result
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[retry_handler] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            
            if attempt < MAX_RETRIES:
                print(f"[retry_handler] Retrying with corrective prompt...")
                # For retry, we could modify the prompt, but since our extract_func
                # doesn't support that, we'll just retry with same input
                continue
            else:
                print(f"[retry_handler] All retries exhausted, returning empty result")
                # Return empty structure based on what was being extracted
                if hasattr(extract_func, '__name__'):
                    if 'experience' in extract_func.__name__:
                        return {"experience": []}
                    elif 'education' in extract_func.__name__:
                        return {"education": []}
                    elif 'header' in extract_func.__name__:
                        return {"headline": "", "location": ""}
                
                return {}
    
    return {}
