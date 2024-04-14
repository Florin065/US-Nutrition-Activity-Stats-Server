"""Module to perform calculations on data."""

from collections import defaultdict
from operator import itemgetter
import pandas as pd

class Helper:
    """Class to perform calculations on data."""
    def __init__(self, csv_path):
        """Initialize Helper class with csv_path."""
        self.csv_path = csv_path
        self.states = set()
        self.categories = {}
        self.data = None

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]
        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]


    def load_data(self):
        """Load data from csv file into memory."""
        data_file = pd.read_csv(self.csv_path, encoding='utf-8')

        self.states.update(data_file['LocationDesc'].unique())

        for _, row in data_file.iterrows():
            category = row["StratificationCategory1"]
            segment = row["Stratification1"]
            if category not in self.categories:
                self.categories[category] = set()
            elif segment not in self.categories[category]:
                self.categories[category].add(segment)

        self.data = data_file.to_dict('records')


    def filter_rows(self, conditions, rows):
        """Filter rows based on conditions."""
        selected_rows = []
        conditions_items = conditions.items()

        for row in rows:
            if all(row[column] == value for column, value in conditions_items):
                selected_rows.append(row)
        return selected_rows


    def calculate_mean(self, columns, rows):
        """Calculate the mean of the selected rows."""
        selected_values = []
        count = 0
        columns_items = columns.items()

        for row in rows:
            if all(row[col] == value for col, value in columns_items):
                selected_values.append(float(row["Data_Value"]))
                count += 1

        return sum(selected_values) / count if count else 0


    def all_states_mean(self, question: str):
        """Calculate the mean for a question in all states."""
        return {state: val for state in self.states for val in
                [self.state_mean(question, state)] if val}


    def global_mean(self, question: str):
        """Calculate the global mean for a question."""
        return self.calculate_mean({"Question": question}, self.data)

    def state_mean(self, question: str, state: str):
        """Calculate the mean for a question in a state."""
        return self.calculate_mean({"Question": question, "LocationDesc": state}, self.data)

    def states_mean(self, question: str, key=itemgetter(1)):
        """Calculate the mean for a question in all states and sort by key."""
        all_states_mean_items = self.all_states_mean(question).items()

        return sorted(all_states_mean_items, key=key)

    def diff_from_mean(self, question: str):
        """Calculate the difference between the global mean and the state mean for a question."""
        global_mean = self.global_mean(question)
        all_states_mean_items = self.all_states_mean(question).items()

        return {state: global_mean - all_states_mean
                for state, all_states_mean in all_states_mean_items}

    def state_diff_from_mean(self, question: str, state: str):
        """Calculate the difference between the global mean and the state mean for a question."""
        return self.global_mean(question) - self.state_mean(question, state)

    def top5(self, question: str, best: bool = True):
        """Return the top 5 states with the highest or lowest mean for a question."""
        results = self.states_mean(question)
        if best:
            questions_to_check = self.questions_best_is_max
        else:
            questions_to_check = self.questions_best_is_min

        if question in questions_to_check:
            return results[-5:]
        return results[:5]

    def mean_by_category_helper(self, state, result, state_rows, ok=True):
        """Helper function to calculate the mean by category."""
        categories_items = self.categories.items()

        for key, value in categories_items:
            category_rows = self.filter_rows({"StratificationCategory1": key}, state_rows)
            for segment in value:
                mean = self.calculate_mean({"Stratification1": segment}, category_rows)
                if mean > 0:
                    if not ok:
                        tuple_key = (key, segment)
                    else:
                        tuple_key = (state, key, segment)
                    result[str(tuple_key)] = mean

    def mean_by_category(self, question: str):
        """Calculate the mean for a question in all states by category."""
        result = defaultdict(float)
        rows = self.filter_rows({"Question": question}, self.data)

        for state in self.states:
            state_rows = self.filter_rows({"LocationDesc": state}, rows)
            self.mean_by_category_helper(state, result, state_rows)

        return result

    def state_mean_by_category(self, question: str, state: str):
        """Calculate the mean for a question in a state by category."""
        result = defaultdict(float)
        rows = self.filter_rows({"Question": question, "LocationDesc": state}, self.data)

        self.mean_by_category_helper(state, result, rows, False)

        return result
