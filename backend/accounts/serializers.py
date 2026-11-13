from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "email", "roles", "is_staff", "is_superuser", "is_active")

    def get_name(self, user):
        return user.get_full_name() or user.email

    def get_roles(self, user):
        roles = list(user.groups.values_list("name", flat=True))
        if user.is_superuser:
            roles.append("superuser")
        if user.is_staff:
            roles.append("staff")
            if "admin" not in roles:
                roles.append("admin")
        # de-dupe while preserving order
        seen = set()
        deduped = []
        for role in roles:
            if role and role not in seen:
                seen.add(role)
                deduped.append(role)
        return deduped or ["user"]


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters."
            )
        return value

    def create(self, validated_data):
        name = validated_data.pop("name")
        first_name, _, last_name = name.strip().partition(" ")
        email = validated_data["email"]
        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
