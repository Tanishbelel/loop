from rest_framework import permissions

class IsProjectManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PROJECT_MANAGER'

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'EMPLOYEE'

class IsOwnerOrProjectManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'PROJECT_MANAGER':
            return True
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        return False
