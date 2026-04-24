// Import Firebase scripts for service worker
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Firebase configuration - using the same config as the main app
const firebaseConfig = {
  apiKey: "AIzaSyCqnawpoonrBLrnNF7Fjxy_EkgmaM4NmRo",
  authDomain: "fir-demo-1611e.firebaseapp.com",
  projectId: "fir-demo-1611e",
  storageBucket: "fir-demo-1611e.firebasestorage.app",
  messagingSenderId: "72259872098",
  appId: "1:72259872098:web:b227b743a85b4fbce4383b"
};

// Initialize Firebase in service worker
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message:', payload);
  
  const notificationTitle = payload.notification?.title || 'IBS Wellness Companion';
  const notificationOptions = {
    body: payload.notification?.body || 'You have a new notification',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    tag: 'ibs-wellness-notification',
    data: payload.data,
    actions: [
      {
        action: 'open',
        title: 'Open App'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click events
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification click received.');

  event.notification.close();

  if (event.action === 'dismiss') {
    return;
  }

  // Open the app when notification is clicked
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if app is already open
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If app is not open, open it
      if (clients.openWindow) {
        return clients.openWindow('/dashboard');
      }
    })
  );
});

// Handle push events (fallback)
self.addEventListener('push', (event) => {
  if (event.data) {
    const payload = event.data.json();
    console.log('[firebase-messaging-sw.js] Push event received:', payload);
    
    const notificationTitle = payload.notification?.title || 'IBS Wellness Companion';
    const notificationOptions = {
      body: payload.notification?.body || 'You have a new notification',
      icon: '/icon-192x192.png',
      badge: '/icon-192x192.png',
      tag: 'ibs-wellness-notification',
      data: payload.data
    };

    event.waitUntil(
      self.registration.showNotification(notificationTitle, notificationOptions)
    );
  }
});