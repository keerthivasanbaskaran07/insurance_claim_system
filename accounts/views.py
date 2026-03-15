from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import User
from policy.models import Policy
from claims.models import Claim
from django.db.models import Sum, Count
from datetime import date, timedelta
from typing import Any


# REGISTER

def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            password = form.cleaned_data["password"]

            user.set_password(password)

            user.save()

            messages.success(request,"Account created successfully")

            return redirect("accounts:login")

        else:

            messages.error(request,"Please fix the errors below")

    else:

        form = RegisterForm()

    return render(request,"accounts/register.html",{"form":form})
    

# DASHBOARDS

@login_required
def admin_dashboard(request):

    total_policies = Policy.objects.count()
    total_claims = Claim.objects.count()
    # Admin only sees claims forwarded into "Investigation" by the Staff
    pending_claims = Claim.objects.filter(status="investigation").count()
    approved_claims = Claim.objects.filter(status="approved").count()
    rejected_claims = Claim.objects.filter(status="rejected").count()

    total_staffs = User.objects.filter(role="staff").count()
    total_premium = Policy.objects.aggregate(total=Sum('premium'))['total'] or 0

    # Filter recent claims to exclude raw "submitted" or "under_review" items
    recent_claims = Claim.objects.filter(status__in=["investigation", "approved", "rejected", "settled"]).order_by('-created_at')[:5]
    recent_policies = Policy.objects.all().order_by('-created_at')[:5]

    context = {
        "total_users": User.objects.count(),
        "total_staffs": total_staffs,
        "total_policies": total_policies,
        "total_claims": total_claims,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "total_premium": total_premium,
        "recent_claims": recent_claims,
        "recent_policies": recent_policies,
    }

    return render(request, "accounts/dashboard_admin.html", context)


@login_required
def staff_dashboard(request):
    claims = Claim.objects.all()
    pending_claims = claims.filter(status__in=["submitted", "under_review"])
    recent_claims = claims.order_by('-created_at')[:5]
    
    # KPI metrics
    total_claims = claims.count()
    submitted_claims = claims.filter(status="submitted").count()
    approved_claims = claims.filter(status="approved").count()
    
    kpi = {
        'total_claims': total_claims,
        'submitted_claims': submitted_claims,
        'approved_claims': approved_claims,
    }

    # Claim status summary calculations
    total_claims_count = claims.count()
    status_counts = claims.values('status').annotate(count=Count('id'))
    
    claim_status_summary = []
    for s in status_counts:
        status = s['status']
        count = s['count']
        pct = (count / total_claims_count * 100) if total_claims_count > 0 else 0
        
        bar_class = 'bg-secondary'
        if status in ['approved', 'settled']: bar_class = 'bg-success'
        elif status in ['under_review', 'investigation']: bar_class = 'bg-warning'
        elif status == 'submitted': bar_class = 'bg-primary'
        elif status == 'rejected': bar_class = 'bg-danger'
        
        claim_status_summary.append({
            'label': status.replace('_', ' ').title(),
            'count': count,
            'percentage': pct,
            'bar_class': bar_class
        })

    context = {
        'claims': claims,
        'kpi': kpi,
        'pending_claims': pending_claims,
        'recent_claims': recent_claims,
        'claim_status_summary': claim_status_summary,
    }

    return render(request, "accounts/dashboard_staff.html", context)



@login_required
def policyholder_dashboard(request):

    context: dict[str, Any] = {}
    
    try:
        # Fetching policies and claims
        holder = request.user.policyholder
        policies = Policy.objects.filter(holder=holder)
        # Using created_by instead of policy__holder to show claims the user filed themselves
        claims = Claim.objects.filter(created_by=request.user)
        
        # KPI calculations
        active_policies = policies.filter(status='active')
        open_claims = claims.filter(status__in=['submitted', 'under_review', 'investigation', 'partially_approved'])
        
        total_sum = active_policies.aggregate(total=Sum('sum_insured'))['total'] or 0
        total_settled = claims.filter(status='settled').aggregate(total=Sum('settled_amount'))['total'] or 0
        
        context['kpi'] = {
            'total_policies': policies.count(),
            'active_policies': active_policies.count(),
            'total_claims': claims.count(),
            'open_claims': open_claims.count(),
            'total_sum_insured': total_sum,
            'total_settled': total_settled,
        }
        
        # Expiring policies calculation
        today = date.today()
        expiring = active_policies.filter(end_date__gte=today, end_date__lte=today + timedelta(days=30))
        expiring_policies = []
        for p in expiring:
            p.days_left = (p.end_date - today).days
            expiring_policies.append(p)
            
        context['expiring_policies'] = expiring_policies
        context['policies'] = policies.order_by('-created_at')[:10]
        
        # Claim summary breakdown
        total_claims_count = claims.count()
        status_counts = claims.values('status').annotate(count=Count('id'))
        
        claim_status_summary = []
        for s in status_counts:
            status = s['status']
            count = s['count']
            pct = (count / total_claims_count * 100) if total_claims_count > 0 else 0
            
            bar_class = 'bg-secondary'
            if status in ['approved', 'settled']: bar_class = 'bg-success'
            elif status in ['under_review', 'investigation']: bar_class = 'bg-warning'
            elif status == 'submitted': bar_class = 'bg-primary'
            elif status == 'rejected': bar_class = 'bg-danger'
            
            claim_status_summary.append({
                'label': status.replace('_', ' ').title(),
                'count': count,
                'percentage': pct,
                'bar_class': bar_class
            })
            
        context['claim_status_summary'] = claim_status_summary
        context['recent_claims'] = claims.order_by('-created_at')[:5]
        
    except Exception as e:
        context['kpi'] = {
            'total_policies': 0, 'active_policies': 0,
            'total_claims': 0, 'open_claims': 0,
            'total_sum_insured': 0, 'total_settled': 0,
        }
        context['policies'] = []
        context['expiring_policies'] = []
        context['claim_status_summary'] = []
        context['recent_claims'] = []

    return render(request, "accounts/dashboard_policyholder.html", context)


@login_required
def profile_view(request):

    return render(request, "accounts/profile.html")


# LOGIN

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request,username=username,password=password)

        if user is not None:

            login(request,user)

            if user.is_superuser or user.role == "admin":
                return redirect("accounts:admin_dashboard")

            elif user.role == "staff":
                return redirect("accounts:staff_dashboard")

            else:
                return redirect("accounts:policyholder_dashboard")

        else:

            messages.error(request,"Invalid username or password")

    return render(request,"accounts/login.html")


# LOGOUT

def logout_view(request):

    logout(request)

    return redirect("accounts:login")


def unauthorized_view(request):

    return render(request,"accounts/unauthorized.html")


# FORGOT PASSWORD

def forgot_password_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            messages.success(request, f"If an account exists for {email}, a password reset link has been sent.")
            return redirect("accounts:login")

    return render(request, "accounts/forgot_password.html")