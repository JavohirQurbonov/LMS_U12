import re

from django import template

register = template.Library()

_YT_WATCH = re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)')


@register.filter
def embed_url(url):
    if not url:
        return ''
    match = _YT_WATCH.search(url)
    if match:
        return f'https://www.youtube.com/embed/{match.group(1)}'
    return url


@register.filter
def is_embeddable(url):
    return bool(url) and ('youtube.com' in url or 'youtu.be' in url or 'vimeo.com' in url)
