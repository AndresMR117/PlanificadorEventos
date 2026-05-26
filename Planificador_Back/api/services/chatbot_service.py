"""
chatbot_service.py
Servicio auxiliar que usa GroqService para procesar mensajes del chatbot.
La lógica de recomendaciones y extracción de estado vive en GroqService.
Este archivo solo orquesta el flujo y mantiene compatibilidad con views.py.
"""
from datetime import datetime
from .groq_service import GroqService
from .sparql_service import SPARQLService


class ChatbotService:

    def __init__(self):
        self.groq   = GroqService()
        self.sparql = SPARQLService()

    # ─────────────────────────────────────────────────────────────
    # Punto de entrada desde views.py
    # ─────────────────────────────────────────────────────────────

    def procesar_mensaje(self, conversacion_id: int, mensaje: str,
                          historial: list) -> dict:
        """
        Recibe el mensaje del usuario y el historial completo,
        genera la respuesta con Groq (con contexto real de BDs),
        y devuelve el dict que views.py necesita.
        """
        # Construir contexto de texto a partir del historial
        contexto = self._historial_a_texto(historial)

        # Obtener respuesta del LLM (con datos reales de las BDs)
        respuesta_ia = self.groq.generar_respuesta(
            mensaje=mensaje,
            contexto=contexto,
        )

        # Extraer estado acumulado para devolverlo al frontend
        texto_completo = contexto + '\n' + mensaje
        estado = self.groq.extraer_estado(texto_completo)

        todos_completos = all([
            estado['tipo_uri'],
            estado['presupuesto'],
            estado['personas'],
            estado['ciudad'],
            estado['fecha'],
        ])

        return {
            'respuesta':      respuesta_ia,
            'estado':         'Datos_completos' if todos_completos else 'Recopilando',
            'tipo_evento':    estado['tipo_django'],
            'num_personas':   estado['personas'],
            'presupuesto':    estado['presupuesto'],
            'ciudad':         estado['ciudad'],
            'fecha':          estado['fecha'],
            'datos_completos': todos_completos,
        }

    # ─────────────────────────────────────────────────────────────
    # Generación de plan completo (usado en plan-generado.html)
    # ─────────────────────────────────────────────────────────────

    def generar_plan_completo(self, tipo_evento: str, num_personas: int,
                               presupuesto: float) -> dict:
        """
        Genera un plan detallado con servicios reales de la BD semántica
        y un cronograma de preparación según el tipo de evento.
        """
        # Obtener URI del tipo para la query SPARQL
        uri = self.groq._extraer_tipo_uri(tipo_evento) or tipo_evento
        servicios = self.sparql.obtener_servicios_por_tipo(uri)

        # Filtrar por presupuesto
        if presupuesto:
            servicios = [s for s in servicios
                         if float(s.get('precioBase') or 0) <= presupuesto]

        cronogramas = {
            'Boda': [
                {'mes': 6, 'actividad': 'Reservar salón y fecha'},
                {'mes': 5, 'actividad': 'Contratar fotógrafo y música'},
                {'mes': 4, 'actividad': 'Elección de catering y torta'},
                {'mes': 3, 'actividad': 'Decoración y flores'},
                {'mes': 2, 'actividad': 'Envío de invitaciones'},
                {'mes': 1, 'actividad': 'Últimas pruebas y ensayo'},
                {'mes': 0, 'actividad': 'Día del evento'},
            ],
            'Cumpleanos': [
                {'mes': 1, 'actividad': 'Definir tema y presupuesto'},
                {'mes': 0.75, 'actividad': 'Contratar animación y catering'},
                {'mes': 0.5,  'actividad': 'Comprar decoración y pastel'},
                {'mes': 0,    'actividad': 'Celebración'},
            ],
            'Grado': [
                {'mes': 3, 'actividad': 'Reserva de salón'},
                {'mes': 2, 'actividad': 'Contratar DJ y fotógrafo'},
                {'mes': 1, 'actividad': 'Comprar torta y decoración'},
                {'mes': 0, 'actividad': 'Ceremonia de graduación'},
            ],
            'QuinceAnos': [
                {'mes': 6, 'actividad': 'Reserva de salón'},
                {'mes': 5, 'actividad': 'Contratar orquesta o DJ'},
                {'mes': 4, 'actividad': 'Elegir vestido y accesorios'},
                {'mes': 3, 'actividad': 'Decoración y catering'},
                {'mes': 2, 'actividad': 'Ensayo del baile'},
                {'mes': 1, 'actividad': 'Últimos detalles'},
                {'mes': 0, 'actividad': 'Día de la quinceañera'},
            ],
        }

        crono = cronogramas.get(uri, cronogramas.get('Cumpleanos', []))
        servicios_top = servicios[:4]
        costo_estimado = sum(float(s.get('precioBase') or 0) for s in servicios_top)

        return {
            'tipo_evento':             tipo_evento,
            'num_personas':            num_personas,
            'presupuesto':             presupuesto,
            'servicios_recomendados':  servicios_top,
            'cronograma':              crono,
            'presupuesto_total_estimado': costo_estimado,
            'recomendaciones': [
                'Reserva con anticipación para mejores precios',
                'Considera temporada baja para ahorrar hasta un 25%',
                'Revisa la calificación de los proveedores antes de contratar',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # Utilidades
    # ─────────────────────────────────────────────────────────────

    def _historial_a_texto(self, historial: list) -> str:
        if not historial:
            return ''
        # Tomar los últimos 10 mensajes para no exceder tokens
        ultimos = historial[-10:] if len(historial) > 10 else historial
        lineas = []
        for msg in ultimos:
            if isinstance(msg, dict):
                rol     = 'Usuario'    if msg.get('rol') == 'user' else 'Asistente'
                mensaje = msg.get('mensaje', '')
                if mensaje:
                    lineas.append(f'{rol}: {mensaje}')
        return '\n'.join(lineas)

    def _formatear_fecha(self, fecha_iso: str) -> str:
        try:
            return datetime.strptime(fecha_iso, '%Y-%m-%d').strftime('%d de %B de %Y')
        except Exception:
            return fecha_iso or 'No especificada'
