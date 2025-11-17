# City Guide Android

Нативный Android-клиент для CoreAgents City Guide, повторяющий сценарии веб-фронтенда: регистрация/логин, редактирование профиля, поиск мест и работа с маршрутами.

## Запуск

1. Откройте каталог `android-app` в Android Studio Hedgehog+.
2. Установите Android SDK 34 и убедитесь, что у вас включён JDK 17.
3. При необходимости обновите значение `API_BASE_URL` в `app/build.gradle.kts` (по умолчанию `http://10.0.2.2:8000/v1/` для эмулятора).
4. Соберите и запустите конфигурацию `app` на эмуляторе или устройстве.

## Архитектура

- **Jetpack Compose** — декларативный UI для всех экранов (авторизация, профиль, места, маршруты).
- **Navigation Compose** — стек навигации по ключевым разделам.
- **Retrofit + Moshi** — вызовы REST API, совместимые с бэкендом из `city_guide`.
- **ViewModel + StateFlow** — единое состояние приложения (`CityGuideState`) и простой репозиторий `CityGuideRepository` для работы с API.

Экранный набор соответствует сценариям из существующего фронтенда: Sign In/Up → Profile → Places → Routes → Route detail/Generate.
