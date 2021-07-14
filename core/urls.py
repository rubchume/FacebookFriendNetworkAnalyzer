from django.urls import path

from core.views import HomeView, LogInView, ScanView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login", LogInView.as_view(), name="login"),
    path("scan", ScanView.as_view(), name="scan"),
]
