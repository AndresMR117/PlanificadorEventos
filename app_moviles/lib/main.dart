import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
//import 'screens/home_screen.dart';
//import 'screens/registro_screen.dart';
//import 'screens/chatbot_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Flow Events',

      theme: ThemeData(
        useMaterial3: true,
      ),

      home: const LoginScreen(),
    );
  }
}
