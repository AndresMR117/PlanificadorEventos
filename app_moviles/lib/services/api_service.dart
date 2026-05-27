import 'dart:convert';

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
    defaultValue: 'http://10.0.2.2:8000/api',
  );

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    return _post('/login', {
      'email': email,
      'password': password,
    });
  }

  static Future<Map<String, dynamic>> register({
    required String nombre,
    required String email,
    required String password,
  }) async {
    return _post('/register', {
      'nombre': nombre,
      'email': email,
      'password': password,
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

    throw ApiException(
      _extractMessage(data),
      statusCode: response.statusCode,
    );
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
}
