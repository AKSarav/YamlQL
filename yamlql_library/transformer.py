import pandas as pd
import copy
from typing import Any, Dict, List, Tuple

class DataTransformer:
    """Transforms nested dictionary data into relational tables."""

    def __init__(self, data: Dict[str, Any]):
        """Initializes the DataTransformer with the data to be transformed."""
        self.data = data

    def _find_nested_lists(self, d: Dict, path: List[str] = []) -> List[List[str]]:
        """Recursively finds paths to all nested lists of objects."""
        paths = []
        for k, v in d.items():
            current_path = path + [k]
            if isinstance(v, list) and v and isinstance(v[0], dict):
                paths.append(current_path)
            elif isinstance(v, dict):
                paths.extend(self._find_nested_lists(v, current_path))
        return paths

    def _normalize_records(self, table_name: str, records: List[Dict]) -> List[Tuple[str, pd.DataFrame]]:
        """Handles the complex normalization of a list of dictionary objects."""
        if not records:
            return []

        tables = []
        nested_list_paths = self._find_nested_lists(records[0])
        
        # Determine the top-level scalar/simple fields to use as metadata for joins
        meta_cols = [k for k, v in records[0].items() if not isinstance(v, (dict, list))]

        # Create a separate table for each nested list found
        for path in nested_list_paths:
            nested_table_name = f"{table_name}_{'_'.join(path)}"
            child_df = pd.json_normalize(
                records,
                record_path=path,
                meta=meta_cols,
                sep='_',
                errors='ignore',
                meta_prefix=f"{table_name}_"
            )
            child_df.columns = [c.replace(' ', '_').replace('.', '_') for c in child_df.columns]
            tables.append((nested_table_name, child_df))

        # Create the parent table by flattening everything first...
        parent_df = pd.json_normalize(records, sep='_')
        parent_df.columns = [c.replace(' ', '_').replace('.', '_') for c in parent_df.columns]
        
        # ...then dropping the columns that were extracted into separate tables.
        cols_to_drop = []
        for path in nested_list_paths:
            col_name = '_'.join(path)
            if col_name in parent_df.columns:
                cols_to_drop.append(col_name)
        
        parent_df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        
        # Only add the parent table if it's not empty after the nested lists were removed.
        if not parent_df.empty and parent_df.shape[1] > 0:
            tables.append((table_name, parent_df))
        
        return tables

    def transform(self) -> List[Tuple[str, pd.DataFrame]]:
        """
        Transforms the dictionary data into a list of named DataFrames.
        - If there are fewer than three root keys, the children of the single root key are used as tables.
        - Otherwise, top-level keys are used as tables.
        """
        tables = []
        data_copy = copy.deepcopy(self.data)

        # Heuristic: If there are fewer than three top-level keys,
        # assume the user wants to treat the keys of the inner dict as tables.
        top_level_keys = list(data_copy.keys())
        if len(top_level_keys) < 3 and isinstance(data_copy[top_level_keys[0]], dict):
            source_data = data_copy[top_level_keys[0]]
        else:
            source_data = data_copy

        for table_name, value in source_data.items():
            if isinstance(value, dict) and len(value) > 1:
                # Create a separate table for each child if there are multiple children
                for child_name, child_value in value.items():
                    if isinstance(child_value, dict) or isinstance(child_value, list):
                        tables.extend(self._normalize_records(f"{table_name}_{child_name}", [child_value]))
            elif isinstance(value, list) and value:
                # Check if it's a list of objects or a list of scalars
                if all(isinstance(item, dict) for item in value):
                    tables.extend(self._normalize_records(table_name, value))
                elif all(not isinstance(item, (dict, list)) for item in value):
                    # It's a list of simple scalars, create a single-column DataFrame
                    df = pd.DataFrame({table_name: value})
                    df.columns = [c.replace(' ', '_').replace('.', '_') for c in df.columns]
                    tables.append((table_name, df))
                # Otherwise, it's a mixed or unsupported list type, so we ignore it.
            elif isinstance(value, dict):
                tables.extend(self._normalize_records(table_name, [value]))
            
        return tables 