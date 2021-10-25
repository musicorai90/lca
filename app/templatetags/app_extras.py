from django import template
from app.models import Personal, Alumno

register = template.Library()

@register.simple_tag
def get_user_lca(usuario):
	grupo = usuario.groups.all()[0].name
	if grupo == 'alumno':
		return Alumno.objects.get(usuario_id=usuario.id)
	else:
		return Personal.objects.get(usuario_id=usuario.id)

@register.simple_tag
def get_grupo_lca(grupos):
	return grupos.all()[0].name