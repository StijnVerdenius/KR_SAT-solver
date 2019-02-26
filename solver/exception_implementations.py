
class RunningTimeException(Exception):
    """
    Exception that is used to cancel some run on purpose without crashing
    """
    pass



class RestartException(Exception):

    """
    Exception that is used to trigger a restart
    """

    def __init__(self, message, stats = None, restart = True, elapsed_runtime = 0 ):
        super(RestartException, self).__init__(message)
        print(message)
        if (restart):
            print("attempting restart\n")
        self.restart = restart
        self.stats = stats
        self.runtime = elapsed_runtime

