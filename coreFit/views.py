from django.shortcuts import render
from .models import CustomUser
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import MembershipPlan, Membership, Payment
from .serializers import MembershipPlanSerializer, MembershipSerializer, PaymentSerializer
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.utils.timezone import now  # To handle datetime operations
from datetime import timedelta  # To calculate membership duration

from rest_framework import viewsets, status  # DRF viewsets & status codes
from rest_framework.response import Response  # DRF response handling
from rest_framework.permissions import IsAuthenticated 
import uuid

class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    def create(self, request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "email": user.email,
                "name": user.full_name,
                "message": "User created successfully"
            }, status=status.HTTP_200_OK)
        errors = serializer.errors
        formatted_errors = {}

        # Format each field error as a string
        for field, error_messages in errors.items():
            formatted_errors[field] = ' '.join(error_messages)

        return Response({
            "message": "Validation failed",
            "errors": formatted_errors  # Send the errors as strings
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginApiView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "name": user.full_name,
                "email": user.email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        request.auth.delete() 
        return Response({"message": "Logged out successfully"}, status=200)

# ✅ Membership Plan Viewset (CRUD)
class MembershipPlanViewSet(viewsets.ModelViewSet):
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer

# ✅ User Membership Viewset (Subscribe, Renew)
class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        plan_id = request.data.get("plan_id")

        try:
            plan = MembershipPlan.objects.get(id=plan_id)
        except MembershipPlan.DoesNotExist:
            return Response({"error": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already has a membership
        membership, created = Membership.objects.get_or_create(user=user, defaults={
            "plan": plan,
            "start_date": now().date(),
            "end_date": now().date() + timedelta(days=plan.get_duration_days()),
            "is_active": True
        })

        if not created:
            # Extend existing membership
            membership.plan = plan
            membership.end_date += timedelta(days=plan.get_duration_days())
            membership.is_active = True
            membership.save()

        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

# ✅ Payment Viewset (Track Transactions)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        membership_id = request.data.get("membership_id")
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")
        
        try:
            membership = Membership.objects.get(id=membership_id, user=user)
        except Membership.DoesNotExist:
            return Response({"error": "Invalid membership"}, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = str(uuid.uuid4())
        payment = Payment.objects.create(
            user=user,
            membership=membership,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status="success"
        )
        membership.is_active = True
        membership.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    

class MembershipStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        membership = Membership.objects.filter(user=user, is_active=True).first()

        if membership:
            return Response({
                "has_membership": True,
                "membership_plan": membership.plan.name,
                "start_date": membership.start_date,
                "end_date": membership.end_date,
                "is_active": membership.is_active
            }, status=status.HTTP_200_OK)
        else:
            return Response({"has_membership": False, "message": "No active membership found."}, status=status.HTTP_200_OK)
