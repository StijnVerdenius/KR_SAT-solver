

class RestartException(Exception):

    def __init__(self, message, restart = True ):
        super(RestartException, self).__init__(message)
        print(message)
        self.restart = restart

