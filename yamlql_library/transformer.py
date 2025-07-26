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

    def _process_node(self, node_value: Any, table_name: str, tables_list: List, depth: int = 0):
        """Recursively processes a node to create tables with universal heuristics."""
        table_name = str(table_name).replace('-', '_')
        
        # Universal configuration - no domain-specific keywords
        MAX_DEPTH = 5  # Reasonable depth limit to handle nesting without going overboard
        MIN_DICT_SIZE_FOR_TABLE = 2  # Only create separate tables for dictionaries with 2+ keys
        
        # Check if we should stop recursing based on universal criteria
        should_stop_recursing = depth >= MAX_DEPTH

        if isinstance(node_value, list):
            if not node_value: return
            if all(isinstance(item, dict) for item in node_value):
                # Always use _normalize_records for lists of objects to get proper flattening
                tables_list.extend(self._normalize_records(table_name, node_value))
            elif all(not isinstance(item, (dict, list)) for item in node_value):
                df = pd.DataFrame({'value': [str(x) for x in node_value]})
                tables_list.append((table_name, df))
        
        elif isinstance(node_value, dict):
            scalar_data = {}
            nested_dicts = {}

            for key, value in node_value.items():
                if isinstance(value, dict):
                    # Only create separate tables for dictionaries that are large enough
                    # and we haven't hit the depth limit
                    if len(value) >= MIN_DICT_SIZE_FOR_TABLE and not should_stop_recursing:
                        nested_dicts[key] = value
                    # ALWAYS add a flattened version to preserve all data
                    for sub_key, sub_value in value.items():
                        if not isinstance(sub_value, (dict, list)):
                            scalar_data[f"{key}_{sub_key}"] = sub_value
                        elif isinstance(sub_value, list) and all(not isinstance(item, (dict, list)) for item in sub_value):
                            # Flatten scalar lists
                            scalar_data[f"{key}_{sub_key}"] = sub_value
                elif isinstance(value, list):
                    # Handle lists within dictionaries
                    self._process_node(value, f"{table_name}_{key}", tables_list, depth + 1)
                else:
                    scalar_data[key] = value

            if scalar_data:
                tables_list.extend(self._normalize_records(table_name, [scalar_data]))

            # Process nested dictionaries that qualified for their own tables
            for child_name, child_value in nested_dicts.items():
                new_table_name = f"{table_name}_{child_name}"
                self._process_node(child_value, new_table_name, tables_list, depth + 1)

    def transform(self) -> List[Tuple[str, pd.DataFrame]]:
        """
        Transforms the YAML data into a list of relational tables by recursively
        processing the data structure with smart stopping conditions.
        """
        all_tables = []
        data_copy = copy.deepcopy(self.data)

        # Handle root-level list first
        if isinstance(data_copy, list):
            self._process_node(data_copy, 'root', all_tables, depth=0)
            return all_tables

        # Heuristic: If there is only one top-level key and its value is a dictionary
        # (e.g., a single document wrapper), step inside it for a more intuitive schema.
        top_level_keys = list(data_copy.keys())
        if len(top_level_keys) == 1 and isinstance(data_copy[top_level_keys[0]], dict):
            source_data = data_copy[top_level_keys[0]]
        else:
            source_data = data_copy

        if isinstance(source_data, dict):
            # Check if this is a "record-like" dictionary (only scalar values)
            # If so, treat it as a single record for a table
            has_only_scalars = all(not isinstance(v, (dict, list)) for v in source_data.values())
            
            if has_only_scalars:
                # This is a single record - create a table with one row
                all_tables.extend(self._normalize_records('data', [source_data]))
            else:
                # This has nested structures - process each item separately
                for table_name, value in source_data.items():
                    self._process_node(value, table_name, all_tables, depth=0)
        elif isinstance(source_data, list):
            self._process_node(source_data, 'root', all_tables, depth=0)

        return all_tables 