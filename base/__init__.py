from django.template.defaultfilters import register

@register.filter
def format_view_count(view_count):
    if view_count > 999999:
        return '{:,.0f}M'.format(view_count / 1000000)
    elif view_count > 999:
        return '{:,.0f}K'.format(view_count / 1000)
    else:
        return view_count
