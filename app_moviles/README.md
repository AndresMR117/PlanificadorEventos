# app_moviles

A new Flutter project.

## Conexion con backend en Railway

La app no debe conectarse directamente a MySQL desde Flutter, porque las
credenciales quedarian expuestas dentro de la aplicacion. El login debe llamar a
un backend desplegado en Railway, y ese backend es el que valida contra MySQL.

Por defecto la app usa `http://10.0.2.2:8000/api`, que sirve para probar un
backend local desde el emulador de Android. Para usar tu backend en Railway:

```bash
flutter run --dart-define=API_BASE_URL=https://tu-backend.up.railway.app/api
```

El backend debe exponer estos endpoints:

- `POST /api/login` con JSON: `{"email":"...", "password":"..."}`
- `POST /api/register` con JSON: `{"nombre":"...", "email":"...", "password":"..."}`

Ambos endpoints deben responder JSON. En errores, envia una propiedad `message`,
`error` o `mensaje` para mostrarla en la app.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
