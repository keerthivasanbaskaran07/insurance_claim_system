from django.urls import path
from . import views

app_name = "premium"

urlpatterns = [

    path(
        "",
        views.premium_list,
        name="premium_list"
    ),

    path(
        "<int:id>/",
        views.premium_detail,
        name="premium_detail"
    ),

    path(
        "pay/<int:id>/",
        views.pay_premium,
        name="pay_premium"
    ),

    path(
        "history/<int:policy_id>/",
        views.premium_history,
        name="premium_history"
    ),

]