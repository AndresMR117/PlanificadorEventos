import 'package:flutter/material.dart';

import '../services/api_service.dart';

class MisEventosScreen extends StatefulWidget {
  const MisEventosScreen({super.key});

  @override
  State<MisEventosScreen> createState() => _MisEventosScreenState();
}

class _MisEventosScreenState extends State<MisEventosScreen> {
  final TextEditingController buscarController = TextEditingController();

  String filtroEstado = '';
  late Future<List<Map<String, dynamic>>> eventosFuture;

  @override
  void initState() {
    super.initState();
    eventosFuture = cargarEventos();
  }

  @override
  void dispose() {
    buscarController.dispose();
    super.dispose();
  }

  Future<List<Map<String, dynamic>>> cargarEventos() async {
    final usuarioId = ApiService.currentUserId;

    if (usuarioId == null) {
      throw const ApiException('Inicia sesion para ver tus eventos');
    }

    final eventos = await ApiService.getEventosUsuario(usuarioId);

    return eventos.map((evento) {
      return {
        ...evento,
        'tipo': evento['tipo_evento'] ?? 'Evento',
        'fecha': evento['fecha_evento'] ?? 'Sin fecha',
        'personas': evento['num_personas'] ?? 0,
        'presupuesto': evento['presupuesto_total'] ?? 0,
        'imagen': imagenPorTipo(evento['tipo_evento']?.toString()),
      };
    }).toList();
  }

  List<Map<String, dynamic>> filtrarEventos(List<Map<String, dynamic>> eventos) {
    return eventos.where((evento) {
      final texto = buscarController.text.toLowerCase();
      final nombre = evento['nombre']?.toString().toLowerCase() ?? '';
      final ciudad = evento['ciudad']?.toString().toLowerCase() ?? '';
      final estado = evento['estado']?.toString() ?? '';

      final coincideBusqueda = nombre.contains(texto) || ciudad.contains(texto);
      final coincideEstado = filtroEstado.isEmpty || estado == filtroEstado;

      return coincideBusqueda && coincideEstado;
    }).toList();
  }

  String imagenPorTipo(String? tipo) {
    switch (tipo) {
      case 'Boda':
        return 'https://images.unsplash.com/photo-1519741497674-611481863552?w=800';
      case 'Cumpleanos':
      case 'Cumpleaños':
        return 'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800';
      case 'Grado':
        return 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800';
      default:
        return 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&q=80';
    }
  }

  Color getEstadoColor(String estado) {
    switch (estado) {
      case 'confirmado':
        return Colors.green;
      case 'planificando':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String getEstadoTexto(String estado) {
    switch (estado) {
      case 'confirmado':
        return 'Confirmado';
      case 'planificando':
        return 'En proceso';
      case 'borrador':
        return 'Borrador';
      case 'completado':
        return 'Completado';
      case 'cancelado':
        return 'Cancelado';
      default:
        return 'Borrador';
    }
  }

  Future<void> recargarEventos() async {
    final nuevosEventos = cargarEventos();
    setState(() {
      eventosFuture = nuevosEventos;
    });
    await nuevosEventos;
  }

  void mostrarDetalle(Map<String, dynamic> evento) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(30),
        ),
      ),
      builder: (_) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 50,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),
              const SizedBox(height: 25),
              Text(
                evento['nombre']?.toString() ?? 'Evento',
                style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              detalleItem(Icons.category, 'Tipo', evento['tipo'].toString()),
              detalleItem(
                Icons.location_on,
                'Ciudad',
                evento['ciudad']?.toString() ?? 'No especificada',
              ),
              detalleItem(Icons.calendar_month, 'Fecha', evento['fecha'].toString()),
              detalleItem(Icons.people, 'Personas', '${evento['personas']}'),
              detalleItem(Icons.attach_money, 'Presupuesto', '\$${evento['presupuesto']}'),
              detalleItem(
                Icons.info,
                'Estado',
                getEstadoTexto(evento['estado']?.toString() ?? ''),
              ),
              const SizedBox(height: 25),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Gestionar Evento'),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  Widget detalleItem(IconData icon, String titulo, String valor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Icon(icon, color: Colors.green),
          const SizedBox(width: 12),
          Text(
            '$titulo: ',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Expanded(child: Text(valor)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xfff7f8f6),
      appBar: AppBar(
        title: const Text('Mis Eventos'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: buscarController,
              onChanged: (_) {
                setState(() {});
              },
              decoration: InputDecoration(
                hintText: 'Buscar eventos...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: filtroBoton(texto: 'Todos', valor: '')),
                const SizedBox(width: 10),
                Expanded(child: filtroBoton(texto: 'Confirmados', valor: 'confirmado')),
                const SizedBox(width: 10),
                Expanded(child: filtroBoton(texto: 'Proceso', valor: 'planificando')),
              ],
            ),
            const SizedBox(height: 24),
            Expanded(
              child: FutureBuilder<List<Map<String, dynamic>>>(
                future: eventosFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  if (snapshot.hasError) {
                    return Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Text(
                          snapshot.error.toString(),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    );
                  }

                  final lista = filtrarEventos(snapshot.data ?? []);

                  if (lista.isEmpty) {
                    return const Center(child: Text('No hay eventos'));
                  }

                  return RefreshIndicator(
                    onRefresh: recargarEventos,
                    child: ListView.builder(
                      itemCount: lista.length,
                      itemBuilder: (context, index) {
                        final evento = lista[index];
                        final estado = evento['estado']?.toString() ?? '';

                        return GestureDetector(
                          onTap: () {
                            mostrarDetalle(evento);
                          },
                          child: Container(
                            margin: const EdgeInsets.only(bottom: 18),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(24),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.04),
                                  blurRadius: 10,
                                ),
                              ],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                ClipRRect(
                                  borderRadius: const BorderRadius.vertical(
                                    top: Radius.circular(24),
                                  ),
                                  child: Image.network(
                                    evento['imagen'].toString(),
                                    height: 180,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                  ),
                                ),
                                Padding(
                                  padding: const EdgeInsets.all(18),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 6,
                                        ),
                                        decoration: BoxDecoration(
                                          color: getEstadoColor(estado).withOpacity(0.15),
                                          borderRadius: BorderRadius.circular(20),
                                        ),
                                        child: Text(
                                          getEstadoTexto(estado),
                                          style: TextStyle(
                                            color: getEstadoColor(estado),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(height: 12),
                                      Text(
                                        evento['nombre']?.toString() ?? 'Evento',
                                        style: const TextStyle(
                                          fontSize: 22,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 10),
                                      Row(
                                        children: [
                                          const Icon(
                                            Icons.location_on,
                                            size: 18,
                                            color: Colors.grey,
                                          ),
                                          const SizedBox(width: 5),
                                          Text(
                                            evento['ciudad']?.toString() ?? 'No especificada',
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      Row(
                                        children: [
                                          const Icon(
                                            Icons.calendar_month,
                                            size: 18,
                                            color: Colors.grey,
                                          ),
                                          const SizedBox(width: 5),
                                          Text(evento['fecha'].toString()),
                                        ],
                                      ),
                                      const SizedBox(height: 18),
                                      SizedBox(
                                        width: double.infinity,
                                        height: 45,
                                        child: ElevatedButton(
                                          onPressed: () {
                                            mostrarDetalle(evento);
                                          },
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: Colors.green,
                                            foregroundColor: Colors.white,
                                            shape: RoundedRectangleBorder(
                                              borderRadius: BorderRadius.circular(14),
                                            ),
                                          ),
                                          child: const Text('Ver Detalles'),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
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

  Widget filtroBoton({
    required String texto,
    required String valor,
  }) {
    final activo = filtroEstado == valor;

    return GestureDetector(
      onTap: () {
        setState(() {
          filtroEstado = valor;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: activo ? Colors.green : Colors.white,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Center(
          child: Text(
            texto,
            style: TextStyle(
              color: activo ? Colors.white : Colors.black,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}
