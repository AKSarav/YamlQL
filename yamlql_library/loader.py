import yaml
from pathlib import Path
from typing import Any, Dict

class YamlLoader:
    """Loads content from a YAML file."""

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
        Loads the YAML content from the file.

        Returns:
            A dictionary representing the YAML content.
        """
        with open(self.file_path, 'r') as f:
            return yaml.safe_load(f)

def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    A convenience function to load a YAML file.

    Args:
        file_path: The path to the YAML file as a string.

    Returns:
        A dictionary representing the YAML content.
    """
    return YamlLoader(Path(file_path)).load() 