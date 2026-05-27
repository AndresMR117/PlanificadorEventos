
import 'package:flutter/material.dart';

import '../services/api_service.dart';
import 'login_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {

  final nombreController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool obscurePassword = true;
  bool loading = false;

  double passwordStrength = 0;
  String passwordStrengthText = '';

  void togglePassword() {

    setState(() {
      obscurePassword = !obscurePassword;
    });
  }

  void checkPasswordStrength(String password) {

    int strength = 0;

    if (password.length >= 8) strength++;
    if (RegExp(r'[a-z]').hasMatch(password)) strength++;
    if (RegExp(r'[A-Z]').hasMatch(password)) strength++;
    if (RegExp(r'[0-9]').hasMatch(password)) strength++;
    if (RegExp(r'[@$!%*?&]').hasMatch(password)) strength++;

    setState(() {
      passwordStrength = strength / 5;

      switch (strength) {
        case 0:
        case 1:
          passwordStrengthText = 'Débil';
          break;

        case 2:
          passwordStrengthText = 'Regular';
          break;

        case 3:
          passwordStrengthText = 'Buena';
          break;

        case 4:
        case 5:
          passwordStrengthText = 'Fuerte';
          break;
      }
    });
  }

  Color getStrengthColor() {

    if (passwordStrength <= 0.2) {
      return Colors.red;
    }

    if (passwordStrength <= 0.4) {
      return Colors.orange;
    }

    if (passwordStrength <= 0.6) {
      return Colors.lightGreen;
    }

    return Colors.green;
  }

  void mostrarError(String mensaje) {

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: Colors.red,
        content: Text(mensaje),
      ),
    );
  }

  Future<void> registrarUsuario() async {

    final nombre = nombreController.text.trim();
    final email = emailController.text.trim();
    final password = passwordController.text;

    if (nombre.isEmpty || email.isEmpty || password.isEmpty) {
      mostrarError('Completa todos los campos');
      return;
    }

    if (nombre.length < 3) {
      mostrarError('El nombre debe tener al menos 3 caracteres');
      return;
    }

    if (!email.contains('@')) {
      mostrarError('Correo inválido');
      return;
    }

    if (password.length < 8) {
      mostrarError('La contraseña debe tener mínimo 8 caracteres');
      return;
    }

    try {
      setState(() {
        loading = true;
      });

      await ApiService.register(
        nombre: nombre,
        email: email,
        password: password,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cuenta creada correctamente'),
        ),
      );

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const LoginScreen(),
        ),
      );
    } catch (e) {
      mostrarError(e is ApiException ? e.message : 'No se pudo crear la cuenta');
    } finally {
      if (!mounted) return;

      setState(() {
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: Colors.white,

      body: SafeArea(

        child: SingleChildScrollView(

          padding: const EdgeInsets.all(24),

          child: Column(

            crossAxisAlignment: CrossAxisAlignment.start,

            children: [

              const SizedBox(height: 30),

              Center(
                child: Column(
                  children: [

                    Container(
                      width: 70,
                      height: 70,

                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(18),
                      ),

                      child: const Icon(
                        Icons.celebration,
                        color: Colors.white,
                        size: 35,
                      ),
                    ),

                    const SizedBox(height: 20),

                    const Text(
                      'Planificador IA',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    const SizedBox(height: 8),

                    const Text(
                      'Crea tu cuenta para comenzar',
                      style: TextStyle(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 45),

              const Text(
                'Nombre completo',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 10),

              TextField(
                controller: nombreController,

                decoration: InputDecoration(
                  hintText: 'Alex Sterling',

                  prefixIcon: const Icon(Icons.person),

                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              const Text(
                'Correo electrónico',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 10),

              TextField(
                controller: emailController,

                decoration: InputDecoration(
                  hintText: 'alex@gmail.com',

                  prefixIcon: const Icon(Icons.email),

                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),

              const SizedBox(height: 20),

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

                onChanged: checkPasswordStrength,

                decoration: InputDecoration(
                  hintText: 'Mínimo 8 caracteres',

                  prefixIcon: const Icon(Icons.lock),

                  suffixIcon: IconButton(
                    icon: Icon(
                      obscurePassword
                          ? Icons.visibility
                          : Icons.visibility_off,
                    ),

                    onPressed: togglePassword,
                  ),

                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              ClipRRect(
                borderRadius: BorderRadius.circular(10),

                child: LinearProgressIndicator(
                  value: passwordStrength,
                  minHeight: 6,
                  backgroundColor: Colors.grey.shade300,
                  valueColor: AlwaysStoppedAnimation(
                    getStrengthColor(),
                  ),
                ),
              ),

              const SizedBox(height: 6),

              Text(
                passwordStrengthText,
                style: TextStyle(
                  color: getStrengthColor(),
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 35),

              SizedBox(
                width: double.infinity,
                height: 55,

                child: ElevatedButton(

                  onPressed: loading
                      ? null
                      : registrarUsuario,

                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),

                  child: loading
                      ? const CircularProgressIndicator(
                          color: Colors.white,
                        )
                      : const Text(
                          'Crear Cuenta',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 25),

              Row(
                mainAxisAlignment: MainAxisAlignment.center,

                children: [

                  const Text(
                    '¿Ya tienes cuenta?',
                  ),

                  TextButton(

                    onPressed: () {

                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const LoginScreen(),
                        ),
                      );
                    },

                    child: const Text(
                      'Iniciar sesión',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

