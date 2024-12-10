from django.test import TestCase

# Create your tests here.
# remember_me = request.POST.get('remember_me')  # This will return either 'on' or None
# user = authenticate(request, username=username, password=password)

# if user is not None:
#     login(request, user)
#     if remember_me:
#         request.session.set_expiry(1209600)  # 2 weeks, for example
#     return redirect('home')