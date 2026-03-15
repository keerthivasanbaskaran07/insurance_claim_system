from django.db import models
from django.conf import settings
from django.utils import timezone
from policy.models import Policy


# -----------------------------
# Claim
# -----------------------------

class Claim(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("investigation", "Investigation"),
        ("approved", "Approved"),
        ("partially_approved", "Partially Approved"),
        ("rejected", "Rejected"),
        ("settled", "Settled"),
        ("closed", "Closed"),
        ("withdrawn", "Withdrawn"),
    ]

    CLAIM_TYPE = [
        ("death", "Death"),
        ("maturity", "Maturity"),
        ("surrender", "Surrender"),
        ("accident", "Accident"),
        ("disability", "Disability"),
        ("critical_illness", "Critical Illness"),
        ("hospitalization", "Hospitalization"),
        ("property_damage", "Property Damage"),
        ("theft", "Theft"),
        ("fire", "Fire"),
        ("natural_disaster", "Natural Disaster"),
        ("third_party", "Third Party Liability"),
        ("other", "Other"),
    ]

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="claims"
    )

    claim_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True
    )

    claim_type = models.CharField(
        max_length=30,
        choices=CLAIM_TYPE
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="draft",
        db_index=True
    )

    incident_date = models.DateField()

    reported_date = models.DateField(default=timezone.now)

    description = models.TextField(blank=True)

    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2)

    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    settled_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    deductible_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    rejection_reason = models.TextField(blank=True)

    # Staff Verification Fields
    policy_validity = models.CharField(max_length=20, blank=True, null=True)
    document_verification = models.CharField(max_length=20, blank=True, null=True)
    amount_verification = models.CharField(max_length=20, blank=True, null=True)
    staff_comments = models.TextField(blank=True, null=True)
    recommended_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_claims"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_claims"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim {self.claim_number} — {self.policy.policy_number}"

    class Meta:
        ordering = ["-created_at"]


# -----------------------------
# Claimant
# -----------------------------

class Claimant(models.Model):

    RELATIONSHIP = [
        ("self", "Self"),
        ("spouse", "Spouse"),
        ("parent", "Parent"),
        ("child", "Child"),
        ("nominee", "Nominee"),
        ("legal_heir", "Legal Heir"),
        ("other", "Other"),
    ]

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="claimants"
    )

    full_name = models.CharField(max_length=200)

    relationship = models.CharField(
        max_length=30,
        choices=RELATIONSHIP
    )

    contact_number = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True)

    id_proof_type = models.CharField(max_length=50, blank=True)

    id_proof_number = models.CharField(max_length=100, blank=True)

    bank_account_number = models.CharField(max_length=30, blank=True)

    bank_ifsc = models.CharField(max_length=20, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.full_name} — {self.claim.claim_number}"


# -----------------------------
# Claim Document
# -----------------------------

class ClaimDocument(models.Model):

    DOCUMENT_TYPE = [
        ("claim_form", "Claim Form"),
        ("death_certificate", "Death Certificate"),
        ("medical_report", "Medical Report"),
        ("hospital_bill", "Hospital Bill"),
        ("discharge_summary", "Discharge Summary"),
        ("fir_copy", "FIR Copy"),
        ("police_report", "Police Report"),
        ("id_proof", "ID Proof"),
        ("address_proof", "Address Proof"),
        ("bank_proof", "Bank Proof"),
        ("policy_copy", "Policy Copy"),
        ("photos", "Photos / Evidence"),
        ("other", "Other"),
    ]

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE
    )

    file = models.FileField(
        upload_to="claims/documents/%Y/%m/"
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.claim_number} — {self.document_type}"


# -----------------------------
# Claim Assessment
# -----------------------------

class ClaimAssessment(models.Model):

    VERDICT = [
        ("approved", "Approved"),
        ("partially_approved", "Partially Approved"),
        ("rejected", "Rejected"),
        ("pending", "Pending Further Info"),
    ]

    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        related_name="assessment"
    )

    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assessed_claims"
    )

    assessed_on = models.DateField(default=timezone.now)

    verdict = models.CharField(
        max_length=30,
        choices=VERDICT
    )

    recommended_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True)

    investigation_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.claim_number} — {self.verdict}"


# -----------------------------
# Claim Settlement
# -----------------------------

class ClaimSettlement(models.Model):

    PAYMENT_MODE = [
        ("neft", "NEFT"),
        ("cheque", "Cheque"),
        ("upi", "UPI"),
        ("cash", "Cash"),
        ("dd", "Demand Draft"),
    ]

    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        related_name="settlement"
    )

    settlement_date = models.DateField(default=timezone.now)

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE
    )

    transaction_reference = models.CharField(max_length=120, blank=True)

    settled_amount = models.DecimalField(max_digits=12, decimal_places=2)

    payee_name = models.CharField(max_length=200)

    bank_account = models.CharField(max_length=30, blank=True)

    bank_ifsc = models.CharField(max_length=20, blank=True)

    remarks = models.TextField(blank=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_claims"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.claim_number} — ₹{self.settled_amount}"


# -----------------------------
# Claim Note
# -----------------------------

class ClaimNote(models.Model):

    NOTE_TYPE = [
        ("internal", "Internal Note"),
        ("customer", "Customer Communication"),
        ("investigation", "Investigation Note"),
        ("legal", "Legal Note"),
    ]

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE,
        default="internal"
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.claim_number} — Note"


# -----------------------------
# Claim Audit Log
# -----------------------------

class ClaimAuditLog(models.Model):

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    action = models.CharField(max_length=200)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.claim_number} — {self.action}"