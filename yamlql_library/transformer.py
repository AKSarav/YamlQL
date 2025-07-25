import pandas as pd
import copy
from typing import Any, Dict, List, Tuple

class DataTransformer:
    """Transforms nested dictionary data into relational tables."""

    def __init__(self, data: Dict[str, Any]):
        """Initializes the DataTransformer with the data to be transformed."""
        self.data = data

    def _find_and_extract_nested_lists(self, records: List[Dict], parent_table_name: str) -> Tuple[List[Dict], List[Tuple[str, pd.DataFrame]]]:
        """
        Finds lists of objects within a list of records, extracts them into new tables,
        and returns the original records with the extracted lists removed.
        """
        if not records:
            return records, []

        new_tables = []
        # Find all paths to nested lists of objects in the first record as a template
        paths_to_extract = []
        
        def find_paths(d, path=[]):
            for k, v in d.items():
                current_path = path + [k]
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    paths_to_extract.append(current_path)
                elif isinstance(v, dict):
                    find_paths(v, current_path)
        
        find_paths(records[0])

        # For each path, create a new table from the nested lists across all records
        for path in paths_to_extract:
            nested_table_name = f"{parent_table_name}_{'_'.join(path)}".replace('-', '_')
            
            # Extract parent metadata for joining
            meta_cols = [k for k, v in records[0].items() if not isinstance(v, (dict, list))]
            
            child_df = pd.json_normalize(
                records,
                record_path=path,
                meta=meta_cols,
                sep='_',
                errors='ignore',
                meta_prefix=f"{parent_table_name}_"
            )
            child_df.columns = [c.replace(' ', '_').replace('.', '_').replace('-', '_') for c in child_df.columns]
            new_tables.append((nested_table_name, child_df))

        # Create a deepcopy of the records to modify them by removing extracted lists
        records_copy = copy.deepcopy(records)
        for record in records_copy:
            for path in paths_to_extract:
                d = record
                for key in path[:-1]:
                    d = d.get(key, {})
                # Pop the list from the dictionary
                if path[-1] in d:
                    d.pop(path[-1])
                    
        return records_copy, new_tables

    def _stringify_scalar_lists(self, data: Any) -> Any:
        """Recursively traverses data to convert all lists of scalars into lists of strings."""
        if isinstance(data, dict):
            return {k: self._stringify_scalar_lists(v) for k, v in data.items()}
        if isinstance(data, list):
            is_scalar_list = all(not isinstance(item, (dict, list)) for item in data)
            if is_scalar_list:
                return [str(item) for item in data]
            else:
                return [self._stringify_scalar_lists(item) for item in data]
        return data

    def _normalize_records(self, table_name: str, records: List[Dict]) -> List[Tuple[str, pd.DataFrame]]:
        """
        Normalizes a list of records into a primary DataFrame and extracts nested
        lists of objects into their own separate tables.
        """
        if not records:
            return []

        # Ensure all scalar lists are stringified before any processing
        records = self._stringify_scalar_lists(records)
        
        # Extract nested lists of objects into their own tables first
        records_without_nested_lists, extracted_tables = self._find_and_extract_nested_lists(records, table_name)
        
        # Flatten the remaining records (which now contain only scalars, dicts, and scalar lists)
        parent_df = pd.json_normalize(records_without_nested_lists, sep='_')
        parent_df.columns = [c.replace(' ', '_').replace('.', '_').replace('-', '_') for c in parent_df.columns]
        
        all_tables = []
        if not parent_df.empty:
            all_tables.append((table_name, parent_df))
        
        all_tables.extend(extracted_tables)
        return all_tables

    def transform(self) -> List[Tuple[str, pd.DataFrame]]:
        """
        Transforms the YAML data into a list of relational tables based on a simple,
        predictable set of rules.
        """
        tables = []
        data_copy = copy.deepcopy(self.data)

        # Rule 1: If the root is a list, treat it as a single table named 'root'.
        if isinstance(data_copy, list):
            if not data_copy:
                return []
            if all(isinstance(item, dict) for item in data_copy):
                return self._normalize_records('root', data_copy)
            elif all(not isinstance(item, (dict, list)) for item in data_copy):
                value_as_str = [str(x) for x in data_copy]
                df = pd.DataFrame({'value': value_as_str})
                return [('root', df)]
            else:
                return [] # Ignore mixed-content root lists

        # Heuristic: If there is only one top-level key and its value is a dictionary
        # (e.g., a single document wrapper), step inside it for a more intuitive schema.
        top_level_keys = list(data_copy.keys())
        if len(top_level_keys) == 1 and isinstance(data_copy[top_level_keys[0]], dict):
            source_data = data_copy[top_level_keys[0]]
        else:
            source_data = data_copy

        # Rule 2: Each key in the source data becomes a table.
        for table_name, value in source_data.items():
            table_name = str(table_name).replace('-', '_')
            
            if isinstance(value, list) and value:
                if all(isinstance(item, dict) for item in value): # List of objects
                    tables.extend(self._normalize_records(table_name, value))
                elif all(not isinstance(item, (dict, list)) for item in value): # List of scalars
                    value_as_str = [str(x) for x in value]
                    df = pd.DataFrame({'value': value_as_str})
                    tables.append((table_name, df))
            elif isinstance(value, dict): # A single object
                # Heuristic: If a dictionary's values are all themselves dictionaries,
                # create a separate table for each child dictionary.
                is_collection_of_objects = value and all(isinstance(v, dict) for v in value.values())
                
                if is_collection_of_objects:
                    for child_name, child_value in value.items():
                        new_table_name = f"{table_name}_{child_name}".replace('-', '_')
                        tables.extend(self._normalize_records(new_table_name, [child_value]))
                else:
                    # It's a regular object to be flattened into a single-row table.
                    tables.extend(self._normalize_records(table_name, [value]))
            
        return tables 