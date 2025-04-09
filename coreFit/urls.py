from django.urls import path
from .views import (SignupView, LoginApiView, LogoutView,
    MembershipPlanViewSet, MembershipViewSet, PaymentViewSet, MembershipStatusView, verify_payment
)




urlpatterns = [
    path("register/", SignupView.as_view()),
    path("login/", LoginApiView.as_view()),
    path("logout/", LogoutView.as_view()),
    path('membership-plans/', MembershipPlanViewSet.as_view({'get': 'list', 'post': 'create'}), name='membershipplan-list'),
    path('membership-plans/<int:pk>/', MembershipPlanViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='membershipplan-detail'),
    path('memberships/', MembershipViewSet.as_view({'get': 'list', 'post': 'create'}), name='membership-list'),
    path('memberships/<int:pk>/', MembershipViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='membership-detail'),
    path('payments/', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path("payments/verify/", verify_payment, name="verify_payment"),
    path('payments/<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='payment-detail'),
    path("membership-status/", MembershipStatusView.as_view(), name="membership-status"),
]