import 'package:flutter/material.dart';

import '../services/api_service.dart';

class ChatbotPage extends StatefulWidget {
  const ChatbotPage({super.key});

  @override
  State<ChatbotPage> createState() => _ChatbotPageState();
}

class _ChatbotPageState extends State<ChatbotPage> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool isTyping = false;
  bool saving = false;
  int? conversacionId;

  Map<String, dynamic> estadoEvento = {
    'tipo': null,
    'presupuesto': null,
    'personas': null,
    'ciudad': null,
    'fecha': null,
  };

  final List<Map<String, dynamic>> messages = [
    {
      'role': 'assistant',
      'message':
          'Hola. Soy tu asistente de Flow Events. Estoy listo para ayudarte a organizar tu proximo evento.',
      'time': 'Ahora',
    },
  ];

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> asegurarConversacion() async {
    if (conversacionId != null) return;

    final usuarioId = ApiService.currentUserId;
    if (usuarioId == null) return;

    final data = await ApiService.crearConversacion(usuarioId: usuarioId);
    final id = data['id'];
    if (id is int) conversacionId = id;
  }

  Future<void> sendMessage([String? text]) async {
    final mensaje = text ?? _controller.text.trim();
    if (mensaje.isEmpty || isTyping) return;

    setState(() {
      messages.add({'role': 'user', 'message': mensaje, 'time': getTime()});
      isTyping = true;
    });

    _controller.clear();
    scrollBottom();

    try {
      await asegurarConversacion();
      final data = await ApiService.enviarChat(
        mensaje: mensaje,
        conversacionId: conversacionId,
      );

      final id = data['conversacion_id'];
      if (id is int) conversacionId = id;

      actualizarEstadoEvento(datosDesdeBackend(data));

      final respuesta = data['respuesta']?.toString() ?? '';
      actualizarEstadoEvento(extraerDatosParciales(respuesta));
      final respuestaLimpia = limpiarRespuesta(respuesta);

      setState(() {
        messages.add({
          'role': 'assistant',
          'message': respuestaLimpia.isEmpty
              ? 'Recibi tu mensaje, pero la API no devolvio una respuesta.'
              : respuestaLimpia,
          'time': getTime(),
        });
      });
    } catch (e) {
      setState(() {
        messages.add({
          'role': 'assistant',
          'message':
              'No pude conectar con el chatbot. Revisa que Django este corriendo y que GROQ_API_KEY este configurada.',
          'time': getTime(),
        });
      });
    } finally {
      if (!mounted) return;
      setState(() {
        isTyping = false;
      });
      scrollBottom();
    }
  }

  Map<String, dynamic> datosDesdeBackend(Map<String, dynamic> data) {
    return {
      'tipo': normalizarTipoEvento(data['tipo_evento']?.toString()),
      'presupuesto': data['presupuesto'],
      'personas': data['num_personas'],
      'ciudad': data['ciudad'],
      'fecha': data['fecha'],
    };
  }

  void actualizarEstadoEvento(Map<String, dynamic> datos) {
    var cambio = false;

    void setCampo(String campo, dynamic valor) {
      if (valor == null) return;
      if (valor is String && valor.trim().isEmpty) return;
      if (valor is String && valor.contains('[')) return;
      estadoEvento[campo] = valor;
      cambio = true;
    }

    setCampo('tipo', datos['tipo']);
    setCampo('presupuesto', parseNumero(datos['presupuesto']));
    setCampo('personas', parseNumero(datos['personas']));
    setCampo('ciudad', datos['ciudad']);
    setCampo('fecha', datos['fecha']);

    if (cambio && mounted) setState(() {});
  }

  bool get eventoCompleto {
    final completo =
        estadoEvento['tipo'] != null &&
        estadoEvento['presupuesto'] != null &&
        estadoEvento['personas'] != null &&
        estadoEvento['ciudad'] != null;

    debugPrint('EVENTO COMPLETO => $completo');

    debugPrint('ESTADO ACTUAL => $estadoEvento');

    return completo;
  }

  int? parseNumero(dynamic value) {
    if (value == null) return null;
    if (value is int) return value;
    if (value is num) return value.toInt();
    final limpio = value.toString().replaceAll(RegExp(r'[^0-9]'), '');
    if (limpio.isEmpty) return null;
    final parsed = int.tryParse(limpio);
    if (parsed == null || parsed == 0) return null;
    return parsed;
  }

  String? normalizarTipoEvento(String? tipo) {
    if (tipo == null || tipo.trim().isEmpty) return null;
    final t = tipo
        .toLowerCase()
        .trim()
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ñ', 'n');

    if (t.contains('boda') || t.contains('matrimonio')) return 'Boda';
    if (t.contains('cumple')) return 'Cumpleaños';
    if (t.contains('grado') || t.contains('gradu')) return 'Grado';
    if (t.contains('quince')) return 'Quinceañera';
    if (t.contains('baby') || t.contains('shower')) return 'BabyShower';
    if (t.contains('infantil')) return 'FiestaInfantil';
    if (t.contains('despedida')) return 'Despedida';
    if (t.contains('aniversario')) return 'Aniversario';
    if (t.contains('corporativo')) return 'EventoCorporativo';
    return tipo.trim();
  }

  // SOLO reemplaza la función extraerDatosParciales por esta versión

  Map<String, dynamic> extraerDatosParciales(String respuesta) {
    final datos = <String, dynamic>{};

    // =====================================================
    // BLOQUE ESTRUCTURADO
    // =====================================================

    final bloque = RegExp(
      r'---DATOS_EVENTO---([\s\S]*?)---FIN_DATOS---',
      caseSensitive: false,
    ).firstMatch(respuesta);

    if (bloque != null) {
      final contenido = bloque.group(1) ?? '';

      String? getCampo(String campo) {
        final match = RegExp(
          '$campo:\\s*(.+)',
          caseSensitive: false,
        ).firstMatch(contenido);

        return match?.group(1)?.trim();
      }

      final tipoRaw = getCampo('TIPO');

      final presupuestoRaw = (getCampo('PRESUPUESTO') ?? '').replaceAll(
        RegExp(r'[^0-9]'),
        '',
      );

      final personasRaw = (getCampo('PERSONAS') ?? '').replaceAll(
        RegExp(r'[^0-9]'),
        '',
      );

      final ciudadRaw = getCampo('CIUDAD');

      final fechaRaw = getCampo('FECHA');

      // TIPO
      if (tipoRaw != null && tipoRaw.isNotEmpty && !tipoRaw.contains('[')) {
        datos['tipo'] = normalizarTipoEvento(tipoRaw);
      }

      // PRESUPUESTO
      if (presupuestoRaw.isNotEmpty) {
        final valor = int.tryParse(presupuestoRaw);

        if (valor != null && valor > 0) {
          datos['presupuesto'] = valor;
        }
      }

      // PERSONAS
      if (personasRaw.isNotEmpty) {
        final valor = int.tryParse(personasRaw);

        if (valor != null && valor > 0) {
          datos['personas'] = valor;
        }
      }

      // CIUDAD
      if (ciudadRaw != null &&
          ciudadRaw.isNotEmpty &&
          !ciudadRaw.contains('[')) {
        datos['ciudad'] = ciudadRaw;
      }

      // FECHA
      if (fechaRaw != null &&
          RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(fechaRaw)) {
        datos['fecha'] = fechaRaw;
      }
    }

    // =====================================================
    // HEURÍSTICA INTELIGENTE
    // =====================================================

    // Tipo evento
    if (datos['tipo'] == null) {
      final match = RegExp(
        r'(boda|cumpleaños|cumpleanos|grado|quinceañera|quinceanera|baby shower|evento corporativo|corporativo)',
        caseSensitive: false,
      ).firstMatch(respuesta);

      if (match != null) {
        datos['tipo'] = normalizarTipoEvento(match.group(1));
      }
    }

    // Presupuesto
    if (datos['presupuesto'] == null) {
      final match = RegExp(
        r'(\$?\s?\d[\d.,]{3,})',
        caseSensitive: false,
      ).firstMatch(respuesta);

      if (match != null) {
        final limpio = match.group(1)!.replaceAll(RegExp(r'[^0-9]'), '');

        final valor = int.tryParse(limpio);

        if (valor != null && valor > 1000) {
          datos['presupuesto'] = valor;
        }
      }
    }

    // Personas
    if (datos['personas'] == null) {
      final match = RegExp(
        r'(\d+)\s*(personas|invitados)',
        caseSensitive: false,
      ).firstMatch(respuesta);

      if (match != null) {
        final valor = int.tryParse(match.group(1)!);

        if (valor != null && valor > 0) {
          datos['personas'] = valor;
        }
      }
    }

    // Ciudad
    if (datos['ciudad'] == null) {
      final ciudades = [
        'florencia',
        'neiva',
        'bogota',
        'medellin',
        'cali',
        'cartagena',
        'barranquilla',
        'villavicencio',
        'ibague',
      ];

      for (final ciudad in ciudades) {
        if (respuesta.toLowerCase().contains(ciudad)) {
          datos['ciudad'] = ciudad;
          break;
        }
      }
    }

    // Fecha
    if (datos['fecha'] == null) {
      final match = RegExp(
        r'(\d{4}-\d{2}-\d{2})',
        caseSensitive: false,
      ).firstMatch(respuesta);

      if (match != null) {
        datos['fecha'] = match.group(1);
      }
    }

    // =====================================================
    // LIMPIEZA
    // =====================================================

    datos.removeWhere((_, value) => value == null || value == '');

    debugPrint('DATOS EXTRAIDOS => $datos');

    return datos;
  }

  String limpiarRespuesta(String respuesta) {
    return respuesta
        .replaceAll(RegExp(r'---DATOS_EVENTO---[\s\S]*?---FIN_DATOS---'), '')
        .replaceAll('**', '')
        .trim();
  }

  Future<void> guardarEvento() async {
    final usuarioId = ApiService.currentUserId;
    if (usuarioId == null || !eventoCompleto) return;

    setState(() {
      saving = true;
    });

    final fecha =
        estadoEvento['fecha']?.toString() ??
        DateTime.now()
            .add(const Duration(days: 90))
            .toIso8601String()
            .split('T')
            .first;
    final tipo = estadoEvento['tipo'].toString();

    try {
      await ApiService.guardarEvento(
        usuarioId: usuarioId,
        conversacionId: conversacionId,
        nombre: '$tipo - $fecha',
        tipoEvento: tipo,
        fechaEvento: fecha,
        numPersonas: parseNumero(estadoEvento['personas']) ?? 1,
        presupuestoTotal: parseNumero(estadoEvento['presupuesto']) ?? 0,
        ciudad: estadoEvento['ciudad']?.toString() ?? 'Florencia',
      );

      setState(() {
        messages.add({
          'role': 'assistant',
          'message':
              'Evento guardado exitosamente. Ya puedes verlo en Mis Eventos.',
          'time': getTime(),
        });
        estadoEvento = {
          'tipo': null,
          'presupuesto': null,
          'personas': null,
          'ciudad': null,
          'fecha': null,
        };
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo guardar el evento: $e')),
      );
    } finally {
      if (!mounted) return;
      setState(() {
        saving = false;
      });
      scrollBottom();
    }
  }

  void scrollBottom() {
    Future.delayed(const Duration(milliseconds: 300), () {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 200,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOut,
      );
    });
  }

  String getTime() {
    final now = TimeOfDay.now();
    final hour = now.hourOfPeriod == 0 ? 12 : now.hourOfPeriod;
    final minute = now.minute.toString().padLeft(2, '0');
    final period = now.period == DayPeriod.am ? 'AM' : 'PM';
    return '$hour:$minute $period';
  }

  Widget buildMessage(Map<String, dynamic> msg) {
    final isUser = msg['role'] == 'user';

    return Padding(
      padding: const EdgeInsets.only(bottom: 22),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        children: [
          if (!isUser)
            Container(
              width: 38,
              height: 38,
              margin: const EdgeInsets.only(right: 10),
              decoration: BoxDecoration(
                color: const Color(0xFF2ECC71),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.auto_awesome,
                color: Colors.white,
                size: 18,
              ),
            ),
          Flexible(
            child: Column(
              crossAxisAlignment: isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 14,
                  ),
                  decoration: BoxDecoration(
                    color: isUser ? const Color(0xFF2563EB) : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft: Radius.circular(isUser ? 18 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 18),
                    ),
                    boxShadow: isUser
                        ? []
                        : [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                  ),
                  child: Text(
                    msg['message'].toString(),
                    style: TextStyle(
                      color: isUser ? Colors.white : const Color(0xFF1A1A2E),
                      fontSize: 14.5,
                      height: 1.5,
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '${isUser ? 'Tu' : 'Flow AI'} - ${msg['time']}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF6B7280),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildChip(String text, IconData icon) {
    return InkWell(
      onTap: () => sendMessage(text),
      borderRadius: BorderRadius.circular(30),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: const Color(0xFF6B7280)),
            const SizedBox(width: 8),
            Text(
              text,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildTypingIndicator() {
    return const Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          SizedBox(width: 8),
          CircularProgressIndicator(strokeWidth: 2),
          SizedBox(width: 12),
          Text('Escribiendo...', style: TextStyle(color: Color(0xFF6B7280))),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F0),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFFF0F2F0),
        foregroundColor: const Color(0xFF1A1A2E),
        title: const Text(
          'Crear Evento',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              children: [
                ...messages.map(buildMessage),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    buildChip('Planificar Boda', Icons.favorite),
                    buildChip('Evento Corporativo', Icons.business_center),
                    buildChip('Cumpleanos', Icons.cake),
                    buildChip('Quinceanera', Icons.star),
                  ],
                ),
                const SizedBox(height: 24),
                if (isTyping) buildTypingIndicator(),
              ],
            ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 8, 18, 18),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: eventoCompleto && !saving
                          ? guardarEvento
                          : null,
                      icon: saving
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.save),
                      label: Text(
                        eventoCompleto
                            ? 'Guardar Evento'
                            : 'Completa tipo, presupuesto, personas y ciudad',
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2ECC71),
                        foregroundColor: Colors.white,
                        disabledBackgroundColor: const Color(0xFFE5E7EB),
                        disabledForegroundColor: const Color(0xFF6B7280),
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.06),
                          blurRadius: 15,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            minLines: 1,
                            maxLines: 5,
                            decoration: const InputDecoration(
                              border: InputBorder.none,
                              hintText:
                                  'Escribe el tipo de evento o una idea...',
                              hintStyle: TextStyle(color: Color(0xFF6B7280)),
                            ),
                            onSubmitted: (_) => sendMessage(),
                          ),
                        ),
                        Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFF2ECC71),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: IconButton(
                            onPressed: isTyping ? null : sendMessage,
                            icon: const Icon(Icons.send, color: Colors.white),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
