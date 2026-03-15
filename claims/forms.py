from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
import os

from .models import (
    Claim,
    Claimant,
    ClaimDocument,
    ClaimAssessment,
    ClaimSettlement,
    ClaimNote,
)

User = get_user_model()


# -----------------------------
# Claim Submission Form
# -----------------------------

class ClaimForm(forms.ModelForm):

    class Meta:
        model = Claim

        fields = [
            "policy",
            "claim_number",
            "claim_type",
            "incident_date",
            "reported_date",
            "description",
            "claimed_amount",
        ]

        widgets = {
            "policy": forms.Select(attrs={"class": "form-select"}),

            "claim_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CLM-2024-00001"
            }),

            "claim_type": forms.Select(attrs={"class": "form-select"}),

            "incident_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "reported_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

            "claimed_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0"
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        incident_date = cleaned_data.get("incident_date")
        reported_date = cleaned_data.get("reported_date")

        if incident_date and reported_date:
            if reported_date < incident_date:
                self.add_error(
                    "reported_date",
                    "Reported date cannot be before incident date."
                )

        if incident_date and incident_date > timezone.now().date():
            self.add_error(
                "incident_date",
                "Incident date cannot be in the future."
            )

        return cleaned_data


# -----------------------------
# Claimant Form
# -----------------------------

class ClaimantForm(forms.ModelForm):

    class Meta:
        model = Claimant

        fields = [
            "full_name",
            "relationship",
            "contact_number",
            "email",
            "id_proof_type",
            "id_proof_number",
            "bank_account_number",
            "bank_ifsc",
            "bank_name",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),

            "relationship": forms.Select(attrs={"class": "form-select"}),

            "contact_number": forms.TextInput(attrs={"class": "form-control"}),

            "email": forms.EmailInput(attrs={"class": "form-control"}),

            "id_proof_type": forms.TextInput(attrs={"class": "form-control"}),

            "id_proof_number": forms.TextInput(attrs={"class": "form-control"}),

            "bank_account_number": forms.TextInput(attrs={"class": "form-control"}),

            "bank_ifsc": forms.TextInput(attrs={"class": "form-control"}),

            "bank_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_bank_ifsc(self):

        ifsc = self.cleaned_data.get("bank_ifsc", "").strip().upper()

        if ifsc and len(ifsc) != 11:
            raise forms.ValidationError(
                "IFSC code must be exactly 11 characters."
            )

        if ifsc and not ifsc.isalnum():
            raise forms.ValidationError(
                "Invalid IFSC format."
            )

        return ifsc


# -----------------------------
# Claim Document Form
# -----------------------------

class ClaimDocumentForm(forms.ModelForm):

    class Meta:
        model = ClaimDocument

        fields = ["document_type", "file", "description"]

        widgets = {
            "document_type": forms.Select(attrs={"class": "form-select"}),

            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),

            "description": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_file(self):

        file = self.cleaned_data.get("file")

        if file:

            max_size = 10 * 1024 * 1024

            if file.size > max_size:
                raise forms.ValidationError(
                    "File size must not exceed 10 MB."
                )

            allowed = [
                ".pdf",
                ".jpg",
                ".jpeg",
                ".png",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
            ]

            ext = os.path.splitext(file.name)[1].lower()

            if ext not in allowed:
                raise forms.ValidationError(
                    "Unsupported file type."
                )

        return file


# -----------------------------
# Claim Assessment Form
# -----------------------------

class ClaimAssessmentForm(forms.ModelForm):

    class Meta:
        model = ClaimAssessment

        fields = [
            "assessed_by",
            "assessed_on",
            "verdict",
            "recommended_amount",
            "remarks",
            "investigation_required",
        ]

        widgets = {
            "assessed_by": forms.Select(attrs={"class": "form-select"}),

            "assessed_on": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "verdict": forms.Select(attrs={"class": "form-select"}),

            "recommended_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),

            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

            "investigation_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        verdict = cleaned_data.get("verdict")
        amount = cleaned_data.get("recommended_amount")

        if verdict in ("approved", "partially_approved") and not amount:
            self.add_error(
                "recommended_amount",
                "Recommended amount required."
            )

        return cleaned_data


# -----------------------------
# Claim Settlement Form
# -----------------------------

class ClaimSettlementForm(forms.ModelForm):

    class Meta:
        model = ClaimSettlement

        fields = [
            "settlement_date",
            "payment_mode",
            "transaction_reference",
            "settled_amount",
            "payee_name",
            "bank_account",
            "bank_ifsc",
            "remarks",
            "processed_by",
        ]

        widgets = {
            "settlement_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "payment_mode": forms.Select(attrs={"class": "form-select"}),

            "transaction_reference": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "settled_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),

            "payee_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "bank_account": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "bank_ifsc": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "remarks": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "processed_by": forms.Select(attrs={"class": "form-select"}),
        }


# -----------------------------
# Claim Note Form
# -----------------------------

class ClaimNoteForm(forms.ModelForm):

    class Meta:
        model = ClaimNote

        fields = ["note_type", "content"]

        widgets = {
            "note_type": forms.Select(attrs={"class": "form-select"}),

            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
        }

    def clean_content(self):

        content = self.cleaned_data.get("content", "").strip()

        if len(content) < 5:
            raise forms.ValidationError(
                "Note must be at least 5 characters."
            )

        return content


# -----------------------------
# Claim Status Update
# -----------------------------

class ClaimStatusForm(forms.ModelForm):

    class Meta:
        model = Claim

        fields = ["status", "rejection_reason"]

        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),

            "rejection_reason": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        reason = cleaned_data.get("rejection_reason")

        if status == "rejected" and not reason:
            self.add_error(
                "rejection_reason",
                "Rejection reason required."
            )

        return cleaned_data


# -----------------------------
# Claim Filter Form
# -----------------------------

class ClaimFilterForm(forms.Form):

    claim_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    claim_type = forms.ChoiceField(
        required=False,
        choices=[("", "All")] + Claim.CLAIM_TYPE,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    status = forms.ChoiceField(
        required=False,
        choices=[("", "All")] + Claim.STATUS,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        })
    )

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )