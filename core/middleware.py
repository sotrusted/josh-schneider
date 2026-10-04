import hashlib
from .models import PageVisit

_BOT_PATTERNS = (
    'bot', 'crawler', 'spider', 'slurp', 'scrape', 'scan', 'archiv',
    'fetch', 'monitor', 'check', 'curl/', 'wget/', 'python-requests',
    'python-urllib', 'httpx', 'go-http', 'java/', 'libwww', 'okhttp',
    'facebookexternalhit', 'twitterbot', 'linkedinbot', 'whatsapp',
    'telegrambot', 'discordbot', 'slackbot', 'iframely', 'embedly',
    'pingdom', 'uptimerobot', 'statuscake', 'newrelic', 'datadog',
    'ahrefs', 'semrush', 'majestic', 'mj12bot', 'dotbot', 'petalbot',
    'bytespider', 'gptbot', 'claudebot', 'anthropic', 'openai',
    'headlesschrome', 'phantomjs', 'prerender', 'lighthouse',
)

_SKIP_PREFIXES = ('/admin', '/static', '/media', '/favicon')


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == 'GET'
            and response.status_code < 400
            and not any(request.path.startswith(p) for p in _SKIP_PREFIXES)
        ):
            self._record(request)
        return response

    def _record(self, request):
        ua = (request.META.get('HTTP_USER_AGENT') or '').lower()
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', '')
        )
        is_bot = not ua or any(p in ua for p in _BOT_PATTERNS)
        PageVisit.objects.create(
            path=request.path[:500],
            ip_hash=hashlib.sha256(ip.encode()).hexdigest(),
            user_agent=ua[:500],
            referrer=(request.META.get('HTTP_REFERER') or '')[:500],
            is_bot=is_bot,
        )
