// Firebase Service Worker for handling background messages
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging.js');

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyDwjvdFz5gUoqPy3GmfSnLW_wnr01-q-kQ",
    authDomain: "demoapp-10497.firebaseapp.com",
    databaseURL: "https://demoapp-10497.firebaseio.com",
    projectId: "demoapp-10497",
    storageBucket: "demoapp-10497.firebasestorage.app",
    messagingSenderId: "600459295936",
    appId: "1:600459295936:web:d08e636375acaec2"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get messaging service
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);
    
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png'
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            if (clientList.length > 0) {
                return clientList[0].focus();
            }
            return clients.openWindow('/');
        })
    );
});
