#########################
# accounts/serializers.py
#########################

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import TenantMembership
from core.models import Tenant
User = get_user_model()


class TokenByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Ungültige Zugangsdaten.")

        if not user.check_password(password):
            raise serializers.ValidationError("Ungültige Zugangsdaten.")

        if not user.is_active:
            raise serializers.ValidationError("User ist deaktiviert.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
            },
        }

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "theme"]


from accounts.permissions import ROLE_PERMISSIONS


class MembershipSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = TenantMembership
        fields = ["role", "role_display", "permissions", "tenant"]

    def get_permissions(self, obj):
        return ROLE_PERMISSIONS.get(obj.role, [])


class UserMeSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(
        many=True,
        read_only=True
    )
    is_pro = serializers.SerializerMethodField()
    is_platform_admin = serializers.BooleanField(read_only=True)
    is_finance_admin = serializers.BooleanField(read_only=True)
    is_global_user_admin = serializers.BooleanField(read_only=True)
    is_platform_helpdesk = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_staff",
            "is_superuser",
            "platform_role",
            "is_platform_admin",
            "is_finance_admin",
            "is_global_user_admin",
            "is_platform_helpdesk",
            "is_pro",
            "memberships",
        ]

    def get_is_pro(self, obj):
        try:
            return bool(hasattr(obj, "ems_subscription") and obj.ems_subscription.is_pro_active)
        except Exception:
            return False


