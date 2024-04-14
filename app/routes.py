"""Module to define the routes for the webserver."""

from app import webserver
from flask import request, jsonify


def dummy_state(op, question, state):
    """Run an operation on a question and state."""
    job_id = webserver.tasks_runner.add_job(op, webserver.data_ingestor, question, state)
    return jsonify({"job_id": job_id})

def dummy_question(op, question):
    """Run an operation on a question."""
    job_id = webserver.tasks_runner.add_job(op, webserver.data_ingestor, question)
    return jsonify({"job_id": job_id})


@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """Get the results of a job."""
    return webserver.tasks_runner.get_job(int(job_id))


@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get the status of all jobs."""

    def get_job_status(tasks_runner):
        results = []
        num_jobs = tasks_runner.task_queue.qsize()
        for i in range(num_jobs):
            results.append({"status": tasks_runner.get_job(i)["status"]})
        return results

    job_id = webserver.tasks_runner.add_job(get_job_status, webserver.tasks_runner)

    result = wait_for_job_completion(webserver.tasks_runner, job_id)
    return result

def wait_for_job_completion(tasks_runner, job_id):
    """Wait for a job to finish and return the result."""
    result = tasks_runner.get_job(job_id)
    while result["status"] == "running":
        result = tasks_runner.get_job(job_id)
    return result


@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs():
    """Get the number of jobs currently running."""
    return str(len([job_id for job_id, status
                    in webserver.tasks_runner.job_status.items() if status == "running"]))


@webserver.route('/api/graceful_shutdown', methods=['GET'])
def get_graceful_shutdown():
    """Gracefully shutdown the webserver."""
    webserver.tasks_runner.graceful_shutdown()
    return ""


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """Get the mean for a question in a state."""
    question = request.get_json()["question"]
    state = request.get_json()["state"]

    def op(data_ingestor, question, state):
        return {state: data_ingestor.state_mean(question, state)}

    return dummy_state(op, question, state)


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """Get the mean for a question in all states."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return dict(data_ingestor.states_mean(question))

    return dummy_question(op, question)


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """Get the top 5 states with the highest mean for a question."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return dict(data_ingestor.top5(question, True))

    return dummy_question(op, question)


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """Get the top 5 states with the lowest mean for a question."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return dict(data_ingestor.top5(question, False))

    return dummy_question(op, question)


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """Get the global mean for a question."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return {"global_mean": data_ingestor.global_mean(question)}

    return dummy_question(op, question)


@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """Get the difference between the global mean and the state mean for a question."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return data_ingestor.diff_from_mean(question)

    return dummy_question(op, question)


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """Get the difference between the global mean and the state mean for a question."""
    question = request.get_json()["question"]
    state = request.get_json()["state"]

    def op(data_ingestor, question, state):
        return {state: data_ingestor.state_diff_from_mean(question, state)}

    return dummy_state(op, question, state)


@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """Get the mean for a question in all states by category."""
    question = request.get_json()["question"]

    def op(data_ingestor, question):
        return data_ingestor.mean_by_category(question)

    return dummy_question(op, question)


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """Get the mean for a question in a state by category."""
    question = request.get_json()["question"]
    state = request.get_json()["state"]

    def op(data_ingestor, question, state):
        return {state: data_ingestor.state_mean_by_category(question, state)}

    return dummy_state(op, question, state)


# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """Display the available routes."""
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg


def get_defined_routes():
    """Return the defined routes."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
