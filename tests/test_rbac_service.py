"""Tests for RBACService."""

from app.core.domain.models.permission import Permission
from app.core.services.rbac_service import RBACService


class TestRBACService:
    def test_has_permission_admin_product_delete(self):
        assert RBACService.has_permission("admin", Permission.PRODUCT_DELETE) is True

    def test_has_permission_user_product_view(self):
        assert RBACService.has_permission("user", Permission.PRODUCT_VIEW) is True

    def test_has_permission_user_product_delete(self):
        assert RBACService.has_permission("user", Permission.PRODUCT_DELETE) is False

    def test_has_permission_guest_login(self):
        assert RBACService.has_permission("guest", Permission.USER_LOGIN) is True

    def test_has_permission_guest_product_view(self):
        assert RBACService.has_permission("guest", Permission.PRODUCT_VIEW) is False

    def test_has_permission_unknown_role(self):
        assert RBACService.has_permission("nonexistent", Permission.PRODUCT_VIEW) is False

    def test_has_any_permission_true(self):
        result = RBACService.has_any_permission("user", [
            Permission.PRODUCT_DELETE,
            Permission.PRODUCT_VIEW,
        ])
        assert result is True

    def test_has_any_permission_false(self):
        result = RBACService.has_any_permission("user", [
            Permission.PRODUCT_DELETE,
            Permission.USER_LIST,
        ])
        assert result is False

    def test_get_role_permissions_admin(self):
        perms = RBACService.get_role_permissions("admin")
        assert Permission.PRODUCT_DELETE in perms
        assert Permission.WAREHOUSE_DELETE in perms

    def test_get_role_permissions_unknown(self):
        assert RBACService.get_role_permissions("nonexistent") == []
