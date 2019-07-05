import logging
import queue
from logging.handlers import QueueHandler, QueueListener

class sfLogger:

    def __init__(self):

        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)

        self.logger = logging.getLogger()
        self.logger.addHandler(self.queue_handler)
        self.logger.setLevel(logging.INFO)

        self.listener = QueueListener(self.log_queue, self.queue_handler)
        self.listener.start()
        
        
    def logprint(self):
        print (self.log_queue.get())