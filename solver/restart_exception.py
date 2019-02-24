

class RestartException(Exception):

    def __init__(self, message, stats = None, restart = True ):
        super(RestartException, self).__init__(message)
        print(message)
        if (restart):
            print("attempting restart\n")
        self.restart = restart
        self.stats = stats

