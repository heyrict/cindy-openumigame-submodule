from django import template

register = template.Library()


@register.filter
def get_page_list(paginator, current):
    max_pagenum = paginator.num_pages
    if current < 10:
        return range(1, 11)
    elif current > max_pagenum - 10:
        return range(max_pagenum - 10, max_pagenum + 1)
    else:
        return range(current - 5, current + 6)
