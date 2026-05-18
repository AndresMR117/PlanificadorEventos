from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'rol', 'plan', 'activo')
    search_fields = ('nombre', 'email')
    list_filter = ('rol', 'plan', 'activo')