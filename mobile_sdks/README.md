# Mobile SDKs

Mobile SDKs for integrating with the DMS (Data Management System) platform across iOS, Android, React Native, and Flutter.

## Overview

These SDKs provide native mobile access to:
- Authentication (OAuth 2.0/OpenID Connect)
- Push notifications
- Real-time BI dashboards
- Document management
- AI-powered features
- Offline support

## Supported Platforms

### iOS SDK
- **Language**: Swift 5.5+
- **Minimum iOS**: 14.0+
- **Features**: Full native iOS integration
- **Location**: `/mobile_sdks/ios/`

### Android SDK
- **Language**: Kotlin 1.9+
- **Minimum Android**: API 24+ (Android 7.0)
- **Features**: Full native Android integration
- **Location**: `/mobile_sdks/android/`

### React Native SDK
- **Language**: TypeScript
- **React Native**: 0.72+
- **Features**: Cross-platform iOS/Android support
- **Location**: `/mobile_sdks/react_native/`

### Flutter SDK
- **Language**: Dart 3.0+
- **Flutter**: 3.10+
- **Features**: Cross-platform with native performance
- **Location**: `/mobile_sdks/flutter/`

## Quick Start

### iOS (Swift)
```swift
import DMSSDK

// Initialize SDK
let sdk = DMSSDK.initialize(
    apiKey: "your_api_key",
    baseURL: "https://api.example.com"
)

// Authenticate
sdk.auth.login(email: "user@example.com", password: "password") { result in
    switch result {
    case .success(let user):
        print("Logged in: \(user.email)")
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### Android (Kotlin)
```kotlin
import com.example.dmssdk.DMSSDK

// Initialize SDK
val sdk = DMSSDK.Builder(context)
    .setApiKey("your_api_key")
    .setBaseURL("https://api.example.com")
    .build()

// Authenticate
sdk.auth.login("user@example.com", "password") { result ->
    result.onSuccess { user ->
        println("Logged in: ${user.email}")
    }.onFailure { error ->
        println("Error: $error")
    }
}
```

### React Native (TypeScript)
```typescript
import { DMSSDK } from '@dms/react-native-sdk';

// Initialize SDK
const sdk = DMSSDK.initialize({
  apiKey: 'your_api_key',
  baseURL: 'https://api.example.com',
});

// Authenticate
const result = await sdk.auth.login({
  email: 'user@example.com',
  password: 'password',
});

console.log('Logged in:', result.user.email);
```

### Flutter (Dart)
```dart
import 'package:dms_sdk/dms_sdk.dart';

// Initialize SDK
final sdk = await DMSdk.initialize(
  apiKey: 'your_api_key',
  baseURL: 'https://api.example.com',
);

// Authenticate
final user = await sdk.auth.login(
  email: 'user@example.com',
  password: 'password',
);

print('Logged in: ${user.email}');
```

## Core Features

### Authentication
- OAuth 2.0 / OpenID Connect integration
- Biometric authentication (Face ID, Touch ID, Fingerprint)
- Secure token storage
- Automatic token refresh

### Push Notifications
- Firebase Cloud Messaging (FCM) integration
- Apple Push Notification Service (APNs) integration
- Custom notification handlers
- Rich notifications with actions

### Real-time Data
- WebSocket connections for live updates
- Real-time BI dashboard synchronization
- Offline-first architecture
- Conflict resolution

### Document Management
- Upload/download documents
- Image/file compression
- OCR text extraction
- PDF generation

### AI Features
- Document summarization
- Entity extraction
- Sentiment analysis
- Q&A on documents

## Installation

### iOS (CocoaPods)
```ruby
# Podfile
pod 'DMSSDK', '~> 2.6.0'
```

### Android (Gradle)
```groovy
// build.gradle
dependencies {
    implementation 'com.example:dms-sdk:2.6.0'
}
```

### React Native (npm)
```bash
npm install @dms/react-native-sdk@2.6.0
# or
yarn add @dms/react-native-sdk@2.6.0
```

### Flutter (pubspec.yaml)
```yaml
dependencies:
  dms_sdk: ^2.6.0
```

## Architecture

All SDKs follow a consistent architecture:

```
SDK
├── Auth Module          # Authentication & authorization
├── Push Module          # Push notifications
├── Data Module          # Data sync & storage
├── Document Module      # Document management
├── AI Module            # AI-powered features
├── Analytics Module     # Usage analytics
└── Networking Layer     # HTTP/WebSocket clients
```

## Configuration

### Environment Configuration
```json
{
  "development": {
    "apiURL": "https://dev-api.example.com",
    "wsURL": "wss://dev-api.example.com/ws",
    "logLevel": "debug"
  },
  "production": {
    "apiURL": "https://api.example.com",
    "wsURL": "wss://api.example.com/ws",
    "logLevel": "error"
  }
}
```

## Testing

Each SDK includes comprehensive test suites:
- Unit tests
- Integration tests
- UI tests
- Performance tests

## Documentation

Detailed documentation for each platform:
- [iOS SDK Documentation](./ios/README.md)
- [Android SDK Documentation](./android/README.md)
- [React Native SDK Documentation](./react_native/README.md)
- [Flutter SDK Documentation](./flutter/README.md)

## Examples

Sample applications for each platform:
- iOS: `/mobile_sdks/ios/Example/`
- Android: `/mobile_sdks/android/example/`
- React Native: `/mobile_sdks/react_native/example/`
- Flutter: `/mobile_sdks/flutter/example/`

## Support

- **API Documentation**: https://docs.example.com
- **Issues**: https://github.com/example/dms-mobile-sdks/issues
- **Discussions**: https://github.com/example/dms-mobile-sdks/discussions

## License

Copyright (c) 2025 DMS Platform
See LICENSE file for details.

## Changelog

### v2.6.0 (2025-01-14)
- Initial mobile SDK structure
- iOS SDK foundation
- Android SDK foundation
- React Native SDK foundation
- Flutter SDK foundation
- OAuth 2.0 authentication
- Push notification support
- Real-time BI integration
