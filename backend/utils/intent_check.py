# utils/intent_check.py

def is_prompt_unclear(prompt: str) -> bool:
    """
    Detects whether the user prompt is too vague to act on.
    Useful for catching unclear references like 'that' or 'do it'.
    """
    vague_terms = [
        "that", "this", "it", "thing", "stuff", 
        "handle that", "do it", "take care of it", "whatever"
    ]
    words = prompt.strip().split()
    low_word_count = len(words) < 3
    vague_language = any(term in prompt.lower() for term in vague_terms)
    return low_word_count or vague_language
