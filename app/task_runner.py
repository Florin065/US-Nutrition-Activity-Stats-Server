"""Module to run tasks in parallel using a thread pool."""

import multiprocessing
from queue import Queue
from threading import Event, Thread
import json
import os

class ThreadPool:
    """Thread pool to run tasks in parallel."""
    def __init__(self):
        """Initialize the thread pool."""
        self.shutdown_event = Event()
        self.task_queue = Queue()
        self.job_status = {}
        self.init_task_runners()

        os.makedirs("data/jobs", exist_ok=True)

    def init_task_runners(self):
        """Initialize the task runners."""
        num_threads = self.get_num_of_threads()
        self.task_runners = [TaskRunner(
            self.task_queue, self.shutdown_event, self.job_status) for _ in range(num_threads)]
        for task_runner in self.task_runners:
            task_runner.start()

    def get_num_of_threads(self) -> int:
        """Get the number of threads to use for the thread pool."""
        default_num_of_threads = max(multiprocessing.cpu_count() - 1, 1)
        num_of_threads = os.environ.get("TP_NUM_OF_THREADS")

        if num_of_threads:
            try:
                num_of_threads = int(num_of_threads)
                if num_of_threads > 0:
                    return num_of_threads
            except ValueError:
                pass

        return default_num_of_threads

    def add_job(self, operation, *args):
        """Add a job to the task queue."""
        if self.shutdown_event.is_set():
            return None

        job_id = self.task_queue.qsize()
        self.task_queue.put((operation, args, job_id))
        self.job_status[job_id] = "queued"

        return job_id

    def get_job(self, job_id):
        """Get the status of a job."""
        status = self.job_status.get(job_id)
        if status == "queued":
            return {"status": "queued"}
        elif status == "running":
            return {"status": "running"}

        path = f"data/jobs/{job_id}.json"
        if not os.path.exists(path):
            return {"status": "error", "reason": "Invalid job_id"}
        return json.load(open(path, "r", encoding='utf-8'))

    def graceful_shutdown(self):
        """Gracefully shutdown the thread pool."""
        self.shutdown_event.set()

        for task_runner in self.task_runners:
            task_runner.join()

class TaskRunner(Thread):
    """Thread to run tasks from the task queue."""
    def __init__(self, task_queue, shutdown_event, job_status):
        """Initialize the task runner."""
        super().__init__()
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.job_status = job_status

    def run(self):
        """Run tasks from the task queue."""
        while not self.shutdown_event.is_set():
            try:
                task, args, job_id = self.task_queue.get(timeout=1)
            except: # pylint: disable=bare-except
                continue

            self.job_status[job_id] = "running"

            result = task(*args)
            self.save_result(job_id, result)

            self.job_status.pop(job_id, None)
            self.task_queue.task_done()

    def save_result(self, job_id, result):
        """Save the result of a job to a file."""
        with open(f"data/jobs/{job_id}.json", "w", encoding='utf-8') as f:
            json.dump({"status": "done", "data": result}, f)
