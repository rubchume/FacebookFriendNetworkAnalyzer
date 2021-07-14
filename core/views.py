import os

from background_task import background
from django.conf import settings
from django.core.files import File
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from core.forms import LogInForm
from core.models import LogEvent, ScanInstance
from src.facebook_friend_network_scanner import FacebookFriendNetworkScanner


class HomeView(TemplateView):
    template_name = "core/home.html"


class LogInView(FormView):
    template_name = "core/login.html"
    form_class = LogInForm
    success_url = reverse_lazy("scan")

    def form_valid(self, form):
        scan_facebook_friend_network(form.cleaned_data["user"], form.cleaned_data["password"])
        LogEvent.objects.all().delete()
        return super().form_valid(form)


@background(schedule=1)
def scan_facebook_friend_network(user, password):
    def write_to_log(text):
        print(text)
        LogEvent.objects.create(
            scan_instance=scan_instance,
            text=text
        )

    def save_scan_results():
        print(settings.BASE_DIR)
        print(settings.MEDIA_ROOT)
        temporary_network_file_path = os.path.join(
            settings.BASE_DIR, settings.MEDIA_ROOT, "temp", f"network_{user}.json"
        )
        ffn.save_network(output_file_name=temporary_network_file_path)
        with open(temporary_network_file_path) as file:
            scan_instance.file = File(file, name=f"{user}.json")
            scan_instance.save()
        os.remove(temporary_network_file_path)

    scan_instance = ScanInstance.objects.create(user=user)

    write_to_log("Configuring scanner")
    ffn = FacebookFriendNetworkScanner(user, password)

    write_to_log("Start scanning")
    ffn.scan_network(notify=write_to_log)

    write_to_log("Saving scan")
    save_scan_results()

    write_to_log("Scan has finished")


class ScanView(TemplateView):
    template_name = "core/scan.html"

    def get_context_data(self, **kwargs):
        events = LogEvent.objects.all().order_by('-datetime')

        context = super().get_context_data(**kwargs)
        context["log"] = events
        return context

