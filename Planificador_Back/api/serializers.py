from rest_framework import serializers
from .models import Usuario, Conversacion, Evento

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'telefono', 'rol', 'plan', 'activo', 'created_at']


class ConversacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    
    class Meta:
        model = Conversacion
        fields = ['id', 'usuario', 'usuario_nombre', 'titulo', 'tipo_evento_uri', 
                  'num_personas', 'presupuesto', 'estado', 'historial_json', 
                  'plan_json', 'created_at', 'updated_at']


class EventoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    conversacion_titulo = serializers.CharField(source='conversacion.titulo', read_only=True)
    
    class Meta:
        model = Evento
        fields = ['id', 'usuario', 'usuario_nombre', 'conversacion', 'conversacion_titulo',
                  'nombre', 'tipo_evento', 'fecha_evento', 'num_personas', 
                  'presupuesto_total', 'ciudad', 'estado', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']