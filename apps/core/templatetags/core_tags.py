"""
Core Template Tags and Filters.

Custom template tags and filters used across all templates.
Load in templates with: {% load core_tags %}

Tags:
    active_link: Returns 'active' CSS class for sidebar navigation.
    format_wait: Formats minutes into human-readable wait time.

Filters:
    status_badge: Returns Bootstrap badge class for queue status.
    role_badge: Returns Bootstrap badge class for user role.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class='active'):
    """
    Return the active CSS class if the current URL matches the given URL name.

    Usage in templates:
        <a class="nav-link {% active_link 'dashboard:home' %}">Dashboard</a>
    """
    try:
        request = context['request']
        if request.resolver_match and request.resolver_match.url_name == url_name:
            return css_class
        # Also check the full namespaced URL name
        if request.resolver_match:
            full_name = f'{request.resolver_match.namespace}:{request.resolver_match.url_name}'
            if full_name == url_name:
                return css_class
    except (KeyError, AttributeError):
        pass
    return ''


@register.simple_tag(takes_context=True)
def active_link_startswith(context, url_prefix, css_class='active'):
    """
    Return active class if the current URL path starts with the given prefix.

    Usage:
        <a class="nav-link {% active_link_startswith '/queues/' %}">Queues</a>
    """
    try:
        request = context['request']
        if request.path.startswith(url_prefix):
            return css_class
    except (KeyError, AttributeError):
        pass
    return ''


@register.filter(name='status_badge')
def status_badge(status):
    """
    Return a Bootstrap badge HTML for a queue token status.

    Usage in templates:
        {{ token.status|status_badge }}
    """
    badges = {
        'WAITING': '<span class="badge bg-warning text-dark"><i class="fas fa-clock me-1"></i>Waiting</span>',
        'CALLED': '<span class="badge bg-info"><i class="fas fa-bullhorn me-1"></i>Called</span>',
        'SERVING': '<span class="badge bg-primary"><i class="fas fa-user-check me-1"></i>Serving</span>',
        'COMPLETED': '<span class="badge bg-success"><i class="fas fa-check-circle me-1"></i>Completed</span>',
        'CANCELLED': '<span class="badge bg-danger"><i class="fas fa-times-circle me-1"></i>Cancelled</span>',
        'NO_SHOW': '<span class="badge bg-secondary"><i class="fas fa-user-slash me-1"></i>No Show</span>',
        'ON_HOLD': '<span class="badge bg-dark"><i class="fas fa-pause-circle me-1"></i>On Hold</span>',
    }
    return mark_safe(badges.get(status, f'<span class="badge bg-secondary">{status}</span>'))


@register.filter(name='role_badge')
def role_badge(role):
    """
    Return a Bootstrap badge HTML for a user role.

    Usage in templates:
        {{ user.role|role_badge }}
    """
    badges = {
        'ADMIN': '<span class="badge bg-danger"><i class="fas fa-shield-alt me-1"></i>Admin</span>',
        'STAFF': '<span class="badge bg-primary"><i class="fas fa-user-tie me-1"></i>Staff</span>',
        'USER': '<span class="badge bg-success"><i class="fas fa-user me-1"></i>User</span>',
    }
    return mark_safe(badges.get(role, f'<span class="badge bg-secondary">{role}</span>'))


@register.filter(name='format_wait')
def format_wait(minutes):
    """
    Format minutes into a human-readable wait time.

    Usage in templates:
        {{ token.estimated_wait_minutes|format_wait }}
    """
    from core.utils import format_wait_time
    return format_wait_time(minutes)


@register.filter(name='star_rating')
def star_rating(value):
    """
    Render star icons for a rating value (1-5).

    Usage in templates:
        {{ feedback.rating|star_rating }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return ''

    stars = ''
    for i in range(1, 6):
        if i <= value:
            stars += '<i class="fas fa-star text-warning"></i>'
        else:
            stars += '<i class="far fa-star text-warning"></i>'
    return mark_safe(stars)


@register.inclusion_tag('includes/pagination.html', takes_context=True)
def render_pagination(context, page_obj):
    """
    Render pagination controls.

    Usage in templates:
        {% render_pagination page_obj %}
    """
    return {
        'page_obj': page_obj,
        'request': context['request'],
    }
