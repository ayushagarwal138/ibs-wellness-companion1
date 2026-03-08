import { initializeApp, getApps } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getMessaging, getToken, onMessage, isSupported } from 'firebase/messaging';
import { getAnalytics, isSupported as isAnalyticsSupported } from 'firebase/analytics';

// Firebase configuration using environment variables
const firebaseConfig = {
  apiKey: process.env['NEXT_PUBLIC_FIREBASE_API_KEY'],
  authDomain: process.env['NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN'],
  projectId: process.env['NEXT_PUBLIC_FIREBASE_PROJECT_ID'],
  storageBucket: process.env['NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET'],
  messagingSenderId: process.env['NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID'],
  appId: process.env['NEXT_PUBLIC_FIREBASE_APP_ID'],
};

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// Initialize Firebase Auth
export const auth = getAuth(app);

// Connect to Auth emulator in development (disabled for now)
// Uncomment the following lines if you want to use Firebase Auth emulator
// if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
//   // Only connect to emulator if not already connected
//   try {
//     connectAuthEmulator(auth, 'http://localhost:9099', { disableWarnings: true });
//   } catch (error) {
//     console.log('Auth emulator connection failed:', error);
//   }
// }

// Initialize Firebase Cloud Messaging
let messaging: any = null;
if (typeof window !== 'undefined') {
  isSupported().then((supported) => {
    if (supported) {
      messaging = getMessaging(app);
    }
  });
}

// Initialize Firebase Analytics
let analytics: any = null;
if (typeof window !== 'undefined') {
  isAnalyticsSupported().then((supported) => {
    if (supported && process.env['NEXT_PUBLIC_GA_MEASUREMENT_ID']) {
      analytics = getAnalytics(app);
    }
  });
}

// Request notification permission and get FCM token
export const requestNotificationPermission = async (): Promise<string | null> => {
  if (!messaging) {
    console.log('Messaging not supported');
    return null;
  }

  try {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('Notification permission granted.');
      
      // Get FCM token
      const token = await getToken(messaging, {
        vapidKey: process.env['NEXT_PUBLIC_FIREBASE_VAPID_KEY'],
      });
      
      if (token) {
        console.log('FCM Token:', token);
        return token;
      } else {
        console.log('No registration token available.');
        return null;
      }
    } else {
      console.log('Unable to get permission to notify.');
      return null;
    }
  } catch (error) {
    console.error('An error occurred while retrieving token:', error);
    return null;
  }
};

// Listen for foreground messages
export const onMessageListener = () =>
  new Promise((resolve) => {
    if (!messaging) {
      resolve(null);
      return;
    }
    
    onMessage(messaging, (payload) => {
      console.log('Message received in foreground:', payload);
      resolve(payload);
    });
  });

// Export Firebase services
export { app, messaging, analytics };
export default app;