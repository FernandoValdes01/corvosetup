---
name: android-mobile
description: Use for Android or mobile development tasks that require running or verifying Ceretime on the local Android emulator.
---

# Android mobile

Cuando una tarea Android necesite ejecutar, probar o revisar la app, usa el atajo `ceretime-mobile`.

- Ejecuta `ceretime-mobile`. Si no está en el `PATH`, usa `@HOME@/.local/bin/ceretime-mobile`.
- Usa el emulador `Medium_Phone` que abre el atajo. Arranca con GPU mediante `-gpu host`.
- No abras Android Studio para ejecutar o revisar la app.
- No uses `expo-web`, `expo start --web`, `npm run web` ni una vista previa en navegador como sustituto del emulador Android.
- Para validar la interfaz, usa la ventana del emulador y las herramientas Android necesarias, como `adb` o `logcat`.
- Si el atajo falla, corrige la causa del fallo. No cambies a Android Studio ni a Expo Web como alternativa.

Si el usuario pide trabajar explícitamente en la versión web, esa petición tiene prioridad sobre esta regla.
