import multiprocessing
from queue import Queue
from threading import Event, Thread
import json
import os

class ThreadPool:
    def __init__(self):
        self.shutdown_event = Event()
        self.task_queue = Queue()
        self.job_status = {}
        self.init_task_runners()

        os.makedirs("data/jobs", exist_ok=True)

    def init_task_runners(self):
        num_threads = self.get_num_of_threads()
        self.taskRunners = [TaskRunner(self.task_queue, self.shutdown_event, self.job_status) for _ in range(num_threads)]
        for taskRunner in self.taskRunners:
            taskRunner.start()

    def get_num_of_threads(self) -> int:
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
        if self.shutdown_event.is_set():
            return None

        job_id = self.task_queue.qsize()
        self.task_queue.put((operation, args, job_id))
        self.job_status[job_id] = "queued"

        return job_id

    def get_job(self, jobId):
        status = self.job_status.get(jobId)
        if status == "queued":
            return {"status": "queued"}
        elif status == "running":
            return {"status": "running"}
        
        path = f"data/jobs/{jobId}.json"
        if not os.path.exists(path):
            return {"status": "error", "reason": "Invalid job_id"}
        return json.load(open(path, "r"))

    def graceful_shutdown(self):
        self.shutdown_event.set()
        
        for taskRunner in self.taskRunners:
            taskRunner.join()

class TaskRunner(Thread):
    def __init__(self, task_queue, shutdown_event, job_status):
        super().__init__()
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.job_status = job_status

    def run(self):
        while not self.shutdown_event.is_set():
            try:
                task, args, jobId = self.task_queue.get(timeout=1)
            except:
                continue

            self.job_status[jobId] = "running"

            result = task(*args)
            self.save_result(jobId, result)

            del self.job_status[jobId]
            self.task_queue.task_done()

    def save_result(self, job_id, result):
        with open(f"data/jobs/{job_id}.json", "w") as f:
            json.dump({"status": "done", "data": result}, f)
