import 'package:flutter/material.dart';

import '../services/api_service.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool loading = false;
  bool obscurePassword = true;

  Future<void> iniciarSesion() async {

    final email = emailController.text.trim();
    final password = passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      mostrarError('Completa todos los campos');
      return;
    }

    try {

      setState(() {
        loading = true;
      });

      final response = await ApiService.login(
        email,
        password,
      );

      print(response);

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const HomeScreen(),
        ),
      );

    } catch (e) {

      mostrarError(
        'Correo o contraseña incorrectos',
      );

    } finally {

      setState(() {
        loading = false;
      });
    }
  }

  void mostrarError(String mensaje) {

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: Colors.red,
        content: Text(mensaje),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: Colors.white,

      body: SafeArea(

        child: SingleChildScrollView(

          child: Column(

            children: [

              // IMAGEN SUPERIOR
              SizedBox(
                height: 320,
                width: double.infinity,

                child: Stack(

                  fit: StackFit.expand,

                  children: [

                    Image.network(
                      'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1200&q=80',
                      fit: BoxFit.cover,
                    ),

                    Container(
                      color: Colors.black.withOpacity(0.35),
                    ),

                    const Positioned(

                      bottom: 30,
                      left: 24,
                      right: 24,

                      child: Column(
                        crossAxisAlignment:
                            CrossAxisAlignment.start,

                        children: [

                          Text(
                            'Flow Events',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 34,
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          SizedBox(height: 10),

                          Text(
                            'Gestión inteligente de eventos para celebraciones inolvidables.',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 15,
                              height: 1.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              Padding(
                padding: const EdgeInsets.all(24),

                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,

                  children: [

                    // TITULO
                    const Text(
                      'Bienvenido',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    const SizedBox(height: 8),

                    const Text(
                      'Inicia sesión para continuar',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 16,
                      ),
                    ),

                    const SizedBox(height: 40),

                    // EMAIL
                    const Text(
                      'Correo Electrónico',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                      ),
                    ),

                    const SizedBox(height: 10),

                    TextField(
                      controller: emailController,

                      decoration: InputDecoration(

                        hintText: 'alex@gmail.com',

                        prefixIcon: const Icon(
                          Icons.email_outlined,
                        ),

                        filled: true,
                        fillColor: Colors.grey.shade100,

                        border: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(14),
                          borderSide: BorderSide.none,
                        ),

                        focusedBorder: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(14),

                          borderSide: const BorderSide(
                            color: Color(0xFF2ECC71),
                            width: 2,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // PASSWORD
                    const Text(
                      'Contraseña',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                      ),
                    ),

                    const SizedBox(height: 10),

                    TextField(

                      controller: passwordController,
                      obscureText: obscurePassword,

                      decoration: InputDecoration(

                        hintText: '••••••••',

                        prefixIcon: const Icon(
                          Icons.lock_outline,
                        ),

                        suffixIcon: IconButton(

                          icon: Icon(
                            obscurePassword
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),

                          onPressed: () {

                            setState(() {

                              obscurePassword =
                                  !obscurePassword;
                            });
                          },
                        ),

                        filled: true,
                        fillColor: Colors.grey.shade100,

                        border: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(14),
                          borderSide: BorderSide.none,
                        ),

                        focusedBorder: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(14),

                          borderSide: const BorderSide(
                            color: Color(0xFF2ECC71),
                            width: 2,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 18),

                    Row(
                      mainAxisAlignment:
                          MainAxisAlignment.spaceBetween,

                      children: [

                        Row(
                          children: [

                            Checkbox(
                              value: true,
                              onChanged: (_) {},
                              activeColor:
                                  const Color(0xFF2ECC71),
                            ),

                            const Text(
                              'Recordarme',
                            ),
                          ],
                        ),

                        TextButton(
                          onPressed: () {},

                          child: const Text(
                            '¿Olvidaste tu contraseña?',
                            style: TextStyle(
                              color: Color(0xFF2ECC71),
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    // BOTON LOGIN
                    SizedBox(

                      width: double.infinity,
                      height: 56,

                      child: ElevatedButton(

                        onPressed: loading
                            ? null
                            : iniciarSesion,

                        style: ElevatedButton.styleFrom(
                          backgroundColor:
                              const Color(0xFF1E293B),

                          foregroundColor: Colors.white,

                          shape: RoundedRectangleBorder(
                            borderRadius:
                                BorderRadius.circular(16),
                          ),
                        ),

                        child: loading

                            ? const SizedBox(
                                width: 24,
                                height: 24,

                                child:
                                    CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 2,
                                ),
                              )

                            : const Text(
                                'Iniciar Sesión',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                      ),
                    ),

                    const SizedBox(height: 30),

                    // SEPARADOR
                    Row(
                      children: [

                        Expanded(
                          child: Divider(
                            color: Colors.grey.shade300,
                          ),
                        ),

                        Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                          ),

                          child: Text(
                            'o continuar con',
                            style: TextStyle(
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ),

                        Expanded(
                          child: Divider(
                            color: Colors.grey.shade300,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // BOTONES SOCIALES
                    Row(

                      children: [

                        Expanded(
                          child: OutlinedButton.icon(

                            onPressed: () {},

                            icon: const Icon(
                              Icons.g_mobiledata,
                              size: 30,
                            ),

                            label: const Text('Google'),

                            style: OutlinedButton.styleFrom(
                              padding:
                                  const EdgeInsets.symmetric(
                                vertical: 14,
                              ),

                              shape: RoundedRectangleBorder(
                                borderRadius:
                                    BorderRadius.circular(14),
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(width: 14),

                        Expanded(
                          child: OutlinedButton.icon(

                            onPressed: () {},

                            icon: const Icon(Icons.business),

                            label: const Text('LinkedIn'),

                            style: OutlinedButton.styleFrom(
                              padding:
                                  const EdgeInsets.symmetric(
                                vertical: 14,
                              ),

                              shape: RoundedRectangleBorder(
                                borderRadius:
                                    BorderRadius.circular(14),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 30),

                    Center(
                      child: Text(
                        'Al continuar aceptas nuestros términos y privacidad.',
                        textAlign: TextAlign.center,

                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}