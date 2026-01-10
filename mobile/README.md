# DMS Mobile App

React Native mobile application for Document Management System.

## Features

- 📱 Native iOS and Android apps
- 🔐 Biometric authentication (Face ID, Touch ID)
- 📴 Offline mode with sync
- 📸 Camera integration for document scanning
- 🔔 Push notifications
- 🌐 Multi-language support
- 🌙 Dark mode

## Tech Stack

- **React Native** - Cross-platform framework
- **Redux** - State management
- **React Navigation** - Navigation
- **Axios** - API client
- **AsyncStorage** - Local storage
- **React Native Push Notification** - Push notifications
- **React Native Biometrics** - Biometric auth
- **React Native Camera** - Camera integration

## Prerequisites

- Node.js 16+
- npm or yarn
- Xcode (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS dependencies)

## Installation

```bash
# Install dependencies
cd mobile
npm install

# iOS specific
cd ios && pod install && cd ..

# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## Project Structure

```
mobile/
├── src/
│   ├── components/      # Reusable components
│   ├── screens/         # App screens
│   ├── navigation/      # Navigation configuration
│   ├── store/           # Redux store
│   ├── services/        # API services
│   ├── utils/           # Utility functions
│   ├── hooks/           # Custom hooks
│   └── constants/       # Constants
├── ios/                 # iOS native code
├── android/             # Android native code
├── assets/              # Images, fonts, etc.
└── package.json         # Dependencies
```

## Screens

### Authentication
- Login
- Register
- Biometric Setup

### Main
- Dashboard
- Services List
- Service Detail
- Service Editor
- Calculator
- Search
- Settings
- Profile
- Notifications

### Features
- Create/Edit Service
- Calculate Costs
- Generate Documents
- Export Data
- Offline Sync

## API Integration

Configure API endpoint in `src/config.js`:

```javascript
export const API_BASE_URL = 'https://api.dms.example.com';
```

## Build for Production

### iOS

```bash
# Build for release
cd ios
xcodebuild -workspace DMS.xcworkspace -scheme DMS -configuration Release
```

### Android

```bash
# Generate signed APK
cd android
./gradlew assembleRelease

# Generate AAB for Play Store
./gradlew bundleRelease
```

## App Distribution

- **iOS**: Submit to App Store via App Store Connect
- **Android**: Submit to Google Play Console
- **Beta Testing**: Use TestFlight (iOS) or Firebase App Distribution

## Environment Variables

Create `.env` file:

```
API_URL=https://api.dms.example.com
API_KEY=your_api_key
SENTRY_DSN=your_sentry_dsn
```

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# E2E tests (Detox)
npm run test:e2e
```

## Troubleshooting

### iOS Build Issues

```bash
# Clean build
cd ios
rm -rf build
pod deintegrate
pod install
```

### Android Build Issues

```bash
# Clean gradle
cd android
./gradlew clean

# Clear cache
rm -rf ~/.gradle/caches
```

## Contributing

See main project CONTRIBUTING.md

## License

MIT
