from fastapi import status


class AppException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class TooEarlyException(AppException):
    def __init__(self, message: str = "Too early request"):
        super().__init__(message, status_code=status.HTTP_425_TOO_EARLY)


class UnavailableServiceException(AppException):
    def __init__(self, message: str = "Unavailable Service"):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
