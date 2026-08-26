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


class MembershipSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()  # ✅ HIER!

    class Meta:
        model = TenantMembership
        fields = ["role", "tenant"]


class UserMeSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "memberships",
        ]
