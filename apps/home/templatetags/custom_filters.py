from django import template

register = template.Library()

@register.filter
def milliseconds_to_mmss(value):
    # Wandelt Millisekunden in Sekunden um
    total_seconds = value // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02}:{seconds:02}"

@register.filter(name='multiply')
def percent(value, arg):
    return value * float(arg)