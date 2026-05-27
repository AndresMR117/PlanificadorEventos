import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F8F6),

      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [

              // NAVBAR
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 16,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [

                    // LOGO
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
                          "Flow Events",
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),

                    ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2ECC71),
                        foregroundColor: Colors.white,
                      ),
                      child: const Text("Crear Evento"),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // HERO SECTION
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [

                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD4F5E2),
                        borderRadius: BorderRadius.circular(30),
                      ),
                      child: const Text(
                        "✨ Inteligencia Artificial",
                        style: TextStyle(
                          color: Color(0xFF1A9E52),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),

                    const SizedBox(height: 24),

                    const Text(
                      "Crea momentos\ninolvidables",
                      style: TextStyle(
                        fontSize: 42,
                        fontWeight: FontWeight.bold,
                        height: 1.1,
                      ),
                    ),

                    const SizedBox(height: 20),

                    const Text(
                      "La IA que entiende tu visión para cada celebración.",
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.black54,
                        height: 1.5,
                      ),
                    ),

                    const SizedBox(height: 30),

                    Row(
                      children: [

                        ElevatedButton(
                          onPressed: () {},
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2ECC71),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 16,
                            ),
                          ),
                          child: const Text("Comenzar"),
                        ),

                        const SizedBox(width: 16),

                        OutlinedButton(
                          onPressed: () {},
                          child: const Text("Ver Galería"),
                        ),
                      ],
                    ),

                    const SizedBox(height: 40),

                    // IMAGEN
                    ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: Image.network(
                        "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&q=80",
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 50),

              // STATS
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [

                    Column(
                      children: [
                        Text(
                          "10k+",
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2ECC71),
                          ),
                        ),
                        SizedBox(height: 6),
                        Text("Eventos"),
                      ],
                    ),

                    Column(
                      children: [
                        Text(
                          "500+",
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2ECC71),
                          ),
                        ),
                        SizedBox(height: 6),
                        Text("Proveedores"),
                      ],
                    ),

                    Column(
                      children: [
                        Text(
                          "98%",
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2ECC71),
                          ),
                        ),
                        SizedBox(height: 6),
                        Text("Satisfacción"),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 60),
            ],
          ),
        ),
      ),
    );
  }
}