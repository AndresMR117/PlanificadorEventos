from django.urls import path
from . import views

urlpatterns = [
    # Auth (MySQL)
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('usuarios/', views.obtener_usuarios, name='usuarios'),
    
    # Proveedores (SPARQL)
    path('proveedores/', views.obtener_proveedores, name='proveedores'),
    path('proveedores/destacados/', views.proveedores_destacados, name='proveedores_destacados'),
    path('proveedores/todos/', views.obtener_todos_proveedores, name='todos_proveedores'),
    path('proveedores/buscar/<str:nombre>/', views.proveedor_por_nombre, name='proveedor_por_nombre'),
    path('proveedores/ciudad/<str:ciudad>/', views.proveedores_por_ciudad, name='proveedores_por_ciudad'),
    path('proveedores/categoria/<str:categoria>/', views.proveedores_por_categoria, name='proveedores_por_categoria'),
    path('proveedores/estadisticas/', views.obtener_proveedores_con_estadisticas, name='proveedores_estadisticas'),
    
    # Tipos de evento (SPARQL)
    path('tipos-evento/', views.obtener_tipos_evento, name='tipos_evento'),
    
    # Categorías (SPARQL)
    path('categorias/', views.obtener_categorias_servicio, name='categorias'),
    
    # Servicios (SPARQL)
    path('servicios/', views.obtener_servicios, name='servicios'),
    path('servicios/tipo/<str:tipo_evento>/', views.servicios_por_tipo, name='servicios_por_tipo'),
    path('servicios/categoria/<str:categoria>/', views.servicios_por_categoria, name='servicios_por_categoria'),
    path('servicios/rango-precio/', views.servicios_por_rango_precio, name='servicios_por_rango_precio'),
    
    # Paquetes (SPARQL)
    path('paquetes/', views.obtener_paquetes, name='paquetes'),
    path('paquetes/tipo/<str:tipo_evento>/', views.paquetes_por_tipo, name='paquetes_por_tipo'),
    
    # Accesorios (SPARQL)
    path('accesorios/', views.obtener_accesorios, name='accesorios'),
    path('accesorios/tipo/<str:tipo_evento>/', views.accesorios_por_tipo, name='accesorios_por_tipo'),
    
    # Ubicaciones (SPARQL)
    path('ubicaciones/', views.obtener_ubicaciones, name='ubicaciones'),
    
    # Factores (SPARQL)
    path('factores-distancia/', views.obtener_factores_distancia, name='factores_distancia'),
    path('temporadas/', views.obtener_temporadas, name='temporadas'),
    
    # Recomendaciones (SPARQL)
    path('recomendaciones/', views.recomendaciones_completas, name='recomendaciones'),
    
    # IA (Groq) - Endpoint principal del chatbot
    path('chatbot/groq/', views.chat_con_groq, name='chatbot_groq'),
    
    # Conversaciones (MySQL)
    path('conversaciones/crear/', views.crear_conversacion, name='crear_conversacion'),
    path('conversaciones/usuario/<int:usuario_id>/', views.obtener_conversaciones_usuario, name='conversaciones_usuario'),
    path('conversaciones/<int:conversacion_id>/', views.obtener_conversacion, name='obtener_conversacion'),
    path('conversaciones/<int:conversacion_id>/mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    
    # Eventos (MySQL) - CRUD completo
    path('eventos/guardar/', views.guardar_evento, name='guardar_evento'),
    path('eventos/usuario/<int:usuario_id>/', views.obtener_eventos_usuario, name='eventos_usuario'),
    path('eventos/<int:evento_id>/', views.obtener_evento, name='obtener_evento'),
    path('eventos/<int:evento_id>/actualizar/', views.actualizar_evento, name='actualizar_evento'),
    path('eventos/<int:evento_id>/eliminar/', views.eliminar_evento, name='eliminar_evento'),
    path('eventos/', views.obtener_todos_eventos, name='todos_eventos'),
    
    # Nuevos endpoints generales
    path('estadisticas/', views.estadisticas_generales, name='estadisticas'),
    path('buscar/', views.buscar_general, name='buscar_general'),
]