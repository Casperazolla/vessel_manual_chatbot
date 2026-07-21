from .models import User
from . import helpers


def signup_request(request):
    data       = request.data
    email      = data.get('email', '').strip().lower()
    password   = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name', '').strip()
    role       = data.get('role', 'user')

    error = helpers.validate_required_fields(data, ['email', 'password', 'first_name', 'last_name'])
    if error:
        return error

    if len(password) < 8:
        return 'Password must be at least 8 characters'

    if role not in ['admin', 'user']:
        return 'Invalid role'

    if User.objects.filter(email=email).exists():
        return 'Email already registered'

    otp = helpers.generate_otp()
    helpers.store_otp_in_session(request, 'signup', otp, extra_data={
        'email':      email,
        'password':   password,
        'first_name': first_name,
        'last_name':  last_name,
        'role':       role,
    })
    helpers.send_otp_email(email, otp, 'signup')
    return True


def signup_verify(request):
    data      = request.data
    email     = data.get('email', '').strip().lower()
    otp_input = data.get('otp', '').strip()

    if not email or not otp_input:
        return 'Email and OTP are required'

    error = helpers.verify_otp_from_session(request, 'signup', otp_input)
    if error:
        return error

    session_data = request.session.get('signup')
    if not session_data or session_data.get('email') != email:
        return 'Session expired. Please signup again'

    user = User.objects.create(
        email      = session_data['email'],
        first_name = session_data['first_name'],
        last_name  = session_data['last_name'],
        password   = helpers.hash_password(session_data['password']),
        role       = session_data['role'],
        is_active  = True,
    )

    # clear session
    del request.session['signup']

    tokens = helpers.get_tokens(user)
    return {
        'user': {
            'email':      user.email,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'role':       user.role,
        },
        **tokens
    }


def login(request):
    data     = request.data
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return 'Email and password are required'

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return 'Invalid credentials'

    if not user.is_active:
        return 'Email not verified'

    if not helpers.verify_password(password, user.password):
        return 'Invalid credentials'

    tokens = helpers.get_tokens(user)
    return {
        'user': {
            'email':      user.email,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'role':       user.role,
        },
        **tokens
    }


def forgot_password(request):
    email = request.data.get('email', '').strip().lower()

    if not email:
        return 'Email is required'

    if not User.objects.filter(email=email).exists():
        return 'Email not registered'

    otp = helpers.generate_otp()
    helpers.store_otp_in_session(request, 'forgot_password', otp, extra_data={
        'email': email
    })
    helpers.send_otp_email(email, otp, 'forgot_password')
    return True


def reset_password(request):
    data         = request.data
    email        = data.get('email', '').strip().lower()
    otp_input    = data.get('otp', '').strip()
    new_password = data.get('new_password', '')

    if not all([email, otp_input, new_password]):
        return 'All fields are required'

    if len(new_password) < 8:
        return 'Password must be at least 8 characters'

    error = helpers.verify_otp_from_session(request, 'forgot_password', otp_input)
    if error:
        return error

    session_data = request.session.get('forgot_password')
    if not session_data or session_data.get('email') != email:
        return 'Session expired. Please try again'

    user          = User.objects.get(email=email)
    user.password = helpers.hash_password(new_password)
    user.save()

    # clear session
    del request.session['forgot_password']
    return True


def get_profile(request):
    user = helpers.get_user_from_token(request)
    if not user:
        return 'Invalid or expired token'

    return {
        'email':      user.email,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'role':       user.role,
        'created_at': str(user.created_at),
    }