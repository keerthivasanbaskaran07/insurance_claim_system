from django.contrib import admin
from .models import (
    PolicyHolder,
    Policy,
    Coverage,
    Beneficiary,
    Premium,
    PolicyDocument,
    PolicyAuditLog,
    PolicyType,
    Insurer
)

@admin.register(PolicyType)
class PolicyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code")

@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email")


# -----------------------
# Policy Holder Admin
# -----------------------

@admin.register(PolicyHolder)
class PolicyHolderAdmin(admin.ModelAdmin):

    list_display = ("id", "user", "phone", "city", "state", "created_at")

    search_fields = ("user__username", "phone", "city")

    list_filter = ("state",)


# -----------------------
# Policy Admin
# -----------------------

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):

    list_display = (
        "policy_number",
        "holder",
        "policy_type",
        "status",
        "start_date",
        "end_date",
        "premium"
    )

    list_filter = ("policy_type", "status")

    search_fields = ("policy_number", "insurer_name")

    ordering = ("-created_at",)


# -----------------------
# Coverage Admin
# -----------------------

@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):

    list_display = (
        "coverage_type",
        "policy",
        "limit_amount",
        "deductible"
    )

    search_fields = ("coverage_type",)


# -----------------------
# Beneficiary Admin
# -----------------------

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "policy",
        "relationship",
        "share_percentage"
    )

    search_fields = ("name",)


# -----------------------
# Premium Admin
# -----------------------

@admin.register(Premium)
class PremiumAdmin(admin.ModelAdmin):

    list_display = (
        "policy",
        "amount",
        "due_date",
        "status"
    )

    list_filter = ("status",)

    search_fields = ("transaction_id",)


# -----------------------
# Policy Document Admin
# -----------------------

@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "document_name",
        "policy",
        "uploaded_at"
    )

    search_fields = ("document_name",)


# -----------------------
# Audit Log Admin
# -----------------------

@admin.register(PolicyAuditLog)
class PolicyAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "policy",
        "action",
        "performed_by",
        "created_at"
    )

    search_fields = ("action",)

    readonly_fields = ("created_at",)