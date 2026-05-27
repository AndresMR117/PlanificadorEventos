import 'package:flutter/material.dart';

import 'chatbot_screen.dart';
import 'eventos_screen.dart';
import 'servicios_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  void abrir(BuildContext context, Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F8F6),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.only(bottom: 32),
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          color: const Color(0xFF2ECC71),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.auto_awesome,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'Flow Events',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    onPressed: () => abrir(context, const MisEventosScreen()),
                    icon: const Icon(Icons.event_note),
                    tooltip: 'Mis Eventos',
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFD4F5E2),
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: const Text(
                      'Inteligencia Artificial',
                      style: TextStyle(
                        color: Color(0xFF1A9E52),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Crea momentos\ninolvidables',
                    style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                      height: 1.1,
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'La IA que entiende tu vision para cada celebracion. MySQL guarda tus usuarios, eventos e historial; Fuseki queda listo para recomendaciones semanticas.',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.black54,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 28),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => abrir(context, const ChatbotPage()),
                          icon: const Icon(Icons.auto_awesome),
                          label: const Text('Crear Evento'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2ECC71),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => abrir(context, const ServiciosScreen()),
                          icon: const Icon(Icons.room_service),
                          label: const Text('Servicios'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFF1A1A2E),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => abrir(context, const MisEventosScreen()),
                      icon: const Icon(Icons.calendar_month),
                      label: const Text('Mis Eventos'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF1A1A2E),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),
                  const SizedBox(height: 36),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(24),
                    child: Stack(
                      children: [
                        Image.network(
                          'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=900&q=80',
                          height: 250,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                        Positioned(
                          left: 16,
                          bottom: 16,
                          child: Container(
                            width: 230,
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.94),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: const Row(
                              children: [
                                Icon(Icons.smart_toy, color: Color(0xFF2ECC71)),
                                SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    'Paquetes ideales de acuerdo a tu evento.',
                                    style: TextStyle(fontWeight: FontWeight.w600),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 34),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: const [
                      _Stat(value: '10k+', label: 'Eventos'),
                      _Stat(value: '500+', label: 'Proveedores'),
                      _Stat(value: '98%', label: 'Satisfaccion'),
                    ],
                  ),
                  const SizedBox(height: 34),
                  const Text(
                    'Categorias de excelencia',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  _CategoryTile(
                    title: 'Bodas',
                    subtitle: 'Elegancia y romance diseñado a tu medida.',
                    image:
                        'https://images.unsplash.com/photo-1519741497674-611481863552?w=700&q=80',
                  ),
                  const SizedBox(height: 14),
                  _CategoryTile(
                    title: 'Graduaciones',
                    subtitle: 'Logros que impulsan el futuro.',
                    image:
                        'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=700&q=80',
                  ),
                  const SizedBox(height: 14),
                  _CategoryTile(
                    title: 'Cumpleanos',
                    subtitle: 'Alegria y comunidad en cada detalle.',
                    image:
                        'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=700&q=80',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.value, required this.label});

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFF2ECC71),
          ),
        ),
        const SizedBox(height: 6),
        Text(label),
      ],
    );
  }
}

class _CategoryTile extends StatelessWidget {
  const _CategoryTile({
    required this.title,
    required this.subtitle,
    required this.image,
  });

  final String title;
  final String subtitle;
  final String image;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(18),
      child: Stack(
        children: [
          Image.network(
            image,
            height: 160,
            width: double.infinity,
            fit: BoxFit.cover,
          ),
          Container(
            height: 160,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withOpacity(0.72),
                ],
              ),
            ),
          ),
          Positioned(
            left: 18,
            right: 18,
            bottom: 16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
