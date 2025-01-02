from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request


class IsAdminOrReadOnly(BasePermission):
    """
    Only admin users can create/update/delete books
    All users (even unauthenticated ones) should be able to list books
    """
    def has_permission(
            self,
            request: Request,
            view: object) -> bool:
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
            )
            or (request.user and request.user.is_staff)
        )
