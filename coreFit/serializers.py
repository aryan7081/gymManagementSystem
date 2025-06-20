from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth import authenticate
from .models import CustomUser, MembershipPlan, Membership, Payment

UserModel = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only = True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    def validate_email(self, value):
        if UserModel.objects.filter(email = value).exists():
            raise serializers.ValidationError("A user with this email already exist")
        return value

    def create(self, validated_data):
        email = validated_data.get("email")
        full_name = validated_data.get("full_name", "")
        profile_photo = validated_data.get("profile_photo", None)
        if not email:
            raise serializers.ValidationError({"message": "Email is required."})
        username_base = slugify(email.split('@')[0])
        user = UserModel.objects.create_user(
            email = email,
            username = username_base,
            password=validated_data['password'],
            full_name=full_name,
            profile_photo=profile_photo 
        )
        return user
    class Meta:
        model = UserModel
        fields = ("id", "email", "password", "full_name", "profile_photo")

    def to_representation(self, instance):
        """
        Customize error representation for email and password fields
        to return them as strings instead of arrays.
        """
        representation = super().to_representation(instance)
        errors = self.errors
        if errors:
            formatted_errors = {}
            for field, error in errors.items():
                formatted_errors[field] = ', '.join(error)  # Join errors as a string
            return {"message": "Validation failed", "errors": formatted_errors}
        return representation

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only= True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username = email, password = password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data["user"] = user
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Must include email and password")
        
        return data
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'full_name', 'contact_number']

class MembershipPlanSerializer(serializers.ModelSerializer):
    features = serializers.StringRelatedField(many=True)
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'price', 'duration', 'description', 'popular', 'features']

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    price = serializers.DecimalField(source="plan.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'user_email', 'plan', 'plan_name', 'price', 'start_date', 'end_date', 'is_active']


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    membership_plan = serializers.CharField(source="membership.plan.name", read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")])

    class Meta:
        model = Payment
        fields = ['id', 'user_email', 'membership', 'membership_plan', 'amount', 'transaction_id', 'status', 'payment_method', 'created_at']

