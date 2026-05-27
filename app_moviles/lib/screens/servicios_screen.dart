import 'package:flutter/material.dart';

class ServiciosScreen extends StatefulWidget {
  const ServiciosScreen({super.key});

  @override
  State<ServiciosScreen> createState() => _ServiciosScreenState();
}

class _ServiciosScreenState extends State<ServiciosScreen> {

  final List<String> tiposEvento = [
    'Boda',
    'Cumpleaños',
    'Graduación',
    'Quinceañera',
    'Corporativo',
  ];

  String? tipoSeleccionado;

  final List<Map<String, dynamic>> todosServicios = [
    {
      'nombre': 'Decoración Premium',
      'categoria': 'Boda',
      'precio': '\$2.500.000',
      'icono': Icons.celebration,
    },
    {
      'nombre': 'DJ Profesional',
      'categoria': 'Cumpleaños',
      'precio': '\$800.000',
      'icono': Icons.music_note,
    },
    {
      'nombre': 'Fotografía Profesional',
      'categoria': 'Graduación',
      'precio': '\$1.200.000',
      'icono': Icons.camera_alt,
    },
    {
      'nombre': 'Catering Ejecutivo',
      'categoria': 'Corporativo',
      'precio': '\$3.000.000',
      'icono': Icons.restaurant,
    },
    {
      'nombre': 'Show en Vivo',
      'categoria': 'Quinceañera',
      'precio': '\$1.500.000',
      'icono': Icons.mic,
    },
  ];

  List<Map<String, dynamic>> serviciosFiltrados = [];

  void cargarServiciosPorTipo() {

    if (tipoSeleccionado == null) {
      setState(() {
        serviciosFiltrados = [];
      });
      return;
    }

    final filtrados = todosServicios.where((servicio) {
      return servicio['categoria'] == tipoSeleccionado;
    }).toList();

    setState(() {
      serviciosFiltrados = filtrados;
    });
  }

  @override
  void initState() {
    super.initState();
    serviciosFiltrados = [];
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: const Color(0xffF5F7FA),

      appBar: AppBar(
        title: const Text(
          'Servicios',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
      ),

      body: Padding(
        padding: const EdgeInsets.all(20),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [

            const Text(
              '📋 Servicios por Tipo de Evento',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 25),

            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
              ),

              child: DropdownButtonHideUnderline(

                child: DropdownButton<String>(

                  value: tipoSeleccionado,
                  isExpanded: true,

                  hint: const Text(
                    'Selecciona un tipo de evento',
                  ),

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

              child: ElevatedButton(

                onPressed: cargarServiciosPorTipo,

                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),

                child: const Text(
                  'Buscar',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 25),

            Expanded(

              child: serviciosFiltrados.isEmpty

                  ? const Center(
                      child: Text(
                        'No hay servicios para mostrar',
                        style: TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                    )

                  : GridView.builder(

                      itemCount: serviciosFiltrados.length,

                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 16,
                        mainAxisSpacing: 16,
                        childAspectRatio: 0.9,
                      ),

                      itemBuilder: (context, index) {

                        final servicio = serviciosFiltrados[index];

                        return Container(

                          padding: const EdgeInsets.all(16),

                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20),
                          ),

                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,

                            children: [

                              CircleAvatar(
                                radius: 30,
                                backgroundColor:
                                    Colors.blue.withOpacity(0.1),

                                child: Icon(
                                  servicio['icono'],
                                  color: Colors.blue,
                                  size: 30,
                                ),
                              ),

                              const SizedBox(height: 16),

                              Text(
                                servicio['nombre'],
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),

                              const SizedBox(height: 10),

                              Text(
                                servicio['precio'],
                                style: const TextStyle(
                                  color: Colors.grey,
                                ),
                              ),

                              const SizedBox(height: 14),

                              SizedBox(
                                width: double.infinity,

                                child: ElevatedButton(

                                  onPressed: () {},

                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.blue,
                                    shape: RoundedRectangleBorder(
                                      borderRadius:
                                          BorderRadius.circular(12),
                                    ),
                                  ),

                                  child: const Text(
                                    'Ver',
                                    style: TextStyle(
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
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