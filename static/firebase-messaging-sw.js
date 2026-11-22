
importScripts(
  "https://www.gstatic.com/firebasejs/13.0.0/firebase-app-compat.js"
);
importScripts(
  "https://www.gstatic.com/firebasejs/13.0.0/firebase-messaging-compat.js"
);

firebase.initializeApp({
  apiKey: "AIzaSyBKkOfRwyp3tBg3LSSbraGT2cCx_iZ3vsg",
  authDomain: "student-study-planner-b64b5.firebaseapp.com",
  projectId: "student-study-planner-b64b5",
  storageBucket: "student-study-planner-b64b5.firebasestorage.app",
  messagingSenderId: "1010040759555",
  appId: "1:1010040759555:web:bf91db48451019975e7536"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  if (payload.notification) return;

  const title = payload.data?.title || "Study Planner";
  const options = {
    body: payload.data?.body || "You have a study reminder!"
  };

  self.registration.showNotification(title, options);
});
