from . import base
import os

class Pwa(base.Base):
    index_content = '''
<html>

<head>
  <script src="https://unpkg.com/vue@3.x"></script>
  <script src="https://cdn.jsdelivr.net/npm/vuetify@3.x/dist/vuetify.min.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/vuetify@3.x/dist/vuetify.min.css" rel="stylesheet">

  <link rel="manifest" href="manifest.json">
  <link rel="icon" type="image/png" href="">
</head>

<body>
  <div id="app">
    <v-banner v-if="deferredPrompt"
    elevation="7"
    :sticky=false
    lines="one"
  >
  <template v-slot:prepend>

    <img  height="25" width="25" :src=" '' " class="elevation-0" />

    </template>
  <template v-slot:text>
    <!-- <img width="25" height="25" :src=" 'assets/pngtree-casino-gambling-roulette-icon-simple-style-png-image_5179660.PNG' " class="elevation-7" /> -->
      Install the native mobile app.
    </template>

    <template v-slot:actions>
      <v-btn color="primary" variant="tonal" @Click="prompt" id="install">Install</v-btn>
    </template>
  </v-banner>
    <v-app>
      <v-container>
        <center>
          <h1>{{ message }}</h1>
          <br>

        </center>
      </v-container>
    </v-app>


  </div>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js', { scope: '/' });
    }
  </script>


</body>
<script>
  const { createApp } = Vue
  const { createVuetify } = Vuetify

  const vuetify = createVuetify()

  const app = createApp({
    data() {
      return {
        message: 'Welcome to Raptor!',
        deferredPrompt: '',
      }
    },
    methods: {
      prompt(){
        this.deferredPrompt.prompt()
      },
    },
    watch: {

    },
    created(){
// This variable will save the event for later use.
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevents the default mini-infobar or install dialog from appearing on mobile
  e.preventDefault();
  // Save the event because you'll need to trigger it later.
  this.deferredPrompt = e;
  // Show your customized install prompt for your PWA
  // Your own UI doesn't have to be a single element, you
  // can have buttons in different locations, or wait to prompt
  // as part of a critical journey.
  showInAppInstallPromotion();
});
    },
    mounted() {
    }
  })
  app.use(vuetify).mount('#app')
</script>

</html>
'''

    sw_content = '''
const CACHE_NAME = `app-v1`;

// Use the install event to pre-cache all initial resources.
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    cache.addAll([
      '/',
    ]);
  })());
});

self.addEventListener('fetch', event => {
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);

    // Get the resource from the cache.
    const cachedResponse = await cache.match(event.request);
    if (cachedResponse) {
      return cachedResponse;
    } else {
        try {
          // If the resource was not in the cache, try the network.
          const fetchResponse = await fetch(event.request);

          // Save the resource in the cache and return it.
          cache.put(event.request, fetchResponse.clone());
          return fetchResponse;
        } catch (e) {
          // The network failed.
        }
    }
  })());
});
'''
    
    def __init__(self, name):
        self.name = name
        manifest_content = '''
{
    "lang": "en-us",
    "name": "'''+self.name+'''",
    "short_name": "'''+self.name+'''",
    "description": "",
    "start_url": "/",
    "background_color": "#2f3d58",
    "theme_color": "#2f3d58",
    "orientation": "any",
    "display": "standalone",
    "icons": [
        {
            "src": "",
            "type": "image/png",
            "sizes": "512x512"
        }
    ]
}
'''
        self.folders = [
            f'apps/{self.name}/pwa',
            f'apps/{self.name}/pwa/dev',
            ]
        self.files = {
            f'apps/{self.name}/pwa/dev/index.html': self.index_content,
            f'apps/{self.name}/pwa/dev/manifest.js': manifest_content,
            f'apps/{self.name}/pwa/dev/sw.js': self.sw_content,
            }

    def create(self):
        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()