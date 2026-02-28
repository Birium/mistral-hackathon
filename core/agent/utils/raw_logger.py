"""
Object Logger
Logs all requests and streaming events to disk for debugging and analysis
"""

import json
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from typing import List, Union, Any


def get_current_timezone_time() -> datetime:
    """Get current time with timezone information"""
    return datetime.now().astimezone()


class ObjectLogger:
    """
    Logger that captures all objects and events during agent execution
    
    This logger:
    - Records input objects (requests, messages, etc.)
    - Records all streaming events (raw chunks)
    - Saves everything to timestamped folders
    - Helps with debugging and analysis
    """
    
    def __init__(self, path: str = "./logs/raw_requests"):
        """
        Initialize the logger
        
        Args:
            path: Base path for log files
        """
        self.save_folder = Path(path)
        self.save_folder.mkdir(parents=True, exist_ok=True)
        self.objects: List[Union[BaseModel, Any]] = []
        self.response_events: List[str] = []
    
    def log_object(self, obj: Union[BaseModel, Any]):
        """
        Log an object (will be saved as JSON)
        
        Args:
            obj: Any object (preferably Pydantic model or dict)
        """
        self.objects.append(obj)
    
    def log_event(self, event_json: str):
        """
        Log a streaming event
        
        Args:
            event_json: JSON string representing an event
        """
        self.response_events.append(event_json)
    
    def save(self):
        """
        Save all logged objects and events to disk
        
        Creates a timestamped folder with:
        - object_N.json files for each logged object
        - events.jsonl file with all streaming events (one per line)
        """
        if not self.objects and not self.response_events:
            return
        
        # Create timestamped folder
        now = get_current_timezone_time()
        timestamp = now.strftime("%m-%d-%H-%M-%S")
        log_folder = self.save_folder / f"request_{timestamp}"
        log_folder.mkdir(parents=True, exist_ok=True)
        
        # Save each object
        for i, obj in enumerate(self.objects, 1):
            object_file = log_folder / f"object_{i}.json"
            with object_file.open('w', encoding='utf-8') as f:
                if isinstance(obj, BaseModel):
                    json.dump(obj.model_dump(), f, indent=2)
                else:
                    json.dump(obj, f, indent=2)
        
        # Save all events as JSONL (one JSON per line)
        if self.response_events:
            response_file = log_folder / "raw_chunks.jsonl"
            with response_file.open('w', encoding='utf-8') as f:
                for event in self.response_events:
                    f.write(event + "\n")
        
        # Clear for next request
        self.objects = []
        self.response_events = []
        
        print(f"\n[DEBUG] Raw stream logs saved to {log_folder}", flush=True)


# Global instance for easy import
object_logger = ObjectLogger(path="./logs/raw_requests")