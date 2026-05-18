from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('cliente', 'Cliente'),
        ('proveedor', 'Proveedor'),
        ('admin', 'Administrador'),
    ]
    PLANES = [
        ('free', 'Free'),
        ('basico', 'Básico'),
        ('premium', 'Premium'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    email = models.CharField(max_length=191, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, blank=True, null=True, default='cliente')
    plan = models.CharField(max_length=20, blank=True, null=True, default='free')
    activo = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'usuarios'
    
    def __str__(self):
        return self.nombre


class Conversacion(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('planificando', 'Planificando'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    titulo = models.CharField(max_length=200, blank=True)
    tipo_evento_uri = models.CharField(max_length=255, blank=True)
    num_personas = models.IntegerField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='activa')
    historial_json = models.JSONField(default=list)
    plan_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'conversaciones'
    
    def __str__(self):
        return f"{self.titulo or 'Conversación'} - {self.usuario.nombre}"


class Evento(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('planificando', 'Planificando'),
        ('confirmado', 'Confirmado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPOS = [
        ('Boda', 'Boda'),
        ('Cumpleaños', 'Cumpleaños'),
        ('Grado', 'Grado'),
        ('Quinceañera', 'Quinceañera'),
        ('BabyShower', 'Baby Shower'),
        ('FiestaInfantil', 'Fiesta Infantil'),
        ('Despedida', 'Despedida'),
        ('Aniversario', 'Aniversario'),
        ('EventoCorporativo', 'Evento Corporativo'),
    ]
    
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    conversacion = models.ForeignKey(Conversacion, on_delete=models.SET_NULL, null=True, blank=True, db_column='conversacion_id')
    nombre = models.CharField(max_length=200)
    tipo_evento = models.CharField(max_length=50, choices=TIPOS)
    fecha_evento = models.DateField(null=True, blank=True)
    num_personas = models.IntegerField(default=0)
    presupuesto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ciudad = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='borrador')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'eventos'
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.nombre}"