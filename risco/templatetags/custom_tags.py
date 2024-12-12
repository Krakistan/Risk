from django import template

register = template.Library()

@register.filter
def clp_format(value):
    """Convierte un valor numérico a formato CLP (pesos chilenos)."""
    return f"${value:,.0f}".replace(",", ".")
