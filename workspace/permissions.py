from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_perfil == 'ADMIN'


class IsLider(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_perfil in ['ADMIN', 'LIDER']


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.tipo_perfil == 'ADMIN'


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.tipo_perfil == 'ADMIN':
            return True
        return obj.usuario == request.user