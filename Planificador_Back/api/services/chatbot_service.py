import json
import re
from .sparql_service import SPARQLService
from datetime import datetime

class ChatbotService:
    def __init__(self):
        self.sparql = SPARQLService()
    
    def procesar_mensaje(self, conversacion_id: int, mensaje: str, historial: list) -> dict:
        """Procesa un mensaje del usuario y genera respuesta"""
        
        # Extraer datos del mensaje
        datos_extraidos = self._extraer_datos(mensaje)
        
        # Buscar datos previos en el historial
        datos_previos = self._obtener_datos_previos(historial)
        
        # Combinar datos
        datos_evento = self._combinar_datos(datos_previos, datos_extraidos)
        
        # Verificar qué campos faltan
        faltantes = self._campos_faltantes(datos_evento)
        
        print(f"[DEBUG] Datos evento: {datos_evento}")
        print(f"[DEBUG] Campos faltantes: {faltantes}")
        
        # Si todos los datos están completos
        if len(faltantes) == 0:
            return self._respuesta_completa(datos_evento)
        
        # Si falta algún dato, preguntar
        siguiente = faltantes[0]
        return self._preguntar_siguiente_dato(siguiente, datos_evento, conversacion_id)
    
    def _extraer_datos(self, mensaje: str) -> dict:
        """Extrae datos del mensaje actual"""
        mensaje_lower = mensaje.lower()
        datos = {
            'tipo_evento': None,
            'personas': None,
            'presupuesto': None,
            'ciudad': None,
            'fecha': None
        }
        
        # Extraer tipo de evento (nombres amigables que luego SPARQLService mapea a URIs)
        tipos = {
            'boda': 'Boda',
            'matrimonio': 'Boda',
            'cumpleaños': 'Cumpleaños',
            'cumple': 'Cumpleaños',
            'grado': 'Grado',
            'graduación': 'Grado',
            'graduacion': 'Grado',
            'quinceañera': 'Quinceañera',
            'quince años': 'Quinceañera',
            'quince': 'Quinceañera',
            'baby shower': 'Baby Shower',
            'fiesta infantil': 'Fiesta Infantil',
            'despedida de soltero': 'Despedida de Soltero',
            'despedida': 'Despedida de Soltero',
            'aniversario': 'Aniversario',
            'bautizo': 'Bautizo',
            'primera comunión': 'Primera Comunión',
            'primera comunion': 'Primera Comunión',
            'evento corporativo': 'Evento Corporativo',
            'corporativo': 'Evento Corporativo',
            'conferencia': 'Conferencia',
        }
        
        for key, value in tipos.items():
            if key in mensaje_lower:
                datos['tipo_evento'] = value
                break
        
        # Extraer número de personas
        numeros = re.findall(r'\b(\d{1,4})\b', mensaje)
        for num in numeros:
            num_int = int(num)
            if 1 <= num_int <= 5000:
                datos['personas'] = num_int
                break
        
        # Extraer presupuesto
        mensaje_clean = mensaje.replace('.', '').replace(',', '')
        numeros_grandes = re.findall(r'\b(\d{5,10})\b', mensaje_clean)
        for num in numeros_grandes:
            num_int = int(num)
            if 100000 <= num_int <= 1000000000:
                datos['presupuesto'] = num_int
                break
        
        if not datos['presupuesto']:
            match = re.search(r'(\d+)\s*millones?', mensaje_lower)
            if match:
                datos['presupuesto'] = int(match.group(1)) * 1000000
        
        # Extraer ciudad
        ciudades = [
            'florencia', 'bogotá', 'bogota', 'medellín', 'medellin',
            'cali', 'bucaramanga', 'cartagena', 'barranquilla', 'belén', 'belen',
            'pereira', 'manizales', 'villavicencio', 'ibagué', 'ibague', 
            'cúcuta', 'cucuta', 'santa marta'
        ]
        for ciudad in ciudades:
            if ciudad in mensaje_lower:
                datos['ciudad'] = ciudad.capitalize()
                break
        
        # Extraer fecha
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        match = re.search(r'(\d{1,2})\s*(?:de|del?)?\s*(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s*(?:de|del?)?\s*(\d{4})', mensaje_lower)
        if match:
            dia = match.group(1).zfill(2)
            mes = meses.get(match.group(2))
            año = match.group(3)
            if mes:
                datos['fecha'] = f"{año}-{str(mes).zfill(2)}-{dia}"
        
        if not datos['fecha']:
            match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', mensaje)
            if match:
                datos['fecha'] = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
        
        return datos
    
    def _obtener_datos_previos(self, historial: list) -> dict:
        """Extrae datos previos del historial de conversación"""
        datos = {
            'tipo_evento': None,
            'personas': None,
            'presupuesto': None,
            'ciudad': None,
            'fecha': None
        }
        
        if not historial:
            return datos
        
        for msg in historial:
            if isinstance(msg, dict):
                if msg.get('tipo_evento'):
                    datos['tipo_evento'] = msg.get('tipo_evento')
                if msg.get('num_personas'):
                    datos['personas'] = msg.get('num_personas')
                if msg.get('presupuesto'):
                    datos['presupuesto'] = msg.get('presupuesto')
                if msg.get('ciudad'):
                    datos['ciudad'] = msg.get('ciudad')
                if msg.get('fecha'):
                    datos['fecha'] = msg.get('fecha')
        
        return datos
    
    def _combinar_datos(self, previos: dict, nuevos: dict) -> dict:
        """Combina datos previos con nuevos (los nuevos tienen prioridad)"""
        resultado = {}
        for key in ['tipo_evento', 'personas', 'presupuesto', 'ciudad', 'fecha']:
            if nuevos.get(key):
                resultado[key] = nuevos[key]
            elif previos.get(key):
                resultado[key] = previos[key]
            else:
                resultado[key] = None
        return resultado
    
    def _campos_faltantes(self, datos: dict) -> list:
        """Retorna lista de campos que faltan en orden"""
        orden = ['tipo_evento', 'personas', 'presupuesto', 'ciudad', 'fecha']
        faltantes = []
        for campo in orden:
            if not datos.get(campo):
                faltantes.append(campo)
        return faltantes
    
    def _preguntar_siguiente_dato(self, campo: str, datos: dict, conversacion_id: int) -> dict:
        """Genera la pregunta para el siguiente campo faltante"""
        
        preguntas = {
            'tipo_evento': "🎉 ¡Hola! ¿Qué tipo de evento quieres organizar?\n(Boda, Cumpleaños, Grado, Quinceañera, etc.)",
            'personas': "👥 ¿Cuántas personas asistirán al evento?",
            'presupuesto': "💰 ¿Cuál es tu presupuesto aproximado para este evento en pesos colombianos?",
            'ciudad': "📍 ¿En qué ciudad de Colombia se realizará el evento?",
            'fecha': "📅 ¿En qué fecha se realizará el evento? (Ej: 15 de diciembre de 2024)"
        }
        
        respuesta = preguntas.get(campo, "Cuéntame más sobre tu evento.")
        
        # Si ya tenemos el tipo de evento, mostrarlo en el mensaje
        if datos.get('tipo_evento') and campo != 'tipo_evento':
            respuesta = f"🎉 ¡Excelente! Organizaremos un(a) {datos['tipo_evento']}.\n\n{respuesta}"
        
        # Si ya tenemos personas, mostrarlo
        if datos.get('personas') and campo == 'presupuesto':
            respuesta = f"👥 Perfecto, {datos['personas']} personas asistirán.\n\n{respuesta}"
        
        # Si ya tenemos presupuesto, mostrarlo
        if datos.get('presupuesto') and campo == 'ciudad':
            presupuesto_formateado = f"${datos['presupuesto']:,.0f}".replace(',', '.')
            respuesta = f"💰 Presupuesto: {presupuesto_formateado} COP\n\n{respuesta}"
        
        return {
            'respuesta': respuesta,
            'estado': f"Esperando_{campo}",
            'tipo_evento': datos.get('tipo_evento'),
            'num_personas': datos.get('personas'),
            'presupuesto': datos.get('presupuesto'),
            'ciudad': datos.get('ciudad'),
            'fecha': datos.get('fecha')
        }
    
    def _respuesta_completa(self, datos: dict) -> dict:
        """Respuesta cuando todos los datos están completos"""
        
        # Formatear valores
        presupuesto_formateado = f"${datos['presupuesto']:,.0f}".replace(',', '.')
        fecha_formateada = self._formatear_fecha(datos['fecha'])
        
        respuesta = f"""✅ ¡Excelente! Ya tengo todos los datos para tu {datos['tipo_evento']}.

📋 **Resumen de tu evento:**
• 🎉 Tipo: {datos['tipo_evento']}
• 👥 Personas: {datos['personas']}
• 💰 Presupuesto: {presupuesto_formateado} COP
• 📍 Ciudad: {datos['ciudad']}
• 📅 Fecha: {fecha_formateada}

✅ ¡Todos los datos completos! Haz clic en el botón "Guardar evento" para guardarlo en tu cuenta."""
        
        # Consultar recomendaciones usando el mapeo correcto de URI
        servicios = self.sparql.recomendar_servicios(datos['tipo_evento'])
        if servicios:
            respuesta += f"\n\n📋 **Servicios sugeridos para tu {datos['tipo_evento']}:**\n"
            for s in servicios[:4]:
                precio = float(s.get('precioBase', 0) or 0)
                cat = s.get('categoria', '')
                nombre = s.get('nombre', 'Servicio')
                empresa = s.get('empresa', '')
                linea = f"• {nombre}"
                if cat:
                    linea += f" [{cat}]"
                if precio > 0:
                    linea += f" - Desde ${precio:,.0f} COP"
                if empresa:
                    linea += f" ({empresa})"
                respuesta += linea + "\n"
        
        return {
            'respuesta': respuesta,
            'estado': "Datos_completos",
            'tipo_evento': datos['tipo_evento'],
            'num_personas': datos['personas'],
            'presupuesto': datos['presupuesto'],
            'ciudad': datos['ciudad'],
            'fecha': datos['fecha'],
            'datos_completos': True
        }
    
    def _formatear_fecha(self, fecha_iso: str) -> str:
        """Convierte fecha ISO a formato legible"""
        try:
            fecha = datetime.strptime(fecha_iso, "%Y-%m-%d")
            return fecha.strftime("%d de %B de %Y")
        except:
            return fecha_iso or "No especificada"
    
    def generar_plan_completo(self, tipo_evento: str, num_personas: int, presupuesto: float) -> dict:
        """Genera un plan completo con cronograma"""
        servicios = self.sparql.recomendar_servicios(tipo_evento)
        
        cronograma = {
            "Boda": [
                {"mes": 6, "actividad": "Reservar salón y fecha"},
                {"mes": 5, "actividad": "Contratar fotógrafo y música"},
                {"mes": 4, "actividad": "Elección de catering y torta"},
                {"mes": 3, "actividad": "Decoración y flores"},
                {"mes": 2, "actividad": "Envío de invitaciones"},
                {"mes": 1, "actividad": "Últimas pruebas"},
                {"mes": 0, "actividad": "Día del evento"}
            ],
            "Cumpleaños": [
                {"mes": 1, "actividad": "Definir tema y presupuesto"},
                {"mes": 0.75, "actividad": "Contratar animación y catering"},
                {"mes": 0.5, "actividad": "Comprar decoración y pastel"},
                {"mes": 0, "actividad": "Celebración"}
            ],
            "Grado": [
                {"mes": 3, "actividad": "Reserva de salón"},
                {"mes": 2, "actividad": "Contratar DJ y fotógrafo"},
                {"mes": 1, "actividad": "Comprar torta y decoración"},
                {"mes": 0, "actividad": "Ceremonia de graduación"}
            ],
            "Quinceañera": [
                {"mes": 6, "actividad": "Reserva de salón"},
                {"mes": 5, "actividad": "Contratar orquesta o DJ"},
                {"mes": 4, "actividad": "Elegir vestido y accesorios"},
                {"mes": 3, "actividad": "Decoración y catering"},
                {"mes": 2, "actividad": "Ensayo del baile"},
                {"mes": 1, "actividad": "Últimos detalles"},
                {"mes": 0, "actividad": "Día de la quinceañera"}
            ]
        }
        
        crono = cronograma.get(tipo_evento, cronograma["Cumpleaños"])
        
        return {
            'tipo_evento': tipo_evento,
            'num_personas': num_personas,
            'presupuesto': presupuesto,
            'servicios_recomendados': servicios[:4],
            'cronograma': crono,
            'presupuesto_total_estimado': sum(float(s.get('precioBase', 0)) for s in servicios[:4]),
            'recomendaciones': [
                "Reserva con anticipación para mejores precios",
                "Considera temporada baja para ahorrar hasta un 25%",
                "Revisa la calificación de los proveedores antes de contratar"
            ]
        }