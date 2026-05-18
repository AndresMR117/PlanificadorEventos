import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from .sparql_service import SPARQLService

load_dotenv()

class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        print(f"[INIT] API Key presente: {bool(self.api_key)}")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.1-8b-instant"
        self.sparql = SPARQLService()

    # ──────────────────────────────────────────────────────────────
    # EXTRACCION DE ESTADO (del historial + mensaje actual)
    # ──────────────────────────────────────────────────────────────

    def _extraer_estado(self, texto_completo: str) -> dict:
        estado = {'tipo_evento': None, 'personas': None,
                  'presupuesto': None, 'ciudad': None, 'fecha': None}
        if not texto_completo:
            return estado
        ctx = texto_completo.lower()

        # Tipo de evento
        tipos = [
            ('boda', 'Boda'), ('matrimonio', 'Boda'),
            ('cumpleanos', 'Cumpleanos'), ('cumple', 'Cumpleanos'),
            ('grado', 'Grado'), ('graduaci', 'Grado'),
            ('quinceanera', 'QuinceAnos'), ('quince a', 'QuinceAnos'),
            ('quince', 'QuinceAnos'), ('baby shower', 'BabyShower'),
            ('fiesta infantil', 'FiestaInfantil'),
            ('despedida de soltero', 'Despedida'), ('despedida', 'Despedida'),
            ('aniversario', 'Aniversario'), ('bautizo', 'Bautizo'),
            ('primera comuni', 'PrimeraComunion'),
            ('evento corporativo', 'EventoCorporativo'), ('corporativo', 'EventoCorporativo'),
            ('conferencia', 'Conferencia'),
        ]
        # Eliminar tildes para comparacion robusta
        ctx_norm = ctx.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
        for key, val in tipos:
            if key in ctx_norm:
                estado['tipo_evento'] = val
                break

        # Nombre bonito para mostrar al usuario
        nombres_bonitos = {
            'Boda': 'Boda', 'Cumpleanos': 'Cumpleaños', 'Grado': 'Grado',
            'QuinceAnos': 'Quinceañera', 'BabyShower': 'Baby Shower',
            'FiestaInfantil': 'Fiesta Infantil', 'Despedida': 'Despedida de Soltero',
            'Aniversario': 'Aniversario', 'Bautizo': 'Bautizo',
            'PrimeraComunion': 'Primera Comunión',
            'EventoCorporativo': 'Evento Corporativo', 'Conferencia': 'Conferencia',
        }
        estado['tipo_display'] = nombres_bonitos.get(estado['tipo_evento'], estado['tipo_evento'])

        # Ciudad (municipios del Caqueta + principales de Colombia)
        ciudades = [
            'florencia', 'belen de los andaquies', 'belen',
            'san vicente del caguan', 'san vicente',
            'puerto rico', 'el doncello', 'la montanita',
            'milan', 'valparaiso', 'albania',
            'cartagena del chaira', 'morelia', 'solita', 'solano',
            'bogota', 'medellin', 'cali', 'bucaramanga',
            'barranquilla', 'pereira', 'manizales',
        ]
        ctx_ciudad = ctx_norm
        for ciudad in ciudades:
            if ciudad in ctx_ciudad:
                estado['ciudad'] = ciudad.title()
                break

        # Personas
        m = re.search(r'(\d{1,4})\s*personas?', ctx)
        if not m:
            # Capturar numero suelto despues de "asistiran" o "invitados"
            m = re.search(r'(?:asistiran|invitados?|somos|seran|para)\s+(\d{1,4})', ctx)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 5000:
                estado['personas'] = val

        # Presupuesto
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:millones?|M\b)', ctx)
        if m:
            num = float(m.group(1).replace(',', '.'))
            estado['presupuesto'] = int(num * 1_000_000)
        else:
            limpio = texto_completo.replace('.', '').replace(',', '')
            nums = re.findall(r'\b(\d{6,10})\b', limpio)
            for n in nums:
                val = int(n)
                if 100_000 <= val <= 2_000_000_000:
                    estado['presupuesto'] = val
                    break

        # Fecha
        meses = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
        }
        m = re.search(
            r'(\d{1,2})\s*(?:de|del?)?\s*(enero|febrero|marzo|abril|mayo|junio|'
            r'julio|agosto|septiembre|octubre|noviembre|diciembre)\s*(?:de|del?)?\s*(\d{4})',
            ctx,
        )
        if m:
            dia = m.group(1).zfill(2)
            mes = meses.get(m.group(2))
            anio = m.group(3)
            if mes:
                estado['fecha'] = f"{anio}-{mes}-{dia}"
        if not estado['fecha']:
            m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', texto_completo)
            if m:
                estado['fecha'] = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"

        return estado

    # ──────────────────────────────────────────────────────────────
    # CONSULTA BD SEMANTICA
    # ──────────────────────────────────────────────────────────────

    def _consultar_bd(self, tipo_uri: str, presupuesto: float = None, ciudad: str = None) -> dict:
        resultado = {'servicios': [], 'paquetes': [], 'proveedores': []}
        try:
            if tipo_uri:
                servicios = self.sparql.recomendar_servicios(tipo_uri)
                if presupuesto:
                    # Filtrar servicios que caben en el 40% del presupuesto (para dejar margen)
                    filtrados = [s for s in servicios if float(s.get('precioBase') or 0) <= presupuesto * 0.4]
                    resultado['servicios'] = filtrados[:8] if filtrados else servicios[:8]
                else:
                    resultado['servicios'] = servicios[:8]
                resultado['paquetes'] = self.sparql.recomendar_paquetes(tipo_uri)[:4]

            if ciudad:
                resultado['proveedores'] = self.sparql.obtener_proveedores_por_ciudad(ciudad)[:6]

            if not resultado['proveedores']:
                resultado['proveedores'] = self.sparql.obtener_proveedores_destacados()[:5]

        except Exception as e:
            print(f"[GROQ] Error BD semantica: {e}")
        return resultado

    def _formatear_bd(self, bd: dict, tipo_display: str, presupuesto: float = None) -> str:
        lineas = []

        if bd['servicios']:
            lineas.append(f"SERVICIOS REALES DISPONIBLES PARA {tipo_display.upper()}:")
            for s in bd['servicios']:
                precio = float(s.get('precioBase') or 0)
                cat = s.get('categoria', 'General')
                empresa = s.get('empresa', '')
                nombre = s.get('nombre', '')
                linea = f"  - [{cat}] {nombre}: ${precio:,.0f} COP"
                if empresa:
                    linea += f" | Proveedor: {empresa}"
                lineas.append(linea)

        if bd['paquetes']:
            lineas.append(f"\nPAQUETES DISPONIBLES:")
            for p in bd['paquetes']:
                precio = float(p.get('precioBase') or 0)
                desc = p.get('descuentoPct', '0')
                nombre = p.get('nombre', '')
                lineas.append(f"  - {nombre}: ${precio:,.0f} COP (descuento {desc}%)")

        if bd['proveedores']:
            lineas.append(f"\nPROVEEDORES DISPONIBLES:")
            for p in bd['proveedores']:
                nombre = p.get('nombre', '')
                cal = p.get('calificacion', '')
                ciudad_p = p.get('ciudad', '')
                tel = p.get('telefono', '')
                linea = f"  - {nombre}"
                if cal:
                    linea += f" (Cal: {cal}/5)"
                if ciudad_p:
                    linea += f" | {ciudad_p}"
                if tel:
                    linea += f" | Tel: {tel}"
                lineas.append(linea)

        if presupuesto:
            lineas.append(f"\nPRESUPUESTO DEL CLIENTE: ${presupuesto:,.0f} COP")

        return "\n".join(lineas) if lineas else "Base de datos no disponible."

    # ──────────────────────────────────────────────────────────────
    # RESPUESTA PRINCIPAL
    # ──────────────────────────────────────────────────────────────

    def generar_respuesta(self, mensaje: str, contexto: str = None, usuario_id: int = None) -> str:
        print(f"\n[GROQ] Mensaje: {mensaje[:80]}")

        texto_completo = (contexto or '') + '\n' + mensaje
        estado = self._extraer_estado(texto_completo)

        tipo_uri = estado.get('tipo_evento')
        tipo_display = estado.get('tipo_display') or tipo_uri or ''
        presupuesto = estado.get('presupuesto')
        ciudad = estado.get('ciudad')
        personas = estado.get('personas')
        fecha = estado.get('fecha')

        # Consultar BD solo cuando hay tipo (para las recomendaciones)
        bd_info = "(Aun no se ha elegido tipo de evento para mostrar recomendaciones)"
        if tipo_uri:
            bd = self._consultar_bd(tipo_uri, presupuesto, ciudad)
            bd_info = self._formatear_bd(bd, tipo_display, presupuesto)

        # Resumen de datos recopilados hasta ahora
        datos_ok = []
        datos_faltantes = []
        if tipo_display:
            datos_ok.append(f"TIPO: {tipo_display}")
        else:
            datos_faltantes.append("TIPO DE EVENTO")
        if presupuesto:
            datos_ok.append(f"PRESUPUESTO: ${presupuesto:,.0f} COP")
        else:
            datos_faltantes.append("PRESUPUESTO")
        if personas:
            datos_ok.append(f"PERSONAS: {personas}")
        else:
            datos_faltantes.append("NUMERO DE PERSONAS")
        if ciudad:
            datos_ok.append(f"CIUDAD: {ciudad}")
        else:
            datos_faltantes.append("CIUDAD")
        if fecha:
            datos_ok.append(f"FECHA: {fecha}")
        else:
            datos_faltantes.append("FECHA")

        todos_completos = len(datos_faltantes) == 0

        system_prompt = f"""Eres "Planificador IA", asistente experto en planificacion de eventos en Colombia (principalmente Caqueta).

== ESTADO ACTUAL DE LA CONVERSACION ==
DATOS YA RECOPILADOS:
{chr(10).join(datos_ok) if datos_ok else 'Ninguno todavia'}

DATOS QUE FALTAN:
{chr(10).join(datos_faltantes) if datos_faltantes else 'NINGUNO - TODOS COMPLETOS'}

== DATOS REALES DE LA BASE DE DATOS SEMANTICA ==
{bd_info}

== INSTRUCCIONES ==
FLUJO OBLIGATORIO (en este orden exacto):
1. Pregunta el TIPO DE EVENTO (si no lo tienes)
2. Con el tipo, pregunta el PRESUPUESTO (no personas todavia) 
3. Con tipo + presupuesto, muestra RECOMENDACIONES REALES de la BD y pregunta cuantas PERSONAS asistiran
4. Con tipo + presupuesto + personas, pregunta la CIUDAD
5. Con los 4 anteriores, pregunta la FECHA
6. Con los 5 datos, muestra el RESUMEN FINAL

REGLAS:
- Responde SIEMPRE en espanol con emojis y tono amigable.
- Si ya tienes un dato, NO lo vuelvas a preguntar.
- Cuando tengas TIPO + PRESUPUESTO (paso 3): muestra 3-4 servicios reales de la BD con sus precios reales. Usa EXACTAMENTE los nombres y precios que aparecen arriba en "SERVICIOS REALES". NO inventes precios ni proveedores.
- Si la BD no tiene servicios para ese tipo, dilo honestamente.
- Reconoce: "5 millones", "5M", "5.000.000" como presupuesto.
- Reconoce municipios del Caqueta: Florencia, Belen de los Andaquies, San Vicente del Caguan, Puerto Rico, El Doncello, Morelia, Milan, etc.

FORMATO DEL RESUMEN FINAL (cuando tengas los 5 datos - OBLIGATORIO incluir el bloque):

🎉 ¡Perfecto! Ya tengo todo para tu [TIPO].

📋 **Resumen de tu evento:**
• 🎉 Tipo: [tipo]
• 💰 Presupuesto: $[X] COP
• 👥 Personas: [N]
• 📍 Ciudad: [ciudad]
• 📅 Fecha: [fecha legible]

📦 **Servicios recomendados:**
[3-4 servicios REALES de la BD con precios reales]

---DATOS_EVENTO---
TIPO: {tipo_display if tipo_display else '[tipo]'}
PRESUPUESTO: {presupuesto if presupuesto else '[presupuesto en numero]'}
PERSONAS: {personas if personas else '[personas en numero]'}
CIUDAD: {ciudad if ciudad else '[ciudad]'}
FECHA: {fecha if fecha else '[YYYY-MM-DD]'}
---FIN_DATOS---

✅ Haz clic en **Guardar Evento** para confirmar."""

        user_message = mensaje
        if contexto:
            user_message = f"Historial:\n{contexto}\n\nUsuario: \"{mensaje}\"\n\nResponde naturalmente."

        try:
            print("[GROQ] Llamando API...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.6,
                max_tokens=800,
            )
            respuesta = response.choices[0].message.content
            print(f"[GROQ] OK: {respuesta[:100]}...")
            return respuesta

        except Exception as e:
            print(f"[GROQ ERROR] {e}")
            return f"❌ Error de conexion con Groq: {str(e)}. Verifica tu GROQ_API_KEY en el archivo .env"
