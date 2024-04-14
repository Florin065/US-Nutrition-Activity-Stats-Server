Nume: Subțirică Florin-Ioan
Grupă: 332CD

<div align="center"><img src="https://media.tenor.com/Zf45U-rHMgkAAAAC/friday-good-morning.gif" width="300px"></div>

# Tema 1 US-Nutrition-Activity-Stats-Server

## Overview
This Flask web server project is designed to ingest data from a CSV file containing nutrition and activity statistics in the USA. It provides endpoints to perform various calculations and analyses on the data.

## General Approach
The project follows a modular approach, with separate modules for data ingestion, task running, calculations, and defining routes. Flask is used as the web framework for its simplicity and flexibility.

## Organization
- **Initialization**: The Flask app is initialized in `__init__.py`. Data ingestion and task running are set up here.
- **Data Ingestion**: The `DataIngestor` class in `app/data_ingestor.py` loads data from the CSV file and prepares it for analysis.
- **Task Running**: The `ThreadPool` class in `app/task_runner.py` manages the execution of tasks in parallel using a thread pool.
- **Calculations**: Helper functions for data analysis are defined in `app/helper.py`.
- **Routes**: Endpoints for interacting with the server are defined in `app/routes.py`.

## Implementation

My implementation does not contain unittests.

Besides the initial skeleton of the homework, I chose to add `app/helper.py' in which I define a Helper class that DataIngestor inherits, thus having access to all the variables and methods/functions of the parent.
I did this because I didn't want to clutter up the endpoints in `app/routes.py', so you can understand the code much better.

For example:

``` python
    @webserver.route('/api/state_mean', methods=['POST'])
    def state_mean_request():
        """Get the mean for a question in a state."""
        question = request.get_json()["question"]
        state = request.get_json()["state"]

        def op(data_ingestor, question, state):
            return {state: data_ingestor.state_mean(question, state)}

        return dummy_state(op, question, state)
```

in the code above, i get the mean for a question in a state. Basically, what I do there is that I take the data from the request, that is, the question and the state for which I am asked to calculate the mean, after which I create the operation that will be executed further in the task runner. Thus, after creating the operation, I call the method dummy_state(op, question, state).

To add a job in thread pool and return the job id (as well as not to write the same code every time), I created two dummy methods that receive the operation and the question or the operation, the question and the state:

``` python
def dummy_state(op, question, state):
    """Run an operation on a question and state."""
    job_id = webserver.tasks_runner.add_job(op, webserver.data_ingestor, question, state)

    return jsonify({"job_id": job_id})

def dummy_question(op, question):
    """Run an operation on a question."""
    job_id = webserver.tasks_runner.add_job(op, webserver.data_ingestor, question)

    return jsonify({"job_id": job_id})
```

The `ThreadPool` class facilitates the management of a pool of threads for concurrent task execution. Upon initialization, it sets up essential components such as an event for signaling shutdown, a task queue, and a dictionary to track job statuses. It dynamically creates and starts individual task runner threads based on system resources or an environment variable. Jobs are added to the task queue, and their statuses are tracked as they progress. The class also provides methods for retrieving job statuses and gracefully shutting down the thread pool when necessary.

The `TaskRunner` class represents a thread responsible for executing tasks from the task queue within the thread pool. During initialization, it receives essential parameters such as the task queue, shutdown event, and job status dictionary. The run method continuously retrieves tasks from the task queue, executes them, and saves the results to JSON files named after the job IDs. To prevent race conditions, it checks for calls to graceful_shutdown, ensuring orderly termination of tasks and thread operations. This proactive approach enhances thread safety and maintains the integrity of task execution within the thread pool.


## Git
https://github.com/Florin065/US-Nutrition-Activity-Stats-Server
