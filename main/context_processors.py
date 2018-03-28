from employee_management.settings import SITE_NAME, API_URL, DOMAIN


def site_detail(request):
    return {
        "SITE_NAME": SITE_NAME,
        "API_URL": API_URL,
        "DOMAIN": DOMAIN
    }
