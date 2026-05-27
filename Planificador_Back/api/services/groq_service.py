import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from .sparql_service import SPARQLService

load_dotenv()


class GroqService:
    """
    Servicio de chatbot que usa Groq (LLM) con contexto real
    extraído de las dos bases de datos del proyecto:
      - BD Semántica (Fuseki/SPARQL): servicios, paquetes, proveedores, accesorios
      - BD Relacional (MySQL): datos del usuario y sus eventos previos
    El LLM NO inventa nada; solo redacta en lenguaje natural
    usando la información que se le inyecta en el system prompt.
    """

    # ── Mapeo texto → URI del TTL (para queries SPARQL) ──────────
    _TEXTO_A_URI = {
        'boda': 'Boda', 'matrimonio': 'Boda',
        'cumpleanos': 'Cumpleanos', 'cumpleaños': 'Cumpleanos', 'cumple': 'Cumpleanos',
        'grado': 'Grado', 'graduacion': 'Grado', 'graduación': 'Grado',
        'quinceanera': 'QuinceAnos', 'quinceañera': 'QuinceAnos',
        'quince anos': 'QuinceAnos', 'quince años': 'QuinceAnos',
        'baby shower': 'BabyShower',
        'fiesta infantil': 'FiestaInfantil',
        'despedida de soltero': 'Despedida', 'despedida': 'Despedida',
        'aniversario': 'Aniversario',
        'bautizo': 'Bautizo',
        'primera comunion': 'PrimeraComunion', 'primera comunión': 'PrimeraComunion',
        'evento corporativo': 'EventoCorporativo', 'corporativo': 'EventoCorporativo',
        'conferencia': 'Conferencia',
    }

    # ── Mapeo URI → valor exacto que acepta el modelo Django ─────
    _URI_A_TIPO_DJANGO = {
        'Boda': 'Boda',
        'Cumpleanos': 'Cumpleaños',
        'Grado': 'Grado',
        'QuinceAnos': 'Quinceañera',
        'BabyShower': 'BabyShower',
        'FiestaInfantil': 'FiestaInfantil',
        'Despedida': 'Despedida',
        'Aniversario': 'Aniversario',
        'Bautizo': 'Bautizo',
        'PrimeraComunion': 'Cumpleaños',   # no existe en model → fallback
        'EventoCorporativo': 'EventoCorporativo',
        'Conferencia': 'EventoCorporativo', # no existe en model → fallback
    }

    # ── Nombre legible para mostrar al usuario ────────────────────
    _URI_A_LABEL = {
        'Boda': 'Boda',
        'Cumpleanos': 'Cumpleaños',
        'Grado': 'Grado',
        'QuinceAnos': 'Quinceañera',
        'BabyShower': 'Baby Shower',
        'FiestaInfantil': 'Fiesta Infantil',
        'Despedida': 'Despedida de Soltero',
        'Aniversario': 'Aniversario',
        'Bautizo': 'Bautizo',
        'PrimeraComunion': 'Primera Comunión',
        'EventoCorporativo': 'Evento Corporativo',
        'Conferencia': 'Conferencia',
    }

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print('[GROQ] ⚠️  GROQ_API_KEY no encontrada en .env')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url='https://api.groq.com/openai/v1'
        )
        self.model = 'llama-3.1-8b-instant'
        self.sparql = SPARQLService()

    # ─────────────────────────────────────────────────────────────
    # 1. EXTRACCIÓN DE ESTADO DEL HISTORIAL
    # ─────────────────────────────────────────────────────────────

    def _normalizar(self, texto: str) -> str:
        """Quita tildes y pone en minúsculas para comparaciones."""
        return (texto.lower()
                .replace('á','a').replace('é','e').replace('í','i')
                .replace('ó','o').replace('ú','u').replace('ñ','n'))

    def _extraer_tipo_uri(self, texto: str) -> str | None:
        norm = self._normalizar(texto)
        # Orden importa: primero las frases largas, luego las cortas
        for key in sorted(self._TEXTO_A_URI, key=len, reverse=True):
            if key in norm:
                return self._TEXTO_A_URI[key]
        return None

    def _extraer_presupuesto(self, texto: str) -> int | None:
        # "5 millones", "5M", "5.000.000", "5000000"
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:millones?|M\b)', texto, re.I)
        if m:
            return int(float(m.group(1).replace(',', '.')) * 1_000_000)
        limpio = texto.replace('.', '').replace(',', '')
        nums = re.findall(r'\b(\d{6,10})\b', limpio)
        for n in nums:
            val = int(n)
            if 100_000 <= val <= 2_000_000_000:
                return val
        return None

    def _extraer_personas(self, texto: str) -> int | None:
        m = re.search(r'(\d{1,4})\s*personas?', texto, re.I)
        if not m:
            # número suelto entre 1 y 9999 en respuesta de una sola palabra
            if re.match(r'^\s*\d{1,4}\s*$', texto.strip()):
                m = re.match(r'(\d{1,4})', texto.strip())
        if m:
            val = int(m.group(1))
            if 1 <= val <= 5000:
                return val
        return None

    def _extraer_ciudad(self, texto: str) -> str | None:
        norm = self._normalizar(texto)
        ciudades = [
            ('florencia',           'Florencia'),
            ('belen de los andaquies', 'Belén de los Andaquíes'),
            ('belen',               'Belén de los Andaquíes'),
            ('san vicente del caguan', 'San Vicente del Caguán'),
            ('san vicente',         'San Vicente del Caguán'),
            ('puerto rico',         'Puerto Rico'),
            ('el doncello',         'El Doncello'),
            ('la montanita',        'La Montañita'),
            ('morelia',             'Morelia'),
            ('milan',               'Milán'),
            ('valparaiso',          'Valparaíso'),
            ('albania',             'Albania'),
            ('solita',              'Solita'),
            ('solano',              'Solano'),
            ('cartagena del chaira','Cartagena del Chairá'),
            ('bogota',              'Bogotá'),
            ('medellin',            'Medellín'),
            ('cali',                'Cali'),
            ('bucaramanga',         'Bucaramanga'),
        ]
        for key, display in ciudades:
            if key in norm:
                return display
        return None

    def _extraer_fecha(self, texto: str) -> str | None:
        meses = {
            'enero':'01','febrero':'02','marzo':'03','abril':'04',
            'mayo':'05','junio':'06','julio':'07','agosto':'08',
            'septiembre':'09','octubre':'10','noviembre':'11','diciembre':'12',
        }
        m = re.search(
            r'(\d{1,2})\s*(?:de|del?)?\s*'
            r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|'
            r'septiembre|octubre|noviembre|diciembre)'
            r'\s*(?:de|del?)?\s*(\d{4})',
            texto, re.I
        )
        if m:
            mes = meses.get(m.group(2).lower())
            if mes:
                return f"{m.group(3)}-{mes}-{m.group(1).zfill(2)}"
        m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', texto)
        if m:
            return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
        return None

    def extraer_estado(self, historial_texto: str) -> dict:
        """
        Extrae del texto acumulado de la conversación los 5 datos
        del evento que ya fueron mencionados.
        """
        estado = {
            'tipo_uri':    None,
            'tipo_label':  None,
            'tipo_django': None,
            'presupuesto': None,
            'personas':    None,
            'ciudad':      None,
            'fecha':       None,
        }
        if not historial_texto:
            return estado

        uri = self._extraer_tipo_uri(historial_texto)
        if uri:
            estado['tipo_uri']    = uri
            estado['tipo_label']  = self._URI_A_LABEL.get(uri, uri)
            estado['tipo_django'] = self._URI_A_TIPO_DJANGO.get(uri, uri)

        # Extraer presupuesto, ciudad y fecha de TODO el historial (usuario + bot)
        estado['presupuesto'] = self._extraer_presupuesto(historial_texto)
        estado['ciudad']      = self._extraer_ciudad(historial_texto)
        estado['fecha']       = self._extraer_fecha(historial_texto)

        # ── PERSONAS: buscar SOLO en los turnos del usuario para evitar
        #    que capacidades de salones ("Salón para 250 personas") se
        #    confundan con el número de invitados declarado por el usuario. ──
        lineas_usuario = '\n'.join(
            linea.replace('Usuario:', '', 1).strip()
            for linea in historial_texto.splitlines()
            if linea.strip().startswith('Usuario:')
        )
        estado['personas'] = self._extraer_personas(lineas_usuario)

        return estado

    # ─────────────────────────────────────────────────────────────
    # 2. CONSULTA A LAS BASES DE DATOS
    # ─────────────────────────────────────────────────────────────

    def _consultar_bd_semantica(self, tipo_uri: str, presupuesto: int | None,
                                 ciudad: str | None) -> dict:
        """
        Consulta Fuseki y devuelve servicios, paquetes y proveedores
        relevantes para el evento. Si Fuseki no responde devuelve listas vacías
        (el LLM lo indicará honestamente al usuario).
        """
        resultado = {'servicios': [], 'servicios_fuera': [], 'paquetes': [], 'proveedores': []}

        if tipo_uri:
            # Servicios
            servicios = self.sparql.obtener_servicios_por_tipo(tipo_uri)
            if presupuesto:
                dentro = [s for s in servicios
                          if float(s.get('precioBase') or 0) <= presupuesto]
                fuera  = [s for s in servicios
                          if float(s.get('precioBase') or 0) >  presupuesto]
                resultado['servicios']       = dentro   # solo los que caben
                resultado['servicios_fuera'] = fuera    # para advertir al usuario
            else:
                resultado['servicios'] = servicios

            # Paquetes
            resultado['paquetes'] = self.sparql.obtener_paquetes_por_tipo(tipo_uri)

        # Proveedores — traer TODOS, el LLM decide cuántos mostrar según el contexto
        if ciudad:
            provs = self.sparql.obtener_proveedores_por_ciudad(ciudad)
            resultado['proveedores'] = provs if provs else \
                self.sparql.obtener_proveedores_destacados()
        else:
            resultado['proveedores'] = self.sparql.obtener_proveedores_destacados()

        return resultado

    def _formatear_bd_para_prompt(self, bd: dict, tipo_label: str,
                                   presupuesto: int | None) -> str:
        """
        Convierte los datos de la BD en un bloque de texto claro
        que el LLM usará como única fuente de verdad.
        """
        lineas = ['=== DATOS REALES DE LA BASE DE DATOS ===']

        if bd['servicios']:
            titulo = f'SERVICIOS PARA {tipo_label.upper()}'
            if presupuesto:
                titulo += f' (dentro del presupuesto de ${presupuesto:,.0f} COP)'
            lineas.append(titulo + ':')
            for s in bd['servicios']:
                precio_base = s.get('precioBase', '')
                precio_pers = s.get('precioPorPersona', '')
                nombre      = s.get('nombre', '?')
                categoria   = s.get('categoria', '')
                empresa     = s.get('empresa', '')

                precio_str = ''
                if precio_base:
                    precio_str = f'${float(precio_base):,.0f} COP'
                elif precio_pers:
                    precio_str = f'${float(precio_pers):,.0f} COP/persona'

                linea = f'  • [{categoria}] {nombre}'
                if precio_str:
                    linea += f' — {precio_str}'
                if empresa:
                    linea += f' | Proveedor: {empresa}'
                lineas.append(linea)
        else:
            if tipo_label:
                lineas.append(f'SERVICIOS: No se encontraron servicios en la BD para {tipo_label}.')

        # ── Servicios que superan el presupuesto (solo informar, NO recomendar) ──
        if bd.get('servicios_fuera'):
            lineas.append(f'\n⚠️ SERVICIOS QUE SUPERAN EL PRESUPUESTO DEL CLIENTE (NO recomendar; solo mencionar si el cliente los pregunta explícitamente):')
            for s in bd['servicios_fuera'][:6]:
                precio_base = s.get('precioBase', '')
                nombre      = s.get('nombre', '?')
                categoria   = s.get('categoria', '')
                empresa     = s.get('empresa', '')
                linea = f'  • [{categoria}] {nombre}'
                if precio_base:
                    linea += f' — ${float(precio_base):,.0f} COP (EXCEDE PRESUPUESTO)'
                if empresa:
                    linea += f' | Proveedor: {empresa}'
                lineas.append(linea)

        if bd['paquetes']:
            lineas.append(f'\nPAQUETES DISPONIBLES:')
            for p in bd['paquetes']:
                precio = float(p.get('precioBase') or 0)
                desc   = p.get('descuentoPct', '0')
                nombre = p.get('nombre', '?')
                lineas.append(f'  • {nombre} — ${precio:,.0f} COP ({desc}% descuento)')

        if bd['proveedores']:
            lineas.append('\nPROVEEDORES DISPONIBLES (ordenados por calificación):')
            for p in bd['proveedores']:
                nombre = p.get('nombre', '?')
                cal    = p.get('calificacion', '')
                tel    = p.get('telefono', '')
                ciudad_p = p.get('ciudad', '')
                linea  = f'  • {nombre}'
                if cal:
                    linea += f' ⭐{cal}/5'
                if ciudad_p:
                    linea += f' | {ciudad_p}'
                if tel:
                    linea += f' | Tel: {tel}'
                lineas.append(linea)

        if len(lineas) == 1:
            lineas.append('(Sin datos disponibles en la BD en este momento)')

        return '\n'.join(lineas)

    # ─────────────────────────────────────────────────────────────
    # 3. GENERACIÓN DE RESPUESTA (punto de entrada principal)
    # ─────────────────────────────────────────────────────────────

    def generar_respuesta(self, mensaje: str, contexto: str = None,
                           usuario_id: int = None) -> str:
        """
        Genera la respuesta del chatbot.
        - Extrae el estado del evento del historial acumulado.
        - Consulta las BDs con los datos disponibles.
        - Inyecta los datos reales en el system prompt.
        - Llama a Groq para que redacte la respuesta en lenguaje natural.
        """
        print(f'\n[GROQ] Mensaje: {mensaje[:80]}')

        # ── Estado acumulado ──────────────────────────────────────
        texto_completo = (contexto or '') + '\n' + mensaje
        estado = self.extraer_estado(texto_completo)

        tipo_uri    = estado['tipo_uri']
        tipo_label  = estado['tipo_label']
        tipo_django = estado['tipo_django']
        presupuesto = estado['presupuesto']
        personas    = estado['personas']
        ciudad      = estado['ciudad']
        fecha       = estado['fecha']

        print(f'[GROQ] Estado detectado → tipo={tipo_uri}, '
              f'ppto={presupuesto}, personas={personas}, '
              f'ciudad={ciudad}, fecha={fecha}')

        # ── Consultar BD semántica ────────────────────────────────
        bd = self._consultar_bd_semantica(tipo_uri, presupuesto, ciudad)
        info_bd = self._formatear_bd_para_prompt(bd, tipo_label or '', presupuesto)

        # ── Resumen de datos recopilados / pendientes ─────────────
        recopilados = []
        pendientes  = []

        if tipo_label:
            recopilados.append(f'✅ Tipo de evento: {tipo_label}')
        else:
            pendientes.append('❌ Tipo de evento')

        if presupuesto:
            recopilados.append(f'✅ Presupuesto: ${presupuesto:,.0f} COP')
        else:
            pendientes.append('❌ Presupuesto')

        if personas:
            recopilados.append(f'✅ Número de personas: {personas}')
        else:
            pendientes.append('❌ Número de personas')

        if ciudad:
            recopilados.append(f'✅ Ciudad: {ciudad}')
        else:
            pendientes.append('❌ Ciudad')

        if fecha:
            recopilados.append(f'✅ Fecha: {fecha}')
        else:
            pendientes.append('❌ Fecha')

        todos_completos = len(pendientes) == 0

        # ── System prompt ─────────────────────────────────────────
        system_prompt = f"""Eres "Planificador IA", asistente amigable de planificación de eventos en Colombia (Caquetá).

Tu única fuente de información son los datos reales que aparecen a continuación.
NO inventes proveedores, precios, calificaciones ni servicios que no estén en esa lista.
Si la BD no tiene datos para un campo, dilo honestamente.

{info_bd}

══ DATOS YA RECOPILADOS EN LA CONVERSACIÓN ══
{chr(10).join(recopilados) if recopilados else '  (ningún dato recopilado aún)'}
{chr(10).join(pendientes)  if pendientes  else '  (✅ todos los datos del evento están completos)'}

══ CÓMO DEBES COMPORTARTE ══

1. INICIO DE CONVERSACIÓN (sin tipo de evento aún):
   Pregunta únicamente el tipo de evento. Nada más.

2. TIENES EL TIPO PERO NO EL PRESUPUESTO:
   Pregunta únicamente el presupuesto. Nada más.

3. TIENES TIPO + PRESUPUESTO → CONVERSACIÓN LIBRE:
   A partir de aquí la conversación es completamente natural.
   - Muestra TODOS los servicios disponibles dentro del presupuesto con nombre y precio exacto de la BD.
   - Si el cliente pregunta por un servicio específico (por ejemplo "quiero barra libre",
     "¿tienen mariachi?", "qué opciones de catering hay?"), respóndele directamente:
     muestra ese servicio con su precio, proveedor y detalles disponibles en la BD.
   - Si el cliente pide recomendaciones, dáselas con datos reales.
   - Ve recogiendo los datos que faltan (personas, ciudad, fecha) de forma natural
     dentro de la conversación, sin interrogar mensaje a mensaje.
     Si el cliente menciona un dato en cualquier momento, ya lo tienes.
   - Si le faltan datos al final, puedes pedirlos amablemente de una vez:
     "Para guardar el evento solo me faltan: personas, ciudad y fecha. ¿Me los puedes dar?"
   - COMPARACIÓN DE PRESUPUESTO (REGLA CRÍTICA DE ARITMÉTICA):
     El presupuesto del cliente es ${int(presupuesto) if presupuesto else 0:,} COP.
     Un servicio SUPERA el presupuesto ÚNICAMENTE si su precio es MAYOR a ese número.
     Ejemplo correcto: servicio $1,100,000 COP con presupuesto $2,000,000 COP → DENTRO del presupuesto.
     Ejemplo correcto: servicio $2,500,000 COP con presupuesto $2,000,000 COP → FUERA del presupuesto.
     SOLO los servicios en la sección "SERVICIOS QUE SUPERAN EL PRESUPUESTO" exceden el límite.
     Si un servicio aparece en la sección principal, está DENTRO del presupuesto. NUNCA digas que
     un servicio de la lista principal "supera el presupuesto".
   - Si el cliente pide un servicio que supera su presupuesto, adviértelo claramente:
     muestra el precio real, explica que excede el presupuesto, y sugiere alternativas
     más baratas de la BD.
   - NUNCA recomiendes servicios de la sección "SERVICIOS QUE SUPERAN EL PRESUPUESTO"
     a menos que el cliente los pida explícitamente.
   - Cuando muestres ubicaciones o proveedores, LISTA TODOS los de la BD.

4. REGLAS GENERALES:
   - Responde siempre en español, con emojis y tono amigable y cercano.
   - NUNCA escribas los pasos internos ni nombres de variables en tu respuesta al usuario.
   - NUNCA digas cosas como "PASO 2", "PASO 3", ni repitas el estado interno.
   - Si un dato ya está en "DATOS YA RECOPILADOS", no lo vuelvas a pedir.
   - Acepta: "5 millones", "5M", "5.000.000", "$5.000.000" como presupuesto válido.
   - Acepta municipios del Caquetá: Florencia, Belén de los Andaquíes,
     San Vicente del Caguán, Morelia, Milán, El Doncello, Puerto Rico, etc.
   - CORRECCIONES DEL USUARIO: si el usuario te corrige sobre un precio, un dato o
     un error que cometiste, acéptalo con gracia, pide disculpas brevemente y continúa
     la conversación normalmente. NUNCA respondas con "Lo siento, no puedo continuar"
     ni te bloquees. Siempre sigue ayudando.
   - NUNCA generes respuestas como "Lo siento, no puedo continuar",
     "No tengo información suficiente para continuar" ni ninguna forma de rechazo
     o bloqueo. Si no tienes datos suficientes, pídelos amablemente al usuario.
   - HISTORIAL = CONVERSACIÓN ACTUAL: Todo el historial que recibes corresponde
     ÚNICAMENTE a la conversación presente. NUNCA digas frases como
     "en la conversación anterior mencionaste", "anteriormente dijiste" ni nada
     que implique que hubo una sesión previa. Si el usuario mencionó algo hace
     dos mensajes, dilo como "mencionaste antes" o "antes dijiste", siempre
     en el contexto de ESTA misma conversación.

5. CUANDO TENGAS LOS 5 DATOS (tipo, presupuesto, personas, ciudad, fecha):
   Muestra el resumen final con este formato exacto (el bloque ---DATOS_EVENTO--- lo usa
   el sistema internamente; el usuario no lo verá):

🎉 ¡Todo listo para tu [TIPO]!

📋 **Resumen de tu evento:**
• 🎉 Tipo: [tipo_label]
• 💰 Presupuesto: $[X] COP
• 👥 Personas: [N]
• 📍 Ciudad: [ciudad]
• 📅 Fecha: [fecha en formato legible]

📦 **Servicios recomendados** (según tu presupuesto):
[Lista los servicios REALES de la BD con nombre, categoría y precio exacto]

---DATOS_EVENTO---
TIPO: {tipo_django or '[tipo_django]'}
PRESUPUESTO: {int(presupuesto) if presupuesto else '[numero]'}
PERSONAS: {int(personas) if personas else '[numero]'}
CIUDAD: {ciudad or '[ciudad]'}
FECHA: {fecha or '[YYYY-MM-DD]'}
---FIN_DATOS---

✅ Haz clic en **Guardar Evento** cuando quieras confirmar."""

        # ── Llamada a Groq ────────────────────────────────────────
        user_message = mensaje
        if contexto:
            user_message = (
                f'Historial de la conversación:\n{contexto}\n\n'
                f'El usuario acaba de escribir: "{mensaje}"'
            )

        try:
            print('[GROQ] Llamando API...')
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message},
                ],
                temperature=0.3,   # baja temperatura = menos alucinaciones
                max_tokens=1500,
            )
            respuesta = response.choices[0].message.content
            print(f'[GROQ] Respuesta ({len(respuesta)} chars): {respuesta[:80]}...')
            return respuesta

        except Exception as e:
            print(f'[GROQ ERROR] {e}')
            return (
                f'❌ Error al conectar con Groq: {e}\n'
                'Verifica que GROQ_API_KEY esté correctamente configurada en el archivo .env'
            )