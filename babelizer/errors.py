class BabelizeError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class ValidationError(BabelizeError):

    pass


class RenderError(BabelizeError):

    pass


class OutputDirExistsError(BabelizeError):

    pass
