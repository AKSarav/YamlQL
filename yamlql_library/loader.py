import yaml
from pathlib import Path
from typing import Any, Dict
import re

class YamlLoader:
    """Loads content from a YAML file, with support for multi-document streams."""

    def __init__(self, file_path: Path):
        """
        Initializes the YamlLoader with the path to the YAML file.

        Args:
            file_path: The path to the YAML file.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} was not found.")
        self.file_path = file_path

    def load(self) -> Dict[str, Any]:
        """
        Loads YAML content from the file. If it's a multi-document file
        (separated by '---'), it merges all documents into a single dictionary.

        Returns:
            A dictionary representing the (potentially merged) YAML content.
        """
        with open(self.file_path, 'r') as f:
            content = f.read()

        # Pre-process the content to handle common multi-document formatting issues
        # Replace '------' with '---' and ensure separators are on their own lines
        processed_content = re.sub(r'^\s*-{3,}\s*$', '---', content, flags=re.MULTILINE)

        # Use safe_load_all to handle multi-document YAML files
        documents = list(yaml.safe_load_all(processed_content))

        if not documents:
            return {}
        
        if len(documents) == 1:
            return documents[0]
        
        # Merge all documents into one. This assumes keys are unique across documents
        # or that later documents are intended to override earlier ones.
        merged_data = {}
        for doc in documents:
            if isinstance(doc, dict):
                merged_data.update(doc)
        
        return merged_data

def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    A convenience function to load a YAML file.

    Args:
        file_path: The path to the YAML file as a string.

    Returns:
        A dictionary representing the YAML content.
    """
    return YamlLoader(Path(file_path)).load() 