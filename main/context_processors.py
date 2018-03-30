from employee_management.settings import SITE_NAME, API_URL, DOMAIN, SITE_LOGO


def site_detail(request):
    return {
        "SITE_NAME": SITE_NAME,
        "SITE_LOGO": SITE_LOGO,
        "API_URL": API_URL,
        "DOMAIN": DOMAIN
    }
