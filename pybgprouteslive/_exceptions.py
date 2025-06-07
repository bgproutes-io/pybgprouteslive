

class PybgproutesliveError(Exception):
    pass


class WebsocketConnectionError(PybgproutesliveError):
    pass


class PrefixToAPIKeyError(PybgproutesliveError):
    pass
