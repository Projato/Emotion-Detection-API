#No complex custom errors yet
class AppError(Exception): 
    """Base application exception."""


class DatabaseConnectionError(AppError): #e.g., mongoclient connection failure
    """Raised when database connection fails."""


class InvalidImageError(AppError):
    """Raised when uploaded image is invalid."""