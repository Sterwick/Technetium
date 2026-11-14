
class CoreError(Exception):
    pass


class RequestParseError(CoreError):
    pass


class ResponseParseError(CoreError):
    pass


class MetadataError(CoreError):
    pass
