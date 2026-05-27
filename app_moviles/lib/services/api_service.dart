import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

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
    defaultValue: 'https://planificadoreventos-production.up.railway.app/api',
  );

  static Map<String, dynamic>? currentUser;

  static int? get currentUserId {
    final id = currentUser?['id'];
    if (id is int) return id;
    if (id is String) return int.tryParse(id);
    return null;
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    final user = await _post('/login/', {'email': email, 'password': password});
    currentUser = user;
    return user;
  }

  static Future<Map<String, dynamic>> register({
    required String nombre,
    required String email,
    required String password,
  }) async {
    return _post('/registro/', {
      'nombre': nombre,
      'email': email,
      'password': password,
    });
  }

  static Future<List<Map<String, dynamic>>> getEventosUsuario(int usuarioId) {
    return _getList('/eventos/usuario/$usuarioId/');
  }

  static Future<Map<String, dynamic>> getEvento(int eventoId) {
    return _get('/eventos/$eventoId/');
  }

  static Future<List<Map<String, dynamic>>> getTiposEvento() {
    return _getList('/tipos-evento/');
  }

  static Future<List<Map<String, dynamic>>> getServiciosPorTipo(String tipo) {
    return _getList('/servicios/tipo/${Uri.encodeComponent(tipo)}/');
  }

  static Future<List<Map<String, dynamic>>> getProveedoresDestacados() {
    return _getList('/proveedores/destacados/');
  }

  static Future<Map<String, dynamic>> crearConversacion({
    required int usuarioId,
    String titulo = 'Chat con IA',
  }) {
    return _post('/conversaciones/crear/', {
      'usuario_id': usuarioId,
      'titulo': titulo,
    });
  }

  static Future<Map<String, dynamic>> enviarChat({
    required String mensaje,
    int? conversacionId,
  }) {
    return _post('/chatbot/groq/', {
      'mensaje': mensaje,
      'usuario_id': currentUserId,
      if (conversacionId != null) 'conversacion_id': conversacionId,
    });
  }

  static Future<Map<String, dynamic>> guardarEvento({
    required int usuarioId,
    int? conversacionId,
    required String nombre,
    required String tipoEvento,
    required String fechaEvento,
    required int numPersonas,
    required num presupuestoTotal,
    required String ciudad,
  }) {
    return _post('/eventos/guardar/', {
      'usuario_id': usuarioId,
      'conversacion_id': conversacionId,
      'nombre': nombre,
      'tipo_evento': tipoEvento,
      'fecha_evento': fechaEvento,
      'num_personas': numPersonas,
      'presupuesto_total': presupuestoTotal,
      'ciudad': ciudad,
    });
  }

  static Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse('$baseUrl$path');

    final response = await http.post(
      uri,
      headers: const {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(body),
    );

    final data = _decodeResponse(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    }

    throw ApiException(_extractMessage(data), statusCode: response.statusCode);
  }

  static Future<Map<String, dynamic>> _get(String path) async {
    final uri = Uri.parse('$baseUrl$path');

    final response = await http.get(
      uri,
      headers: const {'Accept': 'application/json'},
    );

    final data = _decodeResponse(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    }

    throw ApiException(_extractMessage(data), statusCode: response.statusCode);
  }

  static Future<List<Map<String, dynamic>>> _getList(String path) async {
    final uri = Uri.parse('$baseUrl$path');

    final response = await http.get(
      uri,
      headers: const {'Accept': 'application/json'},
    );

    final decoded = response.body.isEmpty ? [] : jsonDecode(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (decoded is List) {
        return decoded
            .whereType<Map>()
            .map((item) => Map<String, dynamic>.from(item))
            .toList();
      }

      throw const ApiException('La respuesta del servidor no es una lista');
    }

    final data = decoded is Map
        ? Map<String, dynamic>.from(decoded)
        : <String, dynamic>{};

    throw ApiException(_extractMessage(data), statusCode: response.statusCode);
  }

  static Map<String, dynamic> _decodeResponse(String body) {
    if (body.isEmpty) return <String, dynamic>{};

    final decoded = jsonDecode(body);

    if (decoded is Map<String, dynamic>) {
      return decoded;
    }

    return {'data': decoded};
  }

  static String _extractMessage(Map<String, dynamic> data) {
    final message = data['message'] ?? data['error'] ?? data['mensaje'];

    if (message is String && message.isNotEmpty) {
      return message;
    }

    return 'No se pudo completar la solicitud';
  }

  static Future<void> logout() async {
    currentUser = null;

    final prefs = await SharedPreferences.getInstance();

    await prefs.remove('usuario');
    await prefs.remove('conversacionId');

    debugPrint('SESION CERRADA');
  }
}
