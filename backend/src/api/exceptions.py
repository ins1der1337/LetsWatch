from fastapi import status


class AppException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class TooEarlyException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_425_TOO_EARLY)
