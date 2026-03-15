import datetime
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from policy.models import PolicyHolder, Policy

from .models import (
    Claim,
    ClaimDocument,
    ClaimNote,
    ClaimAssessment,
    ClaimSettlement,
    ClaimAuditLog
)


# =====================================
# CLAIM LIST
# =====================================

@login_required
def claim_list(request):

    claims = Claim.objects.select_related(
        "policy",
        "assigned_to"
    )

    if not request.user.is_superuser and request.user.role not in ["admin", "staff"]:
        claims = claims.filter(created_by=request.user)

    summary = {
        "total": claims.count(),
        "under_review": claims.filter(status="under_review").count(),
        "investigation": claims.filter(status="investigation").count(),
        "approved": claims.filter(status="approved").count(),
        "rejected": claims.filter(status="rejected").count(),
        "settled": claims.filter(status="settled").count(),
    }

    return render(
        request,
        "claims/claim_list.html",
        {
            "claims": claims,
            "summary": summary
        }
    )


# =====================================
# CREATE CLAIM
# =====================================

@login_required
def claim_submit(request):

    # All policies created by admin are available to every user
    policies = Policy.objects.all()

    if request.method == "POST":

        policy_id = request.POST.get("policy")
        policy = get_object_or_404(Policy, id=policy_id)

        claim = Claim.objects.create(
            policy=policy,
            claim_number=f"CLM-{int(timezone.now().timestamp())}",
            claim_type=request.POST.get("claim_type"),
            status="submitted",
            incident_date=request.POST.get("incident_date"),
            description=request.POST.get("description"),
            claimed_amount=Decimal(request.POST.get("claimed_amount")),
            deductible_amount=policy.deductible,
            created_by=request.user
        )

        # FILE UPLOAD
        file = request.FILES.get("document")

        if file:

            ClaimDocument.objects.create(
                claim=claim,
                document_type="other",
                file=file,
                description="Uploaded during claim submission",
                uploaded_by=request.user
            )

        ClaimAuditLog.objects.create(
            claim=claim,
            action="Claim Created",
            performed_by=request.user
        )

        messages.success(request, "Claim created successfully")

        return redirect("claim:detail", id=claim.id)

    return render(
        request,
        "claims/claim_submit.html",
        {"policies": policies}
    )


# =====================================
# CLAIM DETAIL
# =====================================

@login_required
def claim_detail(request, id):

    claim = get_object_or_404(
        Claim.objects.select_related(
            "policy",
            "assigned_to",
            "assessment",
            "settlement"
        ).prefetch_related(
            "claimants",
            "documents",
            "notes",
            "audit_logs"
        ),
        id=id
    )

    net_claim = (claim.claimed_amount or 0) - (claim.deductible_amount or 0)

    return render(
        request,
        "claims/claim_detail.html",
        {
            "claim": claim,
            "net_claim": net_claim
        }
    )


# =====================================
# EDIT CLAIM
# =====================================

@login_required
def claim_edit(request, id):

    claim = get_object_or_404(Claim, id=id)

    if request.user != claim.policy.holder.user:
        return render(request, "policy/admin_only.html", {
            "message": "Only the policyholder can edit the claim"
        })

    if request.method == "POST":

        claim.description = request.POST.get("description")

        claim.claimed_amount = Decimal(
            request.POST.get("claimed_amount")
        )

        claim.deductible_amount = Decimal(
            request.POST.get("deductible_amount", 0)
        )

        claim.save()

        ClaimAuditLog.objects.create(
            claim=claim,
            action="Claim Updated",
            performed_by=request.user
        )

        messages.success(request, "Claim updated")

        return redirect("claim:detail", id=claim.id)

    return render(
        request,
        "claims/claim_edit.html",
        {"claim": claim}
    )


# =====================================
# DELETE CLAIM
# =====================================

@login_required
def claim_delete(request, id):

    claim = get_object_or_404(Claim, id=id)

    if request.method == "POST":

        ClaimAuditLog.objects.create(
            claim=claim,
            action="Claim Deleted",
            performed_by=request.user
        )

        claim.delete()

        messages.success(request, "Claim deleted")

        return redirect("claim:list")

    return redirect("claim:detail", id=id)


# =====================================
# CLAIM REVIEW
# =====================================

@login_required
def claim_review(request, id):

    claim = get_object_or_404(Claim, id=id)

    today = datetime.date.today()

    days_since_incident = (today - claim.incident_date).days

    net_claimable = (claim.claimed_amount or 0) - (claim.deductible_amount or 0)

    policy = claim.policy

    policy_active_on_incident = (
        policy.start_date <= claim.incident_date <= policy.end_date
    )

    return render(
        request,
        "claims/claim_review.html",
        {
            "claim": claim,
            "today": today,
            "days_since_incident": days_since_incident,
            "net_claimable": net_claimable,
            "policy_active_on_incident": policy_active_on_incident
        }
    )


# =====================================
# UPDATE CLAIM STATUS
# =====================================

@login_required
def update_claim_status(request, id):

    claim = get_object_or_404(Claim, id=id)

    if request.method == "POST":

        status = request.POST.get("status")

        claim.status = status

        # Save staff verification fields if submitted
        if request.POST.get("policy_validity"):
            claim.policy_validity = request.POST.get("policy_validity")
            claim.document_verification = request.POST.get("document_verification")
            claim.amount_verification = request.POST.get("amount_verification")
            claim.staff_comments = request.POST.get("assessment_comments")
            
            if request.POST.get("recommended_amount"):
                claim.recommended_amount = Decimal(request.POST.get("recommended_amount"))

        if request.user.is_admin or request.user.role == 'staff':
            claim.assigned_to = request.user

        if status == 'approved':
            claim.approved_amount = claim.claimed_amount
        elif status == 'settled':
            if claim.approved_amount:
                claim.settled_amount = claim.approved_amount
            else:
                claim.settled_amount = claim.claimed_amount

        claim.save()

        ClaimAuditLog.objects.create(
            claim=claim,
            action=f"Status updated to {status}",
            performed_by=request.user
        )

        messages.success(request, "Claim status updated")

    return redirect("claim:detail", id=claim.id)


# =====================================
# CLAIM ASSESSMENT
# =====================================

@login_required
def claim_assessment(request, claim_id):

    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == "POST":

        try:
            assessment = claim.assessment
        except ClaimAssessment.DoesNotExist:
            assessment = ClaimAssessment(claim=claim)

        assessment.verdict = request.POST.get("verdict")
        assessment.recommended_amount = request.POST.get("recommended_amount")
        assessment.remarks = request.POST.get("remarks")
        assessment.assessed_by = request.user

        assessment.save()

        ClaimAuditLog.objects.create(
            claim=claim,
            action="Claim assessed",
            performed_by=request.user
        )

        messages.success(request, "Assessment saved")

        return redirect("claim:detail", id=claim.id)

    return render(
        request,
        "claims/claim_assessment.html",
        {"claim": claim}
    )


# =====================================
# CLAIM SETTLEMENT
# =====================================

@login_required
def claim_settlement(request, claim_id):

    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == "POST":

        try:
            settlement = claim.settlement
        except ClaimSettlement.DoesNotExist:
            settlement = ClaimSettlement(claim=claim)

        settlement.payment_mode = request.POST.get("payment_mode")

        settlement.settled_amount = Decimal(
            request.POST.get("settled_amount")
        )

        settlement.transaction_reference = request.POST.get("reference")

        settlement.payee_name = request.POST.get("payee_name")

        settlement.processed_by = request.user

        settlement.save()

        claim.status = "settled"
        claim.settled_amount = settlement.settled_amount
        claim.save()

        ClaimAuditLog.objects.create(
            claim=claim,
            action="Claim settled",
            performed_by=request.user
        )

        messages.success(request, "Claim settlement recorded")

        return redirect("claim:detail", id=claim.id)

    return render(
        request,
        "claims/claim_settlement.html",
        {"claim": claim}
    )


# =====================================
# UPLOAD DOCUMENT
# =====================================

@login_required
def upload_claim_document(request, claim_id):

    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == "POST":

        file = request.FILES.get("file")

        ClaimDocument.objects.create(

            claim=claim,

            document_type=request.POST.get("document_type", "other"),

            file=file,

            description=request.POST.get("description", ""),

            uploaded_by=request.user
        )

        messages.success(request, "Document uploaded")

    return redirect("claim:detail", id=claim.id)


# =====================================
# DELETE DOCUMENT
# =====================================

@login_required
def delete_claim_document(request, id):

    document = get_object_or_404(ClaimDocument, id=id)

    claim_id = document.claim.id

    document.delete()

    messages.success(request, "Document deleted")

    return redirect("claim:detail", id=claim_id)


# =====================================
# ADD NOTE
# =====================================

@login_required
def add_claim_note(request, claim_id):

    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == "POST":

        ClaimNote.objects.create(
            claim=claim,
            note_type=request.POST.get("note_type"),
            content=request.POST.get("content"),
            created_by=request.user
        )

        messages.success(request, "Note added")

    return redirect("claim:detail", id=claim.id)


# =====================================
# DELETE NOTE
# =====================================

@login_required
def delete_claim_note(request, id):

    note = get_object_or_404(ClaimNote, id=id)

    claim_id = note.claim.id

    note.delete()

    messages.success(request, "Note deleted")

    return redirect("claim:detail", id=claim_id)


# =====================================
# CLAIM HISTORY
# =====================================

@login_required
def claim_history(request, claim_id):

    claim = get_object_or_404(Claim, id=claim_id)

    logs = claim.audit_logs.all()

    return render(
        request,
        "claims/claim_history.html",
        {
            "claim": claim,
            "logs": logs
        }
    )