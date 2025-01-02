from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    """
    Only admin users can create/update/delete books
    All users (even unauthenticated ones) should be able to list books
    """
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        elif request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return request.user.is_authenticated and request.user.is_staff
        return False


# class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         return bool(
#             (
#                 request.method in SAFE_METHODS
#                 and request.user
#                 and request.user.is_authenticated
#             )
#             or (request.user and request.user.is_staff)
#         )
