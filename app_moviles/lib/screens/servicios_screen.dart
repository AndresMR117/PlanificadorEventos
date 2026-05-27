import 'package:flutter/material.dart';

import '../services/api_service.dart';

class ServiciosScreen extends StatefulWidget {
  const ServiciosScreen({super.key});

  @override
  State<ServiciosScreen> createState() => _ServiciosScreenState();
}

class _ServiciosScreenState extends State<ServiciosScreen> {
  final tiposFallback = const [
    'Boda',
    'Cumpleanos',
    'Grado',
    'QuinceAnos',
    'EventoCorporativo',
  ];

  String? tipoSeleccionado;
  bool loading = false;
  String? error;
  List<String> tiposEvento = [];
  List<Map<String, dynamic>> servicios = [];

  @override
  void initState() {
    super.initState();
    cargarTiposEvento();
  }

  Future<void> cargarTiposEvento() async {
    try {
      final data = await ApiService.getTiposEvento();
      final tipos = data
          .map((item) => item['nombre']?.toString())
          .whereType<String>()
          .where((nombre) => nombre.isNotEmpty)
          .toList();

      setState(() {
        tiposEvento = tipos.isEmpty ? tiposFallback : tipos;
        tipoSeleccionado = tiposEvento.first;
      });
    } catch (_) {
      setState(() {
        tiposEvento = tiposFallback;
        tipoSeleccionado = tiposEvento.first;
      });
    }
  }

  Future<void> cargarServiciosPorTipo() async {
    final tipo = tipoSeleccionado;
    if (tipo == null) return;

    setState(() {
      loading = true;
      error = null;
      servicios = [];
    });

    try {
      final data = await ApiService.getServiciosPorTipo(tipo);
      setState(() {
        servicios = data;
      });
    } catch (e) {
      setState(() {
        error = 'No se pudieron cargar servicios. Revisa la API semantica.';
      });
    } finally {
      if (!mounted) return;
      setState(() {
        loading = false;
      });
    }
  }

  String precioServicio(Map<String, dynamic> servicio) {
    final precio = servicio['precioBase'] ?? servicio['precioPorPersona'];
    if (precio == null || precio.toString().isEmpty) return 'Precio por confirmar';
    return '\$${precio.toString()} COP';
  }

  IconData iconoServicio(String? categoria) {
    final texto = categoria?.toLowerCase() ?? '';
    if (texto.contains('foto')) return Icons.camera_alt;
    if (texto.contains('musica') || texto.contains('audio')) return Icons.music_note;
    if (texto.contains('catering') || texto.contains('comida')) return Icons.restaurant;
    if (texto.contains('decor')) return Icons.celebration;
    return Icons.auto_awesome;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xffF7F8F6),
      appBar: AppBar(
        title: const Text(
          'Servicios',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF1A1A2E),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Servicios por tipo de evento',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Esta seccion queda lista para llenarse desde Apache Jena Fuseki.',
              style: TextStyle(color: Color(0xFF6B7280)),
            ),
            const SizedBox(height: 25),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: tipoSeleccionado,
                  isExpanded: true,
                  hint: const Text('Selecciona un tipo de evento'),
                  items: tiposEvento.map((tipo) {
                    return DropdownMenuItem(
                      value: tipo,
                      child: Text(tipo),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      tipoSeleccionado = value;
                    });
                  },
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: loading ? null : cargarServiciosPorTipo,
                icon: loading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.search),
                label: const Text('Buscar'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2ECC71),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 25),
            if (error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              ),
            Expanded(
              child: servicios.isEmpty
                  ? const Center(
                      child: Text(
                        'Cuando conectes Fuseki en Railway, aqui apareceran los servicios reales.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Color(0xFF6B7280)),
                      ),
                    )
                  : GridView.builder(
                      itemCount: servicios.length,
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 16,
                        mainAxisSpacing: 16,
                        childAspectRatio: 0.82,
                      ),
                      itemBuilder: (context, index) {
                        final servicio = servicios[index];
                        final categoria = servicio['categoria']?.toString();

                        return Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: const Color(0xFFE5E7EB)),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: const Color(0xFFD4F5E2),
                                child: Icon(
                                  iconoServicio(categoria),
                                  color: const Color(0xFF1A9E52),
                                  size: 30,
                                ),
                              ),
                              const SizedBox(height: 14),
                              Text(
                                servicio['nombre']?.toString() ?? 'Servicio',
                                textAlign: TextAlign.center,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                precioServicio(servicio),
                                textAlign: TextAlign.center,
                                style: const TextStyle(color: Color(0xFF6B7280)),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                servicio['empresa']?.toString() ?? 'Proveedor por confirmar',
                                textAlign: TextAlign.center,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 12),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
