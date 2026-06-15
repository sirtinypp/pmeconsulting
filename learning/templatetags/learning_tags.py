from django import template
import re

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter
def youtube_embed_url(value):
    if not value:
        return ""
    # Regex to match youtube video ID
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, value)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube-nocookie.com/embed/{video_id}"
    return value

