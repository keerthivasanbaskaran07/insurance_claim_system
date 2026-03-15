from django.contrib import admin
from .models import (
    PremiumSchedule,
    PremiumInstalment,
    PremiumPayment,
    PremiumAdjustment,
    PremiumAuditLog
)


# -----------------------------
# Premium Instalments Inline
# -----------------------------
class PremiumInstalmentInline(admin.TabularInline):
    model = PremiumInstalment
    extra = 0


# -----------------------------
# Premium Schedule
# -----------------------------
@admin.register(PremiumSchedule)
class PremiumScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "policy",
        "gross_premium",
        "payment_frequency",
        "total_instalments",
        "effective_from",
        "effective_to",
    )

    search_fields = ("policy__policy_number",)

    list_filter = ("payment_frequency",)

    inlines = [PremiumInstalmentInline]


# -----------------------------
# Premium Instalment
# -----------------------------
@admin.register(PremiumInstalment)
class PremiumInstalmentAdmin(admin.ModelAdmin):

    list_display = (
        "schedule",
        "instalment_number",
        "due_date",
        "amount",
        "status",
        "paid_date",
    )

    list_filter = ("status",)

    search_fields = ("schedule__policy__policy_number",)


# -----------------------------
# Premium Payment
# -----------------------------
@admin.register(PremiumPayment)
class PremiumPaymentAdmin(admin.ModelAdmin):

    list_display = (
        "instalment",
        "amount",
        "payment_method",
        "status",
        "transaction_id",
        "paid_at",
    )

    list_filter = ("status", "payment_method")

    search_fields = ("transaction_id",)


# -----------------------------
# Premium Adjustment
# -----------------------------
@admin.register(PremiumAdjustment)
class PremiumAdjustmentAdmin(admin.ModelAdmin):

    list_display = (
        "schedule",
        "adjustment_type",
        "amount",
        "created_at",
    )

    list_filter = ("adjustment_type",)

    search_fields = ("schedule__policy__policy_number",)


# -----------------------------
# Premium Audit Log
# -----------------------------
@admin.register(PremiumAuditLog)
class PremiumAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "schedule",
        "action",
        "performed_by",
        "created_at",
    )

    search_fields = ("action",)