"""
Base command handler for Z-Library Search Application
"""
from abc import ABC, abstractmethod
from typing import Any
from zlibrary.config import Config


class BaseCommandHandler(ABC):
    """Base class for all command handlers"""
    
    def __init__(self, config: Config):
        self.config = config