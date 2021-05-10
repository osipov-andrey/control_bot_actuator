class HTTPClientConnectException(Exception):
    pass


class BadCommandTemplateException(Exception):
    def __init__(self, file_name=""):
        self.file_name = file_name


class NotEnoughArgumentsError(Exception):
    def __init__(self, missing_args: list):
        self.missing_args = missing_args


class UserException(Exception):
    """
    Дает понять, что дальнейшая обработка
    исключения библиотекой не требуется
    """

    pass


class BadEvent(Exception):
    def __init__(self, event_body, bad_field):
        self.event_body = event_body
        self.bad_filed = bad_field
