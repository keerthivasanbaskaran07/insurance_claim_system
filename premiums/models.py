from django.db import models
from django.conf import settings
from policy.models import Policy
from decimal import Decimal


# -----------------------------
# Premium Schedule
# -----------------------------

class PremiumSchedule(models.Model):

    PAYMENT_FREQUENCY = [
        ("single", "Single Payment"),
        ("annual", "Annual"),
        ("half_yearly", "Half Yearly"),
        ("quarterly", "Quarterly"),
        ("monthly", "Monthly"),
    ]

    policy = models.OneToOneField(
        Policy,
        on_delete=models.CASCADE,
        related_name="premium_schedule"
    )

    sum_insured = models.DecimalField(max_digits=12, decimal_places=2)

    base_premium = models.DecimalField(max_digits=10, decimal_places=2)

    net_premium = models.DecimalField(max_digits=10, decimal_places=2)

    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18
    )

    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    gross_premium = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY,
        default="annual"
    )

    total_instalments = models.IntegerField(default=1)

    instalment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    grace_period_days = models.IntegerField(default=30)

    auto_debit_enabled = models.BooleanField(default=False)

    effective_from = models.DateField()
    effective_to = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Premium Schedule - {self.policy.policy_number}"


# -----------------------------
# Premium Instalment
# -----------------------------

class PremiumInstalment(models.Model):

    STATUS = [
        ("upcoming", "Upcoming"),
        ("due", "Due"),
        ("grace", "Grace"),
        ("overdue", "Overdue"),
        ("paid", "Paid"),
        ("lapsed", "Lapsed"),
    ]

    schedule = models.ForeignKey(
        PremiumSchedule,
        on_delete=models.CASCADE,
        related_name="instalments"
    )

    instalment_number = models.IntegerField()

    due_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="upcoming"
    )

    paid_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Instalment {self.instalment_number} - {self.schedule.policy.policy_number}"


# -----------------------------
# Premium Payment
# -----------------------------

class PremiumPayment(models.Model):

    PAYMENT_METHOD = [
        ("upi", "UPI"),
        ("card", "Card"),
        ("netbanking", "Net Banking"),
        ("cash", "Cash"),
        ("neft", "NEFT"),
    ]

    STATUS = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    instalment = models.ForeignKey(
        PremiumInstalment,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    transaction_id = models.CharField(max_length=120, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.instalment.schedule.policy.policy_number} - {self.amount}"


# -----------------------------
# Premium Adjustment
# -----------------------------

class PremiumAdjustment(models.Model):

    TYPE = [
        ("discount", "Discount"),
        ("loading", "Loading"),
        ("refund", "Refund"),
        ("bonus", "Bonus"),
        ("penalty", "Penalty"),
    ]

    schedule = models.ForeignKey(
        PremiumSchedule,
        on_delete=models.CASCADE,
        related_name="adjustments"
    )

    adjustment_type = models.CharField(max_length=20, choices=TYPE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adjustment_type} - {self.amount}"


# -----------------------------
# Premium Audit Log
# -----------------------------

class PremiumAuditLog(models.Model):

    schedule = models.ForeignKey(
        PremiumSchedule,
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
        return f"{self.schedule.policy.policy_number} - {self.action}"