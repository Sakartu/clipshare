from threading import Timer, Event, Thread
import time
class InfiniteTimer(Thread):
    '''
    A class, extending Timer, which behaves just like threading.Timer,
    but instead of returning after the call is completed, it starts
    the timer again.
    '''

    def __init__(self, interval, function, args=[], kwargs={}, immediate=False):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.immediate = immediate

    def run(self):
        if self.immediate:
            self.function(*self.args, **self.kwargs)

        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)

    def cancel(self):
        self.finished.set()
        
