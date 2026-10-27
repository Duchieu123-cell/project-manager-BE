class AppException(Exception):
    status_code = 500
    error_code = "APP_ERROR"
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EmailExistsError(AppException):
    status_code = 400
    error_code = "EMAIL_EXISTS"

class UnauthorizedError(AppException):
    status_code = 401

class ExpiredAccessTokenError(UnauthorizedError):
    error_code = "EXPIRED_ACCESS_TOKEN"
    
class ExpiredRefreshTokenError(UnauthorizedError):
    error_code = "EXPIRED_REFRESH_TOKEN"

class NoAccessTokenError(UnauthorizedError):
    error_code = "NO_ACCESS_TOKEN"
    
class NoRefreshTokenError(UnauthorizedError):
    error_code = "NO_REFRESH_TOKEN"
    
class InvalidCredentialsError(UnauthorizedError):
    error_code = "INVALID_CREDENTIALS"
    
class InvalidAccessTokenError(UnauthorizedError):
    error_code = "INVALID_ACCESS_TOKEN"    
    
class InvalidRefreshTokenError(UnauthorizedError):
    error_code = "INVALID_REFRESH_TOKEN"
    
class ReusedRefreshTokenError(UnauthorizedError):
    error_code = "REUSED_REFRESH_TOKEN"
    
class ForbiddenError(AppException):
    status_code = 403
    error_code = "FORBIDDEN"

class EntityNotFoundError(AppException):
    status_code = 404
    error_code = "ENTITY_NOT_FOUND"