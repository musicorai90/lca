from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CARGOS = [
	('A', 'Administrativo'),
	('O', 'Obrero'),
	('P', 'Profesor'),
]

STATUS = [
	('A', 'Activo'),
	('D', 'Dañado'),
]

STATUS_2 = [
	('E', 'En espera'),
	('A', 'Aceptado'),
	('R', 'Rechazado'),
]

BOOLEANO = [
	('S', 'Si'),
	('N', 'No'),
]

DIAS = [
	('LU', 'Lunes'),
	('MA', 'Martes'),
	('MI', 'Miercoles'),
	('JU', 'Jueves'),
	('VI', 'Viernes'),
]

class Tipo_Bien(models.Model):
	nombre = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

class Personal(models.Model):
	cedula = models.CharField(max_length=8, unique=True)
	nombre = models.CharField(max_length=50)
	telefono = models.CharField(max_length=12)
	direccion = models.CharField(max_length=100)
	correo = models.CharField(max_length=50, null=True)
	cargo = models.CharField(max_length=1, choices=CARGOS)
	horas = models.IntegerField(blank=True, null=True)
	salario = models.IntegerField()
	fecha_nacimiento = models.DateField()
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField(blank=True, null=True)
	imagen = models.ImageField(upload_to="media/perfiles", blank=True, null=True)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.nombre

class Departamento(models.Model):
	nombre = models.CharField(max_length=50)
	personal = models.ManyToManyField(Personal, blank=True)

	def __str__(self):
		return self.nombre

class Bien(models.Model):
	nombre = models.CharField(max_length=50)
	status = models.CharField(max_length=1, choices=STATUS)
	fecha = models.DateField()
	tipo = models.ForeignKey(Tipo_Bien, on_delete=models.CASCADE)
	departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

	def __str__(self):
		cadena = "{0} - {1}"
		return cadena.format(self.tipo, self.nombre)

class Reporte(models.Model):
	observacion = models.CharField(max_length=100, null=True, blank=True)
	status = models.CharField(max_length=1, choices=STATUS_2, default="E")
	fecha_inicio = models.DateField(default=timezone.now)
	fecha_fin = models.DateField(null=True, blank=True)
	bien = models.ForeignKey(Bien, on_delete=models.CASCADE)

	def __str__(self):
		return self.bien.nombre

class Permiso(models.Model):
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()
	imagen = models.ImageField(upload_to="media/recipes")
	status = models.CharField(max_length=1, choices=STATUS_2, default="E")
	personal = models.ForeignKey(Personal, on_delete=models.CASCADE)

	def __str__(self):
		return self.personal.nombre

class Memorandum(models.Model):
	observacion = models.CharField(max_length=100)
	fecha = models.DateField()
	personal = models.ForeignKey(Personal, on_delete=models.CASCADE)

	def __str__(self):
		return self.personal.nombre

class Asistencia_Personal(models.Model):
	fecha = models.DateField()
	horas = models.IntegerField()
	personal = models.ForeignKey(Personal, on_delete=models.CASCADE)

	def __str__(self):
		return self.personal.nombre

class Asignatura(models.Model):
	nombre = models.CharField(max_length=100)
	guia = models.CharField(max_length=1, choices=BOOLEANO, default="N")
	personal = models.ForeignKey(Personal, on_delete=models.CASCADE)

	def __str__(self):
		return self.nombre

class Unidad(models.Model):
	descripcion = models.CharField(max_length=100)
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()
	asignatura = models.ForeignKey(Personal, on_delete=models.CASCADE)

	def __str__(self):
		return self.descripcion

class Horario(models.Model):
	dia = models.CharField(max_length=2, choices=DIAS)
	hora_inicio = models.TimeField()
	hora_fin = models.TimeField()
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)

	def __str__(self):
		return self.dia

class Representante(models.Model):
	cedula = models.CharField(max_length=8)
	nombre = models.CharField(max_length=50)
	telefono = models.CharField(max_length=12)
	direccion = models.CharField(max_length=100)

	def __str__(self):
		return self.nombre

class Alumno(models.Model):
	cedula = models.CharField(max_length=8)
	nombre = models.CharField(max_length=50)
	telefono = models.CharField(max_length=12)
	direccion = models.CharField(max_length=100)
	correo = models.CharField(max_length=50, null=True)
	fecha_nacimiento = models.DateField()
	imagen = models.ImageField(upload_to='media/perfiles', null=True)
	representante = models.ForeignKey(Representante, on_delete=models.CASCADE)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.nombre

class Asignatura_Alumno(models.Model):
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
	alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)

	def __str__(self):
		cadena = "{0} - {1}"
		return cadena.format(self.asignatura.nombre, self.alumno.nombre)

class Asistencia_Alumno(models.Model):
	fecha = models.DateField()
	asignatura_alumno = models.ForeignKey(Asignatura_Alumno, on_delete=models.CASCADE)

	def __str__(self):
		return self.asignatura_alumno.__str__()

class Evaluacion(models.Model):
	nombre = models.CharField(max_length=50)
	nota = models.IntegerField()
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()

	def __str__(self):
		return self.nombre

class Evaluacion_Alumno(models.Model):
	nota = models.IntegerField()
	fecha = models.DateField()
	asignatura_alumno = models.ForeignKey(Asignatura_Alumno, on_delete=models.CASCADE)
	evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)

	def __str__(self):
		cadena = "{0} - {1}"
		return cadena.format(self.asignatura_alumno.__str__(), self.evaluacion.nombre)

class Tipo_Solicitud(models.Model):
	nombre = models.CharField(max_length=50)
	costo = models.IntegerField()

	def __str__(self):
		return self.nombre

class Solicitud(models.Model):
	referencia = models.IntegerField()
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()
	tipo = models.ForeignKey(Tipo_Solicitud, on_delete=models.CASCADE)
	alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)

	def __str__(self):
		cadena = "{0} - {1}"
		return cadena.format(self.tipo.nombre, self.alumno.nombre)

class Libro(models.Model):
	nombre = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

class Prestamo(models.Model):
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()
	observacion = models.CharField(max_length=100)
	libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
	alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)

	def __str__(self):
		cadena = "{0} - {1}"
		return cadena.format(self.libro.nombre, self.alumno.nombre)