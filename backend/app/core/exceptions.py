class DomainException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(DomainException):
    pass


class ConflictError(DomainException):
    pass


class ValidationError(DomainException):
    pass


class AuthError(DomainException):
    pass


class UnprocessableEntityError(DomainException):
    pass


class NotAuthenticatedError(AuthError):
    def __init__(
        self,
        message: str = "Authentication required",
    ):
        super().__init__(message)


class AlreadyAuthenticatedError(AuthError):
    def __init__(
        self,
        message: str = "Already authenticated",
    ):
        super().__init__(message)


class InvalidCredentialsError(AuthError):
    def __init__(
        self,
        message: str = "Incorrect credentials",
    ):
        super().__init__(message)


class InvalidTokenError(AuthError):
    def __init__(
        self,
        message: str = "Invalid or expired token",
    ):
        super().__init__(message)


class AccountNotVerifiedError(AuthError):
    def __init__(
        self,
        message: str = "Account is not verified",
    ):
        super().__init__(message)


class UserNotFoundError(NotFoundError):
    def __init__(
        self,
        message: str = "User not found",
    ):
        super().__init__(message)


class QuizNotFoundError(NotFoundError):
    def __init__(
        self,
        message: str = "Quiz not found",
    ):
        super().__init__(message)


class RoomNotFoundError(NotFoundError):
    def __init__(
        self,
        message: str = "Room not found",
    ):
        super().__init__(message)


class SessionNotFoundError(NotFoundError):
    def __init__(
        self,
        message: str = "Session not found",
    ):
        super().__init__(message)


class SessionMemberNotFoundError(NotFoundError):
    def __init__(
        self,
        message: str = "Member not found for this session",
    ):
        super().__init__(message)


class UserAlreadyExistsError(ConflictError):
    def __init__(
        self,
        message: str = "User already exists",
    ):
        super().__init__(message)


class AccountAlreadyVerifiedError(ConflictError):
    def __init__(
        self,
        message: str = "Account is already verified",
    ):
        super().__init__(message)


class SessionInvalidStateError(ValidationError):
    def __init__(
        self,
        message: str = "Invalid session state",
    ):
        super().__init__(message)
