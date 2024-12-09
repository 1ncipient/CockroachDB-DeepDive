import json
import time
from datetime import datetime
from typing import Dict, Any, List

class QueryExporter:
    def __init__(self, output_file: str = "query_history.json"):
        self.output_file = output_file
        self.query_history: List[Dict[str, Any]] = []
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing data from the JSON file if it exists."""
        try:
            with open(f"./perf_log/{self.output_file}", 'r') as f:
                self.query_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.query_history = []

    def add_query(self, statement: str, query_time: str, result_count: int, sql_explanation: str):
        """
        Add a new query entry to the history.
        
        Args:
            statement (str): The SQL statement that was executed
            result_count (int): Number of results returned
            sql_explanation (str): The explanation provided by the database
        """
        query_data = {
            "timestamp": datetime.now().isoformat(),
            "statement": statement,
            "query_time": query_time,
            "result_count": result_count,
            "sql_explanation": sql_explanation
        }
        self.query_history.append(query_data)
        self._save_to_file()

    def _save_to_file(self):
        """Save the current query history to the JSON file."""
        with open(f"./perf_log/{self.output_file}", 'w') as f:
            json.dump(self.query_history, f, indent=2)

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the complete query history."""
        return self.query_history

    def clear_history(self):
        """Clear the query history."""
        self.query_history = []
        self._save_to_file()

query_exporter = QueryExporter(output_file="postgres_query_history.json")