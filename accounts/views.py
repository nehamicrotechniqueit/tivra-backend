# accounts/views.py
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

# 🔍 Validation Utility Functions
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    # केवल 10 अंकों का नंबर स्वीकार करेगा
    pattern = r'^\d{10}$'
    return re.match(pattern, phone)

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        company_name = data.get('company_name', '').strip()
        
        # 🚨 1. Mandatory Fields Check
        if not email or not password or not full_name:
            return Response({'error': 'Full Name, Email, and Password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 🚨 2. Strict Email Validation
        if not is_valid_email(email):
            return Response({'error': 'Invalid email format. Please enter a valid business email (e.g., name@domain.com).'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 🚨 3. Strict Phone Validation (Optional field but if provided, must be 10 digits)
        if phone_number and not is_valid_phone(phone_number):
            return Response({'error': 'Invalid Phone Number. It must contain exactly 10 digits.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 🚨 4. Password Strength
        if len(password) < 8:
            return Response({'error': 'Password security too weak. Minimum 8 characters required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(email=email).exists():
            return Response({'error': 'A workspace already exists with this email address.'}, status=status.HTTP_400_BAD_REQUEST)
        
        role = 'admin' if User.objects.count() == 0 else 'user'

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name,
                phone=phone_number,
                company_name=company_name,
                role=role
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {'id': user.id, 'email': user.email, 'full_name': user.first_name, 'role': user.role}
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'Server Execution Failure: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        
        if not email or not password:
            return Response({'error': 'Email and password are required fields.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not is_valid_email(email):
            return Response({'error': 'Please enter a valid email format to proceed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No workspace found with this email. Please Register first.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Access Denied. Invalid or incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'error': 'This workspace terminal has been suspended.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {'id': user.id, 'email': user.email, 'full_name': user.first_name, 'role': getattr(user, 'role', 'user')}
        }, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email or not is_valid_email(email):
            return Response({'error': 'A valid registered email address is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # सुरक्षा कारणों से प्रोफेशनल एप्स 400 या 200 ही देते हैं ताकि हैकर्स को पता न चले कौन सा ईमेल रजिस्टर्ड है, 
            # लेकिन आपके डिबग के लिए हम एरर दे रहे हैं:
            return Response({'error': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)
            
        # 🛡️ सुरक्षित टोकन और UID जनरेशन
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # 🔗 Next.js का पासवर्ड रीसेट पेज लिंक
        reset_link = f"http://localhost:3000/reset-password?uid={uid}&token={token}"
        
        # 📧 ईमेल भेजने का असली प्रोफेशनल फॉर्मेट
        subject = "TIVRA CRM - Secure Password Reset Request"
        message = f"Hello {user.first_name},\n\nWe received a request to reset your TIVRA CRM terminal password. Click the link below to configure a new password:\n\n{reset_link}\n\nIf you did not make this request, please ignore this email secure terminal.\n\nRegards,\nTeam TIVRA AI"
        
        try:
            send_mail(subject, message, None, [email], fail_silently=False)
            return Response({'success': True, 'message': 'Password recovery token dispatched safely to your email.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Email Service Failure: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# accounts/views.py के अंदर केवल ResetPasswordConfirmView को इससे बदलें:

class ResetPasswordConfirmView(APIView):
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password', '').strip()
        
        # टर्मिनल में डिबग करने के लिए प्रिंट स्टेटमेंट
        print(f"--- Reset Request Received --- UID: {uid}, Token: {token}")

        if not uid or not token or not new_password:
            return Response({'error': 'Secure parameters missing.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. UID को सही से डिकोड करना
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"Decoding Error: {str(e)}")
            return Response({'error': 'Invalid or corrupted reset link.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. टोकन वैलिडेशन चेक
        if not default_token_generator.check_token(user, token):
            print("Token Validation Failed: Token might be expired or already used.")
            return Response({'error': 'Reset token expired or already used. Please request a new link.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 3. 🔒 पासवर्ड को सेट और हैश करना
            user.set_password(new_password)
            user.save()
            print(f"Password successfully changed for user: {user.email}")
            return Response({'success': True, 'message': 'Password updated successfully. You can now login.'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Database Save Error: {str(e)}")
            return Response({'error': 'Failed to update database record.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)