from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth import authenticate
from .models import CustomUser, MembershipPlan, Membership, Payment

UserModel = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only = True, min_length=8)
    def validate_email(self, value):
        if UserModel.objects.filter(email = value).exists():
            raise serializers.ValidationError("A user with this email already exist")
        return value

    def create(self, validated_data):
        print("ye dekho: ", validated_data)
        email = validated_data.get("email")
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        username_base = slugify(email.split('@')[0])
        user = UserModel.objects.create_user(
            email = email,
            username = username_base,
            password=validated_data['password']
        )
        return user
    class Meta:
        model = UserModel
        fields = ("id", "email", "password")

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
    class Meta:
        model = MembershipPlan
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = MembershipPlanSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    membership = MembershipSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
