from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import (
    PremiumSchedule,
    PremiumInstalment,
    PremiumPayment,
    PremiumAdjustment,
    PremiumAuditLog
)

from policy.models import Policy


# --------------------------------------------------
# Premium Schedule List
# --------------------------------------------------

@login_required
def premium_list(request):

    schedules = PremiumSchedule.objects.select_related(
        "policy"
    ).prefetch_related(
        "instalments"
    )

    context = {
        "schedules": schedules
    }

    return render(request, "premium/premium_list.html", context)


# --------------------------------------------------
# Premium Detail Page
# --------------------------------------------------

@login_required
def premium_detail(request, id):

    schedule = get_object_or_404(
        PremiumSchedule.objects.select_related("policy")
        .prefetch_related(
            "instalments__payments",
            "adjustments",
            "audit_logs"
        ),
        pk=id
    )

    instalments = schedule.instalments.all()

    paid_count = instalments.filter(status="paid").count()

    total_instalments = schedule.total_instalments

    paid_percent = 0
    if total_instalments > 0:
        paid_percent = int((paid_count / total_instalments) * 100)

    context = {
        "schedule": schedule,
        "paid_count": paid_count,
        "paid_percent": paid_percent,
    }

    return render(request, "premium/premium_detail.html", context)


# --------------------------------------------------
# Pay Premium Instalment
# --------------------------------------------------

@login_required
def pay_premium(request, id):

    instalment = get_object_or_404(
        PremiumInstalment.objects.select_related(
            "schedule__policy"
        ).prefetch_related("payments"),
        pk=id
    )

    if request.method == "POST":

        amount = request.POST.get("amount")
        method = request.POST.get("payment_method")
        status = request.POST.get("status")
        txn = request.POST.get("transaction_id")
        paid_at = request.POST.get("paid_at")

        payment = PremiumPayment.objects.create(
            instalment=instalment,
            amount=amount,
            payment_method=method,
            transaction_id=txn,
            status=status,
            paid_at=paid_at if paid_at else None
        )

        # If payment success mark instalment paid
        if status == "success":

            instalment.status = "paid"

            instalment.paid_date = (
                payment.paid_at.date()
                if payment.paid_at
                else timezone.now().date()
            )

            instalment.save()

        # Create audit log
        PremiumAuditLog.objects.create(
            schedule=instalment.schedule,
            action=f"Payment {status} for Instalment #{instalment.instalment_number}",
            performed_by=request.user,
            description=f"₹{amount} via {method}. TXN: {txn}"
        )

        return redirect(
            "premium:premium_detail",
            id=instalment.schedule.id
        )

    context = {
        "instalment": instalment
    }

    return render(request, "premium/premium_pay.html", context)


# --------------------------------------------------
# Premium Payment History
# --------------------------------------------------

@login_required
def premium_history(request, policy_id):

    schedule = get_object_or_404(
        PremiumSchedule.objects.select_related("policy")
        .prefetch_related("instalments__payments"),
        policy_id=policy_id
    )

    payments = PremiumPayment.objects.filter(
        instalment__schedule=schedule
    ).select_related(
        "instalment"
    ).order_by("-created_at")

    # Filters
    status = request.GET.get("status")
    method = request.GET.get("method")
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    txn = request.GET.get("txn")

    if status:
        payments = payments.filter(status=status)

    if method:
        payments = payments.filter(payment_method=method)

    if from_date:
        payments = payments.filter(paid_at__date__gte=from_date)

    if to_date:
        payments = payments.filter(paid_at__date__lte=to_date)

    if txn:
        payments = payments.filter(transaction_id__icontains=txn)

    total_payments = payments.count()

    total_paid = payments.filter(status="success").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_failed = payments.filter(status="failed").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_pending = payments.filter(status="pending").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_refunded = payments.filter(status="refunded").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    paid_instalments = schedule.instalments.filter(
        status="paid"
    ).count()

    context = {
        "schedule": schedule,
        "payments": payments,
        "total_payments": total_payments,
        "total_paid": total_paid,
        "total_failed": total_failed,
        "total_pending": total_pending,
        "total_refunded": total_refunded,
        "paid_instalments": paid_instalments,
    }

    return render(
        request,
        "premium/premium_history.html",
        context
    )