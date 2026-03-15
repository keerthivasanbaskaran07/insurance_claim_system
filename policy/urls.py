from django.urls import path
from . import views

app_name = "policy"

urlpatterns = [

    path("", views.policy_list, name="list"),
    path("create/", views.create_policy, name="create"),
    path("<int:id>/", views.policy_detail, name="detail"),
    path("edit/<int:id>/", views.edit_policy, name="edit"),
    path("status/<int:id>/", views.update_policy_status, name="update_status"),
    path("delete/<int:id>/", views.delete_policy, name="delete"),
    path("status/<int:id>/", views.update_policy_status, name="update_status"),
]