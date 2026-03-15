from django.db import models
from django.conf import settings


# ------------------------------
# Policy Holder
# ------------------------------

class PolicyHolder(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)
    address = models.TextField()

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'policy_policyholder'
        verbose_name_plural = "Policy Holders"


# ------------------------------
# Categories & Insurers
# ------------------------------

class PolicyType(models.Model):
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Insurer(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


# ------------------------------
# Policy
# ------------------------------

class Policy(models.Model):

    STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]

    policy_number = models.CharField(max_length=30, unique=True)

    holder = models.ForeignKey(
        PolicyHolder,
        on_delete=models.CASCADE,
        related_name="policies"
    )

    policy_type = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='draft'
    )

    insurer_name = models.CharField(max_length=150, blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    sum_insured = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    premium = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    deductible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.policy_number

    class Meta:
        db_table = 'policy_policy'
        verbose_name_plural = "Policies"


# ------------------------------
# Coverage
# ------------------------------

class Coverage(models.Model):

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="coverages"
    )

    coverage_type = models.CharField(max_length=100)

    limit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    deductible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.coverage_type} - {self.policy.policy_number}"


# ------------------------------
# Beneficiary
# ------------------------------

class Beneficiary(models.Model):

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="beneficiaries"
    )

    name = models.CharField(max_length=150)

    relationship = models.CharField(max_length=100)

    share_percentage = models.IntegerField()

    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


# ------------------------------
# Premium
# ------------------------------

class Premium(models.Model):

    STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="premiums"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    due_date = models.DateField()

    paid_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return f"{self.policy.policy_number} - {self.amount}"


# ------------------------------
# Policy Document
# ------------------------------

class PolicyDocument(models.Model):

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_name = models.CharField(max_length=200)

    file = models.FileField(upload_to="policy_documents/")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name


# ------------------------------
# Policy Audit Log
# ------------------------------

class PolicyAuditLog(models.Model):

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    action = models.CharField(max_length=200)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.policy.policy_number} - {self.action}"