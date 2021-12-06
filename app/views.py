from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.http import HttpResponse

from .utils import render_to_pdf

from django.contrib.auth.models import User, Group
from . import models

from braces.views import LoginRequiredMixin, GroupRequiredMixin

import datetime

class Index(LoginRequiredMixin, TemplateView):
	template_name = "index.html"

class Perfil(LoginRequiredMixin, DetailView):
	template_name = "perfil.html"

	def get_object(self):
		grupo = self.request.user.groups.all()[0].name
		if grupo == "alumno":
			return get_object_or_404(models.Alumno, usuario_id=self.request.user.id)
		else:
			return get_object_or_404(models.Personal, usuario_id=self.request.user.id)

class EditarPerfil(LoginRequiredMixin, UpdateView):
	template_name = "editar.html"
	fields = ['cedula','nombre','telefono','fecha_nacimiento','direccion','correo','imagen']
	success_url = "/perfil/"

	def get_object(self):
		grupo = self.request.user.groups.all()[0].name
		if grupo == "alumno":
			return get_object_or_404(models.Alumno, usuario_id=self.request.user.id)
		else:
			return get_object_or_404(models.Personal, usuario_id=self.request.user.id)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['grupo'] = self.request.user.groups.all()[0].name
		return context

	def form_valid(self, form):
		obj = form.save(commit=False)
		if obj.cedula != self.request.user.username:
			if len(User.objects.filter(username=obj.cedula)):
				messages.add_message(self.request, messages.INFO, 'Ya esta cédula está registrada.')
			else:
				usuario = User.objects.get(id=self.request.user.id)
				usuario.username = obj.cedula
				usuario.save()
				obj.save()
		else:
			obj.save()
		return super().form_valid(form)

class TipoBien(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "tipo_bien/index.html"
	model = models.Tipo_Bien

class AgregarTipoBien(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "tipo_bien/agregar.html"
	model = models.Tipo_Bien
	fields = ['nombre']
	success_url = "/tipo_bien/"
	success_message = "Creado con éxito."

class VerTipoBien(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "tipo_bien/ver.html"
	model = models.Tipo_Bien

class EditarTipoBien(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "tipo_bien/editar.html"
	model = models.Tipo_Bien
	fields = ['nombre']
	success_url = "/tipo_bien/"
	success_message = "Editado con éxito."

class EliminarTipoBien(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Tipo_Bien
	success_url = "/tipo_bien/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class Personal(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "personal/index.html"
	model = models.Personal

class AgregarPersonal(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "personal/agregar.html"
	model = models.Personal
	fields = ['cedula','nombre','telefono','cargo','direccion','correo','salario','fecha_nacimiento','fecha_inicio','horas','imagen']
	success_url = "/personal/"
	success_message = "Creado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		if obj.cargo == 'P' and obj.horas is None:
			messages.add_message(self.request, messages.INFO, 'Los profesores deben tener horas asignadas.')
			return redirect('/personal/agregar/')
		usuario = User.objects.create_user(obj.cedula, obj.correo, obj.cedula)
		grupo = Group.objects.get(name=obj.get_cargo_display().casefold())
		grupo.user_set.add(usuario)
		obj.usuario_id = usuario.id
		obj.save()
		return super().form_valid(form)

class VerPersonal(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "personal/ver.html"
	model = models.Personal

class EditarPersonal(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "personal/editar.html"
	model = models.Personal
	fields = ['cedula','nombre','telefono','cargo','direccion','correo','salario','fecha_nacimiento','fecha_inicio','imagen','horas']
	success_url = "/personal/"
	success_message = "Editado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		if len(User.objects.filter(username=obj.cedula)) == 0:
			usuario = User.objects.get(id=obj.usuario.id)
			usuario.username = obj.cedula
			usuario.save()
			obj.save()
		if obj.cargo != 'P':
			obj.horas = None
		usuario = User.objects.get(id=obj.usuario.id)
		usuario_grupo = User.groups.through.objects.get(user=usuario)
		grupo = Group.objects.get(name=obj.get_cargo_display().casefold())
		usuario_grupo.group = grupo
		usuario_grupo.save()
		return super().form_valid(form)

class DesincorporarPersonal(GroupRequiredMixin, View):
	group_required = u'secretario'

	def get(self, request, *args, **kwargs):
		self.object = get_object_or_404(models.Personal, id=kwargs['personal_id'])
		self.object.fecha_fin = datetime.datetime.now()
		self.object.save()
		messages.add_message(self.request, messages.INFO, 'Desincorporado con éxito.')
		return redirect('/personal/')

class IncorporarPersonal(GroupRequiredMixin, View):
	group_required = u'secretario'

	def get(self, request, *args, **kwargs):
		self.object = get_object_or_404(models.Personal, id=kwargs['personal_id'])
		self.object.fecha_fin = None
		self.object.save()
		messages.add_message(self.request, messages.INFO, 'Incorporado con éxito.')
		return redirect('/personal/')

class Departamento(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "departamento/index.html"
	model = models.Departamento

class AgregarDepartamento(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "departamento/agregar.html"
	model = models.Departamento
	fields = ['nombre','personal']
	success_url = "/departamento/"
	success_message = "Creado con éxito."

class VerDepartamento(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "departamento/ver.html"
	model = models.Departamento

class EditarDepartamento(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "departamento/editar.html"
	model = models.Departamento
	fields = ['nombre','personal']
	success_url = "/departamento/"
	success_message = "Editado con éxito."

class Bien(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "bien/index.html"
	model = models.Bien

class AgregarBien(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "bien/agregar.html"
	model = models.Bien
	fields = ['nombre','status','fecha','tipo','departamento']
	success_url = "/bien/"
	success_message = "Creado con éxito."

class VerBien(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "bien/ver.html"
	model = models.Bien

class EditarBien(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "bien/editar.html"
	model = models.Bien
	fields = ['nombre','status','fecha','tipo','departamento']
	success_url = "/bien/"
	success_message = "Editado con éxito."

class EliminarBien(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Bien
	success_url = "/bien/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class Reporte(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "reporte/index.html"
	model = models.Reporte

class AgregarReporte(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = [u'profesor']
	template_name = "reporte/agregar.html"
	model = models.Reporte
	fields = ['bien']
	success_url = "/reporte/"
	success_message = "Creado con éxito."

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		usuario = models.Personal.objects.filter(cedula=self.request.user.username)[0]
		departamento = models.Departamento.objects.filter(personal=usuario)[0]
		context['form'].fields['bien'].queryset = models.Bien.objects.filter(departamento=departamento)
		return context

class VerReporte(GroupRequiredMixin, DetailView):
	group_required = [u'secretario', u'profesor']
	template_name = "reporte/ver.html"
	model = models.Reporte

class EditarReporte(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "reporte/editar.html"
	model = models.Reporte
	fields = ['observacion','status']
	success_url = "/reporte/"
	success_message = "Editado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		if obj.status != 'E':
			obj.fecha_fin = timezone.now()
		if obj.status == 'A':
			obj.bien.status = "D"
			obj.bien.save()
		obj.save()
		return super().form_valid(form)

class Permiso(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'administrativo', u'profesor', u'obrero']
	template_name = "permiso/index.html"
	model = models.Permiso

class AgregarSecretarioPermiso(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = [u'secretario']
	template_name = "permiso/agregar_secretario.html"
	model = models.Permiso
	fields = ['fecha_inicio','fecha_fin','personal','imagen']
	success_url = "/permiso/"
	success_message = "Creado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		obj.status = "A"
		obj.save()
		return super().form_valid(form)

class AgregarPersonalPermiso(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = [u'administrativo', u'profesor', u'obrero']
	template_name = "permiso/agregar_personal.html"
	model = models.Permiso
	fields = ['fecha_inicio','fecha_fin','imagen']
	success_url = "/permiso/"
	success_message = "Creado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		obj.personal = models.Personal.objects.filter(cedula=self.request.user.username)[0]
		obj.save()
		return super().form_valid(form)

class VerPermiso(GroupRequiredMixin, DetailView):
	group_required = [u'secretario', u'administrativo', u'profesor', u'obrero']
	template_name = "permiso/ver.html"
	model = models.Permiso

class EditarPermiso(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "permiso/editar.html"
	model = models.Permiso
	fields = ['fecha_inicio','fecha_fin','status']
	success_url = "/permiso/"
	success_message = "Respondido con éxito."

class Memorandum(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'administrativo', u'profesor', u'obrero']
	template_name = "memorandum/index.html"
	model = models.Memorandum

class AgregarMemorandum(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "memorandum/agregar.html"
	model = models.Memorandum
	fields = ['personal','fecha','observacion']
	success_url = "/memorandum/"
	success_message = "Creado con éxito."

class VerMemorandum(GroupRequiredMixin, DetailView):
	group_required = [u'secretario', u'administrativo', u'profesor', u'obrero']
	template_name = "memorandum/ver.html"
	model = models.Memorandum

class EditarMemorandum(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "memorandum/editar.html"
	model = models.Memorandum
	fields = ['personal','fecha','observacion']
	success_url = "/memorandum/"
	success_message = "Editado con éxito."

class EliminarMemorandum(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Memorandum
	success_url = "/memorandum/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class AsistenciaPersonal(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "asistencia_personal/index.html"
	model = models.Asistencia_Personal

class AgregarAsistenciaPersonal(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "asistencia_personal/agregar.html"
	model = models.Asistencia_Personal
	fields = ['personal','fecha','horas']
	success_url = "/asistencia_personal/"
	success_message = "Creado con éxito."

class EditarAsistenciaPersonal(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "asistencia_personal/editar.html"
	model = models.Asistencia_Personal
	fields = ['personal','fecha','horas']
	success_url = "/asistencia_personal/"
	success_message = "Editado con éxito."

class EliminarAsistenciaPersonal(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Asistencia_Personal
	success_url = "/asistencia_personal/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class Asignatura(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "asignatura/index.html"
	model = models.Asignatura

class AgregarAsignatura(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "asignatura/agregar.html"
	model = models.Asignatura
	fields = ['nombre','personal','guia']
	success_url = "/asignatura/"
	success_message = "Creado con éxito."

class VerAsignatura(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "asignatura/ver.html"
	model = models.Asignatura

class EditarAsignatura(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "asignatura/editar.html"
	model = models.Asignatura
	fields = ['nombre','personal','guia']
	success_url = "/asignatura/"
	success_message = "Editado con éxito."

class Horario(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "horario/index.html"
	model = models.Horario

class AgregarHorario(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "horario/agregar.html"
	model = models.Horario
	fields = ['asignatura','dia','hora_inicio','hora_fin']
	success_url = "/horario/"
	success_message = "Creado con éxito."

class VerHorario(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "horario/ver.html"
	model = models.Horario

class EditarHorario(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "horario/editar.html"
	model = models.Horario
	fields = ['asignatura','dia','hora_inicio','hora_fin']
	success_url = "/horario/"
	success_message = "Editado con éxito."

class EliminarHorario(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Horario
	success_url = "/horario/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class Representante(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "representante/index.html"
	model = models.Representante

class AgregarRepresentante(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "representante/agregar.html"
	model = models.Representante
	fields = ['cedula','nombre','telefono','direccion']
	success_url = "/representante/"
	success_message = "Creado con éxito."

class VerRepresentante(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "representante/ver.html"
	model = models.Representante

class EditarRepresentante(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "representante/editar.html"
	model = models.Representante
	fields = ['cedula','nombre','telefono','direccion']
	success_url = "/representante/"
	success_message = "Editado con éxito."

class Alumno(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "alumno/index.html"
	model = models.Alumno

class AgregarAlumno(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "alumno/agregar.html"
	model = models.Alumno
	fields = ['cedula','nombre','telefono','direccion','correo','fecha_nacimiento','representante','imagen']
	success_url = "/alumno/"
	success_message = "Creado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		usuario = User.objects.create_user(obj.cedula, obj.correo, obj.cedula)
		grupo = Group.objects.get(name="alumno")
		grupo.user_set.add(usuario)
		obj.usuario_id = usuario.id
		obj.save()
		return super().form_valid(form)

class VerAlumno(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "alumno/ver.html"
	model = models.Alumno

class EditarAlumno(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "alumno/editar.html"
	model = models.Alumno
	fields = ['cedula','nombre','telefono','direccion','correo','fecha_nacimiento','representante','imagen']
	success_url = "/alumno/"
	success_message = "Editado con éxito."

	def form_valid(self, form):
		obj = form.save(commit=False)
		if len(User.objects.filter(username=obj.cedula)) == 0:
			usuario = User.objects.get(id=obj.usuario.id)
			usuario.username = obj.cedula
			usuario.save()
		obj.save()
		return super().form_valid(form)

class AsignaturaAlumno(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "asignatura_alumno/index.html"
	model = models.Asignatura_Alumno

class AgregarAsignaturaAlumno(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "asignatura_alumno/agregar.html"
	model = models.Asignatura_Alumno
	fields = ['asignatura','alumno']
	success_url = "/asignatura_alumno/"
	success_message = "Creado con éxito."

class EditarAsignaturaAlumno(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "asignatura_alumno/editar.html"
	model = models.Asignatura_Alumno
	fields = ['asignatura','alumno']
	success_url = "/asignatura_alumno/"
	success_message = "Editado con éxito."

class EliminarAsignaturaAlumno(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'secretario'
	model = models.Asignatura_Alumno
	success_url = "/asignatura_alumno/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class AsistenciaAlumno(GroupRequiredMixin, ListView):
	group_required = [u'secretario', u'profesor']
	template_name = "asistencia_alumno/index.html"
	model = models.Asistencia_Alumno

class AgregarAsistenciaAlumno(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'profesor'
	template_name = "asistencia_alumno/agregar.html"
	model = models.Asistencia_Alumno
	fields = ['asignatura_alumno','fecha']
	success_url = "/asistencia_alumno/"
	success_message = "Creado con éxito."

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		usuario = models.Personal.objects.filter(cedula=self.request.user.username)[0]
		asignatura = models.Asignatura.objects.filter(personal=usuario)
		aa = models.Asignatura_Alumno.objects.none()
		for a in asignatura:
			aa = aa | models.Asignatura_Alumno.objects.filter(asignatura=a)
		context['form'].fields['asignatura_alumno'].queryset = aa
		return context

class EditarAsistenciaAlumno(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'profesor'
	template_name = "asistencia_alumno/editar.html"
	model = models.Asistencia_Alumno
	fields = ['asignatura_alumno','fecha']
	success_url = "/asistencia_alumno/"
	success_message = "Editado con éxito."

class EliminarAsistenciaAlumno(SuccessMessageMixin, GroupRequiredMixin, DeleteView):
	group_required = u'profesor'
	model = models.Asistencia_Alumno
	success_url = "/asistencia_alumno/"

	def get(self, *args, **kwargs):
		messages.add_message(self.request, messages.INFO, 'Eliminado con éxito.')
		return self.post(*args, **kwargs)

class Actividad(GroupRequiredMixin, ListView):
	group_required = u'secretario'
	template_name = "actividad/index.html"
	model = models.Actividad

class AgregarActividad(SuccessMessageMixin, GroupRequiredMixin, CreateView):
	group_required = u'secretario'
	template_name = "actividad/agregar.html"
	model = models.Actividad
	fields = ['fecha', 'descripcion', 'participantes']
	success_url = "/actividad/"
	success_message = "Creado con éxito."

class VerActividad(GroupRequiredMixin, DetailView):
	group_required = u'secretario'
	template_name = "actividad/ver.html"
	model = models.Actividad

class EditarActividad(SuccessMessageMixin, GroupRequiredMixin, UpdateView):
	group_required = u'secretario'
	template_name = "actividad/editar.html"
	model = models.Actividad
	fields = ['fecha', 'descripcion', 'participantes']
	success_url = "/actividad/"
	success_message = "Editado con éxito."

def personal_pdf(request):
	template = 'pdf/personal.html'
	context = {'personal': models.Personal.objects.all()}
	pdf = render_to_pdf(template, context)
	if pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "personal.pdf"
		content = "inline; filename='%s'" % filename
		download = request.GET.get("download")
		if download:
			content = "attachment; filename='%s'" % filename
		response['Content-Disposition'] = content
		return response
	return HttpResponse("Not found")