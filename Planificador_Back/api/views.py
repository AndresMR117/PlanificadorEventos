from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario, Conversacion, Evento
from .services.sparql_service import SPARQLService
from .services.groq_service import GroqService
import hashlib
import re
from django.utils import timezone

# Inicializar servicios
groq = GroqService()
sparql = SPARQLService()


# ==================== AUTENTICACIÓN (MySQL) ====================

@api_view(['POST'])
def registro(request):
    nombre = request.data.get('nombre')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not nombre or not email or not password:
        return Response({'error': 'Todos los campos son obligatorios'}, status=400)
    
    if len(password) < 8:
        return Response({'error': 'La contraseña debe tener al menos 8 caracteres'}, status=400)
    
    if Usuario.objects.filter(email=email).exists():
        return Response({'error': 'Email ya registrado'}, status=400)
    
    usuario = Usuario.objects.create(
        nombre=nombre,
        email=email,
        password_hash=hashlib.sha256(password.encode()).hexdigest(),
        rol='cliente',
        activo=1
    )
    
    return Response({
        'id': usuario.id,
        'nombre': usuario.nombre,
        'email': usuario.email,
        'rol': usuario.rol
    }, status=201)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email y contraseña son obligatorios'}, status=400)
    
    try:
        usuario = Usuario.objects.get(email=email, activo=1)
        if usuario.password_hash == hashlib.sha256(password.encode()).hexdigest():
            return Response({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'rol': usuario.rol
            })
    except Usuario.DoesNotExist:
        pass
    
    return Response({'error': 'Credenciales inválidas'}, status=401)


@api_view(['GET'])
def obtener_usuarios(request):
    usuarios = Usuario.objects.all()
    data = [{
        'id': u.id,
        'nombre': u.nombre,
        'email': u.email,
        'rol': u.rol,
        'activo': u.activo,
        'created_at': u.created_at
    } for u in usuarios]
    return Response(data)


# ==================== PROVEEDORES (SPARQL) ====================

@api_view(['GET'])
def obtener_proveedores(request):
    proveedores = sparql.obtener_proveedores()
    return Response(proveedores)


@api_view(['GET'])
def proveedores_destacados(request):
    proveedores = sparql.obtener_proveedores_destacados()
    return Response(proveedores)


@api_view(['GET'])
def obtener_todos_proveedores(request):
    proveedores = sparql.obtener_proveedores()
    return Response(proveedores)


@api_view(['GET'])
def proveedor_por_nombre(request, nombre):
    proveedores = sparql.obtener_proveedor_por_nombre(nombre)
    return Response(proveedores)


@api_view(['GET'])
def proveedores_por_ciudad(request, ciudad):
    proveedores = sparql.obtener_proveedores_por_ciudad(ciudad)
    return Response(proveedores)


@api_view(['GET'])
def proveedores_por_categoria(request, categoria):
    proveedores = sparql.obtener_proveedores_por_categoria(categoria)
    return Response(proveedores)


# ==================== TIPOS DE EVENTO (SPARQL) ====================

@api_view(['GET'])
def obtener_tipos_evento(request):
    tipos = sparql.obtener_tipos_evento()
    return Response(tipos)


# ==================== CATEGORÍAS (SPARQL) ====================

@api_view(['GET'])
def obtener_categorias_servicio(request):
    categorias = sparql.obtener_categorias_servicio()
    return Response(categorias)


# ==================== SERVICIOS (SPARQL) ====================

@api_view(['GET'])
def obtener_servicios(request):
    servicios = sparql.obtener_servicios()
    return Response(servicios)


@api_view(['GET'])
def servicios_por_tipo(request, tipo_evento):
    servicios = sparql.obtener_servicios_por_tipo(tipo_evento)
    return Response(servicios)


@api_view(['GET'])
def servicios_por_categoria(request, categoria):
    servicios = sparql.obtener_servicios_por_categoria(categoria)
    return Response(servicios)


@api_view(['GET'])
def servicios_por_rango_precio(request):
    min_precio = request.query_params.get('min', 0)
    max_precio = request.query_params.get('max', 10000000)
    servicios = sparql.obtener_servicios_por_rango_precio(float(min_precio), float(max_precio))
    return Response(servicios)


# ==================== PAQUETES (SPARQL) ====================

@api_view(['GET'])
def obtener_paquetes(request):
    paquetes = sparql.obtener_paquetes()
    return Response(paquetes)


@api_view(['GET'])
def paquetes_por_tipo(request, tipo_evento):
    paquetes = sparql.obtener_paquetes_por_tipo(tipo_evento)
    return Response(paquetes)


# ==================== ACCESORIOS (SPARQL) ====================

@api_view(['GET'])
def obtener_accesorios(request):
    accesorios = sparql.obtener_accesorios()
    return Response(accesorios)


@api_view(['GET'])
def accesorios_por_tipo(request, tipo_evento):
    accesorios = sparql.obtener_accesorios_por_tipo(tipo_evento)
    return Response(accesorios)


# ==================== UBICACIONES (SPARQL) ====================

@api_view(['GET'])
def obtener_ubicaciones(request):
    ubicaciones = sparql.obtener_ubicaciones()
    return Response(ubicaciones)


# ==================== FACTORES (SPARQL) ====================

@api_view(['GET'])
def obtener_factores_distancia(request):
    factores = sparql.obtener_factores_distancia()
    return Response(factores)


@api_view(['GET'])
def obtener_temporadas(request):
    temporadas = sparql.obtener_temporadas()
    return Response(temporadas)


# ==================== RECOMENDACIONES (SPARQL) ====================

@api_view(['GET'])
def recomendaciones_completas(request):
    tipo_evento = request.query_params.get('tipo', 'Boda')
    presupuesto_max = request.query_params.get('presupuesto_max')
    ciudad = request.query_params.get('ciudad')
    
    if presupuesto_max:
        presupuesto_max = float(presupuesto_max)
    
    recomendaciones = sparql.generar_recomendaciones_completas(tipo_evento, presupuesto_max, ciudad)
    return Response(recomendaciones)


# ==================== CONSULTAS COMBINADAS (SPARQL + MySQL) ====================

@api_view(['GET'])
def obtener_proveedores_con_estadisticas(request):
    proveedores = sparql.obtener_proveedores()
    
    for p in proveedores:
        nombre = p.get('nombre', '')
        p['menciones'] = Conversacion.objects.filter(
            historial_json__icontains=nombre
        ).count()
    
    return Response(proveedores)


# ==================== CHATBOT PRINCIPAL (CON EXTRACCIÓN DE DATOS) ====================

@api_view(['POST'])
def chat_con_groq(request):
    """
    Chatbot donde la IA gestiona la conversación.
    """
    mensaje = request.data.get('mensaje')
    conversacion_id = request.data.get('conversacion_id')
    usuario_id = request.data.get('usuario_id')
    
    print(f"\n[DEBUG] Mensaje recibido: {mensaje}")
    print(f"[DEBUG] Conversacion ID: {conversacion_id}")
    print(f"[DEBUG] Usuario ID: {usuario_id}")
    
    # Obtener o crear la conversación
    conversacion = None
    if conversacion_id:
        try:
            conversacion = Conversacion.objects.get(id=conversacion_id)
        except Conversacion.DoesNotExist:
            pass
    
    if not conversacion and usuario_id:
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            conversacion = Conversacion.objects.create(
                usuario=usuario,
                titulo="Chat con IA",
                historial_json=[]
            )
            print(f"[DEBUG] Conversación creada: {conversacion.id}")
        except Usuario.DoesNotExist:
            print("[DEBUG] Usuario no encontrado")
    
    # Construir contexto con el historial
    contexto = ""
    if conversacion and conversacion.historial_json:
        ultimos = conversacion.historial_json[-6:] if len(conversacion.historial_json) > 6 else conversacion.historial_json
        for msg in ultimos:
            rol = "Usuario" if msg.get('rol') == 'user' else "Asistente"
            contexto += f"{rol}: {msg.get('mensaje', '')}\n"
        print(f"[DEBUG] Contexto construido: {contexto[:200]}...")
    
    # Obtener respuesta de la IA
    respuesta_ia = groq.generar_respuesta(mensaje, contexto, usuario_id)
    print(f"[DEBUG] Respuesta IA: {respuesta_ia[:100]}...")
    
    # Guardar en el historial
    if conversacion:
        historial = conversacion.historial_json or []
        historial.append({
            'rol': 'user',
            'mensaje': mensaje,
            'timestamp': str(timezone.now())
        })
        historial.append({
            'rol': 'assistant',
            'mensaje': respuesta_ia,
            'timestamp': str(timezone.now())
        })
        conversacion.historial_json = historial
        conversacion.updated_at = timezone.now()
        conversacion.save()
    
    return Response({'respuesta': respuesta_ia})


# ==================== ENVIAR MENSAJE (para conversaciones existentes) ====================

@api_view(['POST'])
def enviar_mensaje(request, conversacion_id):
    """Enviar un mensaje a una conversación existente"""
    try:
        conversacion = Conversacion.objects.get(id=conversacion_id)
    except Conversacion.DoesNotExist:
        return Response({'error': 'Conversación no encontrada'}, status=404)
    
    mensaje = request.data.get('mensaje', '')
    
    if not mensaje:
        return Response({'error': 'El mensaje no puede estar vacío'}, status=400)
    
    # Construir contexto con el historial reciente
    contexto = ""
    historial = conversacion.historial_json or []
    ultimos = historial[-10:] if len(historial) > 10 else historial
    for msg in ultimos:
        rol = "Usuario" if msg.get('rol') == 'user' else "Asistente"
        contexto += f"{rol}: {msg.get('mensaje', '')}\n"
    
    # Obtener respuesta de la IA
    respuesta_ia = groq.generar_respuesta(mensaje, contexto, conversacion.usuario.id)
    
    # Guardar en el historial
    historial.append({
        'rol': 'user',
        'mensaje': mensaje,
        'timestamp': str(timezone.now())
    })
    historial.append({
        'rol': 'assistant',
        'mensaje': respuesta_ia,
        'timestamp': str(timezone.now())
    })
    
    conversacion.historial_json = historial
    conversacion.updated_at = timezone.now()
    conversacion.save()
    
    return Response({
        'respuesta': respuesta_ia,
        'historial': historial
    })


# ==================== EVENTOS (MySQL) ====================

@api_view(['POST'])
def guardar_evento(request):
    """Guardar evento final desde el chatbot"""
    data = request.data
    
    campos_requeridos = ['usuario_id', 'nombre', 'tipo_evento', 'fecha_evento', 'num_personas', 'presupuesto_total', 'ciudad']
    campos_faltantes = []
    
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or data[campo] == '':
            campos_faltantes.append(campo)
    
    if campos_faltantes:
        return Response({
            'error': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        usuario = Usuario.objects.get(id=data['usuario_id'])
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    tipos_validos = [t[0] for t in Evento.TIPOS]
    if data['tipo_evento'] not in tipos_validos:
        return Response({'error': f'Tipo de evento no válido'}, status=400)
    
    try:
        num_personas = int(data['num_personas'])
        if num_personas <= 0:
            return Response({'error': 'El número de personas debe ser mayor a 0'}, status=400)
    except (ValueError, TypeError):
        return Response({'error': 'Número de personas inválido'}, status=400)
    
    try:
        presupuesto_total = float(data['presupuesto_total'])
        if presupuesto_total < 0:
            return Response({'error': 'El presupuesto no puede ser negativo'}, status=400)
    except (ValueError, TypeError):
        return Response({'error': 'Presupuesto inválido'}, status=400)
    
    try:
        evento = Evento.objects.create(
            usuario_id=data['usuario_id'],
            conversacion_id=data.get('conversacion_id'),
            nombre=data['nombre'],
            tipo_evento=data['tipo_evento'],
            fecha_evento=data.get('fecha_evento'),
            num_personas=num_personas,
            presupuesto_total=presupuesto_total,
            ciudad=data.get('ciudad', ''),
            estado='planificando'
        )
        
        if data.get('conversacion_id'):
            try:
                conversacion = Conversacion.objects.get(id=data['conversacion_id'])
                conversacion.estado = 'confirmada'
                conversacion.num_personas = num_personas
                conversacion.presupuesto = presupuesto_total
                conversacion.save()
            except Conversacion.DoesNotExist:
                pass
        
        return Response({
            'success': True,
            'id': evento.id,
            'mensaje': '✅ ¡Evento guardado exitosamente!',
            'evento': {
                'id': evento.id,
                'nombre': evento.nombre,
                'tipo_evento': evento.tipo_evento,
                'fecha_evento': evento.fecha_evento,
                'num_personas': evento.num_personas,
                'presupuesto_total': float(evento.presupuesto_total),
                'ciudad': evento.ciudad,
                'estado': evento.estado,
                'created_at': evento.created_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Error al guardar evento: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_eventos_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    
    eventos = Evento.objects.filter(usuario_id=usuario_id).order_by('-created_at')
    data = [{
        'id': e.id,
        'nombre': e.nombre,
        'tipo_evento': e.tipo_evento,
        'fecha_evento': e.fecha_evento,
        'num_personas': e.num_personas,
        'presupuesto_total': float(e.presupuesto_total) if e.presupuesto_total else 0,
        'ciudad': e.ciudad,
        'estado': e.estado,
        'created_at': e.created_at,
        'updated_at': e.updated_at
    } for e in eventos]
    return Response(data)


@api_view(['GET'])
def obtener_evento(request, evento_id):
    try:
        evento = Evento.objects.get(id=evento_id)
        return Response({
            'id': evento.id,
            'usuario_id': evento.usuario_id,
            'conversacion_id': evento.conversacion_id,
            'nombre': evento.nombre,
            'tipo_evento': evento.tipo_evento,
            'fecha_evento': evento.fecha_evento,
            'num_personas': evento.num_personas,
            'presupuesto_total': float(evento.presupuesto_total) if evento.presupuesto_total else 0,
            'ciudad': evento.ciudad,
            'estado': evento.estado,
            'created_at': evento.created_at,
            'updated_at': evento.updated_at
        })
    except Evento.DoesNotExist:
        return Response({'error': 'Evento no encontrado'}, status=404)


@api_view(['PUT'])
def actualizar_evento(request, evento_id):
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return Response({'error': 'Evento no encontrado'}, status=404)
    
    data = request.data
    campos_permitidos = ['nombre', 'tipo_evento', 'fecha_evento', 'num_personas', 'presupuesto_total', 'ciudad', 'estado']
    
    for campo in campos_permitidos:
        if campo in data and data[campo] is not None:
            if campo == 'num_personas':
                try:
                    valor = int(data[campo])
                    if valor > 0:
                        setattr(evento, campo, valor)
                except (ValueError, TypeError):
                    pass
            elif campo == 'presupuesto_total':
                try:
                    valor = float(data[campo])
                    if valor >= 0:
                        setattr(evento, campo, valor)
                except (ValueError, TypeError):
                    pass
            else:
                setattr(evento, campo, data[campo])
    
    evento.save()
    
    return Response({
        'success': True,
        'mensaje': 'Evento actualizado exitosamente',
        'evento': {
            'id': evento.id,
            'nombre': evento.nombre,
            'tipo_evento': evento.tipo_evento,
            'fecha_evento': evento.fecha_evento,
            'num_personas': evento.num_personas,
            'presupuesto_total': float(evento.presupuesto_total),
            'ciudad': evento.ciudad,
            'estado': evento.estado
        }
    })


@api_view(['DELETE'])
def eliminar_evento(request, evento_id):
    try:
        evento = Evento.objects.get(id=evento_id)
        evento.delete()
        return Response({'success': True, 'mensaje': 'Evento eliminado exitosamente'})
    except Evento.DoesNotExist:
        return Response({'error': 'Evento no encontrado'}, status=404)


# ==================== CONVERSACIONES ====================

@api_view(['POST'])
def crear_conversacion(request):
    usuario_id = request.data.get('usuario_id')
    titulo = request.data.get('titulo', 'Nueva conversación')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    
    conversacion = Conversacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        historial_json=[]
    )
    
    return Response({
        'id': conversacion.id,
        'titulo': conversacion.titulo,
        'created_at': conversacion.created_at
    }, status=201)


@api_view(['GET'])
def obtener_conversaciones_usuario(request, usuario_id):
    conversaciones = Conversacion.objects.filter(usuario_id=usuario_id).order_by('-updated_at')
    data = [{
        'id': c.id,
        'titulo': c.titulo,
        'estado': c.estado,
        'tipo_evento_uri': c.tipo_evento_uri,
        'num_personas': c.num_personas,
        'presupuesto': c.presupuesto,
        'created_at': c.created_at,
        'updated_at': c.updated_at,
        'historial_json': c.historial_json,
        'plan_json': c.plan_json
    } for c in conversaciones]
    return Response(data)


@api_view(['GET'])
def obtener_conversacion(request, conversacion_id):
    try:
        conversacion = Conversacion.objects.get(id=conversacion_id)
        return Response({
            'id': conversacion.id,
            'usuario_id': conversacion.usuario.id,
            'titulo': conversacion.titulo,
            'tipo_evento_uri': conversacion.tipo_evento_uri,
            'num_personas': conversacion.num_personas,
            'presupuesto': conversacion.presupuesto,
            'estado': conversacion.estado,
            'historial_json': conversacion.historial_json,
            'plan_json': conversacion.plan_json,
            'created_at': conversacion.created_at,
            'updated_at': conversacion.updated_at
        })
    except Conversacion.DoesNotExist:
        return Response({'error': 'Conversación no encontrada'}, status=404)


# ==================== NUEVOS ENDPOINTS ÚTILES ====================

@api_view(['GET'])
def estadisticas_generales(request):
    total_usuarios = Usuario.objects.count()
    total_conversaciones = Conversacion.objects.count()
    total_eventos = Evento.objects.count()
    proveedores = sparql.obtener_proveedores()
    servicios = sparql.obtener_servicios()
    
    return Response({
        'total_usuarios': total_usuarios,
        'total_conversaciones': total_conversaciones,
        'total_eventos': total_eventos,
        'total_proveedores': len(proveedores),
        'total_servicios': len(servicios),
        'proveedores_destacados': sparql.obtener_proveedores_destacados()[:3]
    })


@api_view(['GET'])
def buscar_general(request):
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({'error': 'Se requiere un término de búsqueda'}, status=400)
    
    resultados = {
        'proveedores': sparql.obtener_proveedores_por_nombre(query),
        'servicios': [],
        'paquetes': []
    }
    
    tipos = sparql.obtener_tipos_evento()
    for tipo in tipos:
        servicios = sparql.obtener_servicios_por_tipo(tipo.get('nombre'))
        for s in servicios:
            if query.lower() in s.get('nombre', '').lower():
                resultados['servicios'].append(s)
    
    paquetes = sparql.obtener_paquetes()
    for p in paquetes:
        if query.lower() in p.get('nombre', '').lower():
            resultados['paquetes'].append(p)
    
    return Response(resultados)