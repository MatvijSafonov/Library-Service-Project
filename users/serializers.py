from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "is_staff")
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def create(self, validated_data: dict) -> User:
        """Create a new User instance with encrypted password and return it."""
        return User.objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        """Update a User instance with encrypted password and return it."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
