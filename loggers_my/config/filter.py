import logging


class InfoFilter(logging.Filter):
    """
    Simple Filter class
    """
    def __init__(self):
        super().__init__(name='filter_info_logs')

    def filter(self, record):
        """
        Return Log Record Object based on condition - Return only INFO logs

        :param record: Log Record Object
        :return: Log Record Object
        """
        assert isinstance(record, logging.LogRecord)
        if record.levelno == logging.INFO:
            return record


class WarningFilter(logging.Filter):
    """
    Simple Filter class
    """
    def __init__(self):
        super().__init__(name='filter_warning_logs')

    def filter(self, record):
        """
        Return Log Record Object based on condition - Return only WARNING logs

        :param record: Log Record Object
        :return: Log Record Object
        """
        assert isinstance(record, logging.LogRecord)
        if record.levelno == logging.WARNING:
            return record


class DebugFilter(logging.Filter):
    """
    Simple Filter class
    """
    def __init__(self):
        super().__init__(name='filter_debug_logs')

    def filter(self, record):
        """
        Return Log Record Object based on condition - Return only DEBUG logs

        :param record: Log Record Object
        :return: Log Record Object
        """
        assert isinstance(record, logging.LogRecord)
        if record.levelno == logging.DEBUG:
            return record
