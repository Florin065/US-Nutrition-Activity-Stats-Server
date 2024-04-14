"""Module to load data from csv file and perform calculations."""

from collections import defaultdict

from app.helper import Helper

class DataIngestor(Helper):
    """Class to load data from csv file and perform calculations."""
    def __init__(self, csv_path: str):
        """Initialize the data ingestor."""
        self.states = set()
        self.categories = defaultdict(set)
        self.data = []
        self.csv_path = csv_path

        

        self.load_data()
