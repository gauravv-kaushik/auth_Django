from rest_framework import serializers
from account.models import MyUser
from account.utils import Util
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 =  serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = ['email','name','dob','password','password2']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    
    def validate(self, data):
        if(data['password']!=data['password2']):
            raise serializers.ValidationError("Both Password must be same")
        return data

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = MyUser
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id','email','name','dob']

class UserChangePasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=255,style={'input_type':'password'}, write_only=True)
    new_password2 = serializers.CharField(max_length=255,style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['new_password1','new_password2']
    
    def validate(self, data):
        user = self.context.get('user')
        if(data['new_password1']!=data['new_password2']):
            raise serializers.ValidationError("both password must be same")
        user.set_password(data['new_password1'])
        user.save()
        return data

class UserSendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    class Meta:
        fields = ['email']
    
    def validate(self, data):
        if MyUser.objects.filter(email=data['email']).exists():
            user = MyUser.objects.get(email=data['email'])
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset-password/'+uid+'/'+token
            print("link",link)
            body = "Click this link to reset your password "+link
            content = {
                'subject':'Reset Your Password',
                'body': body,
                'to_email':user.email
            }
            Util.send_email(content)
            return data
        else:
            raise serializers.ValidationError("You're not a registered user")

class UserPasswordResetSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=255,style={'input_type':'password'}, write_only=True)
    new_password2 = serializers.CharField(max_length=255,style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['new_password1','new_password2']
    
    def validate(self, data):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            if(data['new_password1']!=data['new_password2']):
                raise serializers.ValidationError("both password must be same")
            
            id = smart_str(urlsafe_base64_decode(uid))
            user = MyUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or Expired')
            user.set_password(data['new_password1'])
            user.save()
            return data
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or Expired')
