from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from . import methods


# ─── PUBLIC ROUTES (no token needed) ─────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def signup_request(request):
    try:
        result = methods.signup_request(request)
        if result is True:
            return Response({'status': 200, 'data': 'OTP sent to your email'}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def signup_verify(request):
    try:
        result = methods.signup_verify(request)
        if isinstance(result, dict):
            return Response({'status': 200, 'data': result}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def login(request):
    try:
        result = methods.login(request)
        if isinstance(result, dict):
            return Response({'status': 200, 'data': result}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def forgot_password(request):
    try:
        result = methods.forgot_password(request)
        if result is True:
            return Response({'status': 200, 'data': 'OTP sent to your email'}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def reset_password(request):
    try:
        result = methods.reset_password(request)
        if result is True:
            return Response({'status': 200, 'data': 'Password reset successful'}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)


# ─── PROTECTED ROUTES (JWT token required) ────────────────────────────────────

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_profile(request):
    try:
        result = methods.get_profile(request)
        if isinstance(result, dict):
            return Response({'status': 200, 'data': result}, status=200)
        return Response({'status': 400, 'data': result}, status=400)
    except Exception as e:
        return Response({'status': 500, 'message': str(e)}, status=500)
    

@api_view(['GET'])
def test(request):
    return Response({'status': 200, 'data': 'This is api is working'}, status=200)