import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue:
        'https://planificadoreventos-production.up.railway.app/api',
  );

  static Map<String, dynamic>? currentUser;

  // =====================================================
  // USER
  // =====================================================

  static int? get currentUserId {
    final id = currentUser?['id'];

    if (id is int) return id;

    if (id is String) {
      return int.tryParse(id);
    }

    return null;
  }

  // =====================================================
  // AUTH
  // =====================================================

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    final user = await _post(
      '/login/',
      {
        'email': email,
        'password': password,
      },
    );

    currentUser = user;

    debugPrint('LOGIN OK => $user');

    return user;
  }

  static Future<Map<String, dynamic>> register({
    required String nombre,
    required String email,
    required String password,
  }) async {
    return _post(
      '/registro/',
      {
        'nombre': nombre,
        'email': email,
        'password': password,
      },
    );
  }

  // =====================================================
  // EVENTOS
  // =====================================================

  static Future<List<Map<String, dynamic>>>
      getEventosUsuario(
    int usuarioId,
  ) {
    return _getList(
      '/eventos/usuario/$usuarioId/',
    );
  }

  static Future<Map<String, dynamic>> getEvento(
    int eventoId,
  ) {
    return _get('/eventos/$eventoId/');
  }

  static Future<List<Map<String, dynamic>>>
      getTiposEvento() {
    return _getList('/tipos-evento/');
  }

  static Future<List<Map<String, dynamic>>>
      getServiciosPorTipo(
    String tipo,
  ) {
    return _getList(
      '/servicios/tipo/${Uri.encodeComponent(tipo)}/',
    );
  }

  static Future<List<Map<String, dynamic>>>
      getProveedoresDestacados() {
    return _getList(
      '/proveedores/destacados/',
    );
  }

  // =====================================================
  // CHATBOT
  // =====================================================

  static Future<Map<String, dynamic>>
      crearConversacion({
    required int usuarioId,
    String titulo = 'Chat con IA',
  }) async {
    debugPrint(
      'CREANDO CONVERSACION => usuario: $usuarioId',
    );

    return _post(
      '/conversaciones/crear/',
      {
        'usuario_id': usuarioId,
        'titulo': titulo,
      },
    );
  }

  static Future<Map<String, dynamic>>
      enviarChat({
    required String mensaje,
    int? conversacionId,
  }) async {
    debugPrint('================================');
    debugPrint('ENVIANDO CHAT');
    debugPrint('MENSAJE => $mensaje');
    debugPrint(
      'USUARIO => $currentUserId',
    );
    debugPrint(
      'CONVERSACION => $conversacionId',
    );
    debugPrint('================================');

    return _post(
      '/chatbot/groq/',
      {
        'mensaje': mensaje,
        'usuario_id': currentUserId,
        if (conversacionId != null)
          'conversacion_id':
              conversacionId,
      },
    );
  }

  static Future<Map<String, dynamic>>
      guardarEvento({
    required int usuarioId,
    int? conversacionId,
    required String nombre,
    required String tipoEvento,
    required String fechaEvento,
    required int numPersonas,
    required num presupuestoTotal,
    required String ciudad,
  }) async {
    final body = {
      'usuario_id': usuarioId,
      'conversacion_id': conversacionId,
      'nombre': nombre,
      'tipo_evento': tipoEvento,
      'fecha_evento': fechaEvento,
      'num_personas': numPersonas,
      'presupuesto_total':
          presupuestoTotal,
      'ciudad': ciudad,
    };

    debugPrint(
      'GUARDANDO EVENTO => ${jsonEncode(body)}',
    );

    return _post(
      '/eventos/guardar/',
      body,
    );
  }

  // =====================================================
  // POST
  // =====================================================

  static Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body,
  ) async {
    try {
      final uri =
          Uri.parse('$baseUrl$path');

      debugPrint('POST => $uri');

      final response = await http
          .post(
            uri,
            headers: const {
              'Accept':
                  'application/json',
              'Content-Type':
                  'application/json',
            },
            body: jsonEncode(body),
          )
          .timeout(
            const Duration(
              seconds: 60,
            ),
          );

      debugPrint(
        'STATUS => ${response.statusCode}',
      );

      debugPrint(
        'BODY => ${response.body}',
      );

      final data =
          _decodeResponse(response.body);

      if (response.statusCode >= 200 &&
          response.statusCode < 300) {
        return data;
      }

      throw ApiException(
        _extractMessage(data),
        statusCode:
            response.statusCode,
      );
    } on TimeoutException {
      throw const ApiException(
        'La conexión tardó demasiado.',
      );
    } catch (e, stack) {
      debugPrint('POST ERROR => $e');
      debugPrint(stack.toString());

      rethrow;
    }
  }

  // =====================================================
  // GET
  // =====================================================

  static Future<Map<String, dynamic>> _get(
    String path,
  ) async {
    try {
      final uri =
          Uri.parse('$baseUrl$path');

      debugPrint('GET => $uri');

      final response = await http
          .get(
            uri,
            headers: const {
              'Accept':
                  'application/json',
            },
          )
          .timeout(
            const Duration(
              seconds: 60,
            ),
          );

      debugPrint(
        'STATUS => ${response.statusCode}',
      );

      final data =
          _decodeResponse(response.body);

      if (response.statusCode >= 200 &&
          response.statusCode < 300) {
        return data;
      }

      throw ApiException(
        _extractMessage(data),
        statusCode:
            response.statusCode,
      );
    } on TimeoutException {
      throw const ApiException(
        'La conexión tardó demasiado.',
      );
    } catch (e, stack) {
      debugPrint('GET ERROR => $e');
      debugPrint(stack.toString());

      rethrow;
    }
  }

  // =====================================================
  // GET LIST
  // =====================================================

  static Future<List<Map<String, dynamic>>>
      _getList(
    String path,
  ) async {
    try {
      final uri =
          Uri.parse('$baseUrl$path');

      debugPrint('GET LIST => $uri');

      final response = await http
          .get(
            uri,
            headers: const {
              'Accept':
                  'application/json',
            },
          )
          .timeout(
            const Duration(
              seconds: 60,
            ),
          );

      debugPrint(
        'STATUS => ${response.statusCode}',
      );

      final decoded =
          response.body.isEmpty
              ? []
              : jsonDecode(
                  response.body,
                );

      if (response.statusCode >= 200 &&
          response.statusCode < 300) {
        if (decoded is List) {
          return decoded
              .whereType<Map>()
              .map(
                (item) =>
                    Map<String,
                        dynamic>.from(
                  item,
                ),
              )
              .toList();
        }

        throw const ApiException(
          'La respuesta no es una lista',
        );
      }

      final data = decoded is Map
          ? Map<String, dynamic>.from(
              decoded,
            )
          : <String, dynamic>{};

      throw ApiException(
        _extractMessage(data),
        statusCode:
            response.statusCode,
      );
    } on TimeoutException {
      throw const ApiException(
        'La conexión tardó demasiado.',
      );
    } catch (e, stack) {
      debugPrint(
        'GET LIST ERROR => $e',
      );

      debugPrint(stack.toString());

      rethrow;
    }
  }

  // =====================================================
  // HELPERS
  // =====================================================

  static Map<String, dynamic>
      _decodeResponse(
    String body,
  ) {
    if (body.isEmpty) {
      return <String, dynamic>{};
    }

    final decoded = jsonDecode(body);

    if (decoded
        is Map<String, dynamic>) {
      return decoded;
    }

    return {
      'data': decoded,
    };
  }

  static String _extractMessage(
    Map<String, dynamic> data,
  ) {
    final message =
        data['message'] ??
            data['error'] ??
            data['mensaje'];

    if (message is String &&
        message.isNotEmpty) {
      return message;
    }

    return 'No se pudo completar la solicitud';
  }
}