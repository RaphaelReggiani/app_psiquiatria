class UserDomainException(Exception):
    """Base exception for user domain."""
    pass


class InvalidRoleAssignment(UserDomainException):
    pass


class UnauthorizedRoleChange(UserDomainException):
    pass


class AuthenticationFailed(UserDomainException):
    pass


class EmailAlreadyExists(UserDomainException):
    pass
