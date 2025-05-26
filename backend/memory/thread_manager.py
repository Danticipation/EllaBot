from typing import List, Dict
from datetime import datetime

class ThreadMemory:
    """
    Manages conversation thread memory with a fixed-size message history.

    Attributes:
        messages: List of message dictionaries containing author, message, and timestamp.
        max_messages: Maximum number of messages to keep in memory.
    """

    def __init__(self, max_messages: int = 10):
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add(self, author: str, message: str) -> None:
        """Store a new message with a timestamp in memory."""
        self.messages.append({
            "author": author,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def clear(self) -> None:
        """Clear all stored messages."""
        self.messages.clear()

    def get_messages(self) -> List[Dict[str, str]]:
        """Retrieve a copy of all stored messages."""
        return self.messages.copy()
