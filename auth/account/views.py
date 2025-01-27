from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from account.serializers import *
from account.renderers import UserRenderer


# Create your views here.
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if(serializer.is_valid(raise_exception=True)):
            user=serializer.save()
            token = get_token_for_user(user)
            return Response({'token':token,'msg':'Registration Success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if(serializer.is_valid(raise_exception=True)):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if(user):
                token = get_token_for_user(user)
                return Response({'token':token,'msg':"user logged in successfuly"}, status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':'wrong email or password entered'}}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if(serializer.is_valid(raise_exception=True)):
            return Response({'msg':'password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSendPasswordResetEmail(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request):
        serializer = UserSendPasswordResetEmailSerializer(data=request.data)
        if(serializer.is_valid(raise_exception=True)):
            return Response({'msg':'password reset link sent to your email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        if(serializer.is_valid(raise_exception=True)):
            return Response({'msg':'password Reset Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        


