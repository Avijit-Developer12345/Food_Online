from django.shortcuts import render, redirect
from vender.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied

# Restrict the user from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restricte the Customer from accessing the Veddor page

def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


# ================= REGISTER USER =================
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already registered!')
        return redirect('myAccount')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():

            user = User.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            user.role = User.CUSTOMER
            user.save()

            messages.success(request, 'Your account has been registered successfully!')
            return redirect('login')

        else:
            print(form.errors)

    else:
        form = UserForm()

    return render(request, 'accounts/registerUser.html', {'form': form})


# ================= REGISTER VENDOR =================
def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')

    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid():  # ✅ FIXED

            user = User.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user

            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile

            vendor.save()

            messages.success(request, 'Vendor registered successfully! Please wait for approval.')
            return redirect('login')

        else:
            print(form.errors)
            print(v_form.errors)

    else:
        form = UserForm()
        v_form = VendorForm()

    return render(request, 'accounts/registerVendor.html', {
        'form': form,
        'v_form': v_form
    })


# ================= LOGIN =================
def login(request):
    if request.user.is_authenticated:
        return redirect('myAccount')

    if request.method == 'POST':
        username = request.POST.get('email')   # using email as username
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)  # ✅ FIXED

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')


# ================= LOGOUT =================
def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


# ================= MY ACCOUNT =================
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)

    if redirectUrl:
        return redirect(redirectUrl)
    
    return render(request, 'accounts/myAccount.html')  # ✅ STOP LOOP

# ================= CUSTOMER DASHBOARD =================
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html')


# ================= VENDOR DASHBOARD =================
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')