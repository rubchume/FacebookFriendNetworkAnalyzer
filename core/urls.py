from django.urls import path

from core.views import HomeView, LogInView, ScanView, ChooseNetworkView, AnalysisView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login", LogInView.as_view(), name="login"),
    path("scan", ScanView.as_view(), name="scan"),
    path("choose_network", ChooseNetworkView.as_view(), name="choose_network"),
    path("analysis/<int:pk>", AnalysisView.as_view(), name="analysis"),
]
