import os

from kivy.core.audio import SoundLoader
from kivy.utils import platform

SOUND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds'))
SOUND_NAMES = ('sprint_done', 'break_done', 'session_done')

CHANNEL_ID = 'sprintrunner_alerts'
NOTIFICATION_ID = 1


class Alerts:
    """Chimes and Android notifications for finished blocks and sessions."""

    def __init__(self):
        # Load once and keep the references: a Sound that is only held in a
        # local variable can be garbage-collected while it is still playing.
        self.sounds = {}
        for name in SOUND_NAMES:
            sound = SoundLoader.load(os.path.join(SOUND_DIR, name + '.wav'))
            if sound:
                sound.volume = 0.9
                self.sounds[name] = sound
        self._channel_ready = False

    def play(self, name):
        sound = self.sounds.get(name)
        if not sound:
            print(f"Sound not available: {name}")
            return
        sound.stop()  # restart cleanly if the previous chime is still ringing
        sound.play()

    # -- Android notifications

    def request_permission(self):
        """Android 13+ asks the user before an app may show notifications."""
        if platform != 'android':
            return
        try:
            from android.permissions import request_permissions
            request_permissions(['android.permission.POST_NOTIFICATIONS'])
        except Exception as e:
            print(f"Notification permission request failed: {e}")

    def notify(self, title, text):
        if platform != 'android':
            return
        try:
            from android import mActivity
            from jnius import autoclass, cast
            Context = autoclass('android.content.Context')
            Builder = autoclass('android.app.Notification$Builder')
            PendingIntent = autoclass('android.app.PendingIntent')
            JString = autoclass('java.lang.String')

            context = mActivity.getApplicationContext()
            manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
            self._ensure_channel(manager)

            # Tapping the notification brings the app back
            intent = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName())
            FLAG_IMMUTABLE = 0x04000000
            content = PendingIntent.getActivity(context, 0, intent, FLAG_IMMUTABLE)

            builder = Builder(context, CHANNEL_ID)
            builder.setSmallIcon(context.getApplicationInfo().icon)
            builder.setContentTitle(cast('java.lang.CharSequence', JString(title)))
            builder.setContentText(cast('java.lang.CharSequence', JString(text)))
            builder.setContentIntent(content)
            builder.setAutoCancel(True)
            manager.notify(NOTIFICATION_ID, builder.build())
        except Exception as e:
            print(f"Notification failed: {e}")

    def _ensure_channel(self, manager):
        if self._channel_ready:
            return
        from jnius import autoclass, cast
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationManager = autoclass('android.app.NotificationManager')
        JString = autoclass('java.lang.String')
        channel = NotificationChannel(CHANNEL_ID, cast('java.lang.CharSequence', JString('Sprint alerts')),
                                      NotificationManager.IMPORTANCE_HIGH)
        channel.setDescription('When a sprint, break or session finishes')
        channel.setSound(None, None)  # the app plays its own chime
        manager.createNotificationChannel(channel)
        self._channel_ready = True
