from . import base
import os

class Pwa(base.Base):
    index_content = '''

<!DOCTYPE html>
<html>
<head>
  <title>Raptor App</title>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/danfojs@1.1.2/lib/bundle.min.js"></script>
  <script src="https://code.highcharts.com/highcharts.js"></script>
  <script src="https://code.highcharts.com/modules/boost.js"></script>
  <script src="https://code.highcharts.com/modules/exporting.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, minimal-ui">
  <link rel="icon" type="image/png" href="">
  <!-- <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='50' height='50' viewBox='0 0 400.000000 400.000000'%3E%3Cg transform='translate(0.000000,400.000000) scale(0.100000,-0.100000)' fill='%23000000' stroke='none'%3E%3Cpath d='M1835 3894 c-794 -81 -1441 -618 -1659 -1381 -64 -223 -86 -518 -57 -756 68 -549 381 -1047 856 -1360 155 -102 377 -199 562 -246 188 -48 479 -70 653 -51 589 64 1095 379 1422 886 47 72 145 276 178 369 180 511 133 1099 -127 1563 -94 167 -179 278 -323 422 -168 169 -303 267 -505 366 -277 135 -479 184 -775 189 -102 2 -203 1 -225 -1z m383 -284 c340 -41 662 -195 916 -440 248 -239 400 -515 469 -854 19 -95 22 -142 22 -321 -1 -179 -4 -225 -23 -313 -91 -416 -306 -754 -640 -1002 -210 -157 -439 -252 -722 -301 -117 -21 -414 -18 -535 5 -586 109 -1073 531 -1254 1086 -62 188 -75 274 -75 500 -1 226 15 340 76 524 29 89 127 297 154 327 8 8 14 18 14 22 0 11 87 130 124 171 20 21 36 40 36 43 0 9 114 122 135 133 13 7 22 17 19 22 -3 4 1 8 9 8 7 0 26 14 43 31 16 17 58 49 94 72 36 23 75 48 85 55 24 15 224 112 231 112 4 0 20 6 37 13 61 26 102 39 144 46 23 4 48 12 55 18 11 9 79 20 288 46 62 8 217 6 298 -3z'/%3E%3Cpath d='M950 2910 c0 -12 8 -21 23 -24 12 -3 34 -7 49 -10 15 -4 39 -17 54 -29 36 -31 40 -82 25 -314 -6 -98 -22 -362 -36 -588 -28 -465 -30 -484 -55 -542 -22 -50 -58 -71 -138 -81 -48 -6 -57 -10 -57 -27 0 -19 8 -20 273 -23 l272 -2 0 23 c0 21 -7 25 -61 35 -70 13 -120 46 -139 92 -14 33 -15 12 35 820 14 223 25 413 25 423 0 38 23 13 59 -65 21 -46 114 -240 206 -433 92 -192 184 -386 205 -430 139 -296 221 -456 236 -462 39 -15 13 -66 419 807 106 228 214 459 239 514 26 54 49 96 52 93 10 -10 87 -1203 80 -1242 -12 -64 -79 -109 -181 -121 -50 -6 -56 -9 -53 -28 3 -21 5 -21 338 -21 333 0 335 0 338 21 3 20 -3 22 -68 26 -126 9 -142 36 -160 266 -27 350 -80 1133 -80 1188 0 73 14 90 80 99 82 11 90 14 90 35 0 20 -6 20 -195 18 l-195 -3 -81 -170 c-44 -93 -99 -208 -121 -255 -22 -47 -100 -211 -173 -365 -73 -154 -160 -337 -193 -407 -34 -71 -65 -128 -70 -128 -5 0 -38 62 -75 138 -36 75 -96 200 -132 277 -37 77 -87 181 -110 230 -23 50 -61 128 -83 175 -22 47 -86 180 -140 295 l-100 210 -201 3 c-195 2 -201 2 -201 -18z'/%3E%3C/g%3E%3C/svg%3E" type="image/svg+xml"> -->
  <link rel="manifest" href="manifest.json">
</head>

<body>
  <style>
    [v-cloak] {display: none};
</style>

<div id="app">
  <div v-if="pwa_install" role="alert" class="alert shadow-lg">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    <span>Install Raptor. on your device!</span>
    <div>
      <button class=" btn btn-sm black-text-shadow-sm btn-primary text-white  shadow-lg  hover:bg-primary shadow-blue-500/50 hover:shadow-xl hover:shadow-blue-500/50 hover:-translate-y-0.5 no-animation black-text-shadow" @Click="prompt"  id="install" >Install</button>
    </div>
  </div>
</div>

<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js', { scope: '/' });
  }
</script>
<script>
  // Disable right-clicking
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
});
</script>

</body>
<script>
  const { createApp } = Vue

  createApp({
    delimiters: ["[[","]]"],
    data() {
      return {
        pwa_install: '',
      }
    },
    created(){
        // This variable will save the event for later use.
        window.addEventListener('beforeinstallprompt', (e) => {
          // Prevents the default mini-infobar or install dialog from appearing on mobile
        //   e.preventDefault();
          // Save the event because you'll need to trigger it later.
          this.pwa_install = e;
          // Show your customized install prompt for your PWA
          // Your own UI doesn't have to be a single element, you
          // can have buttons in different locations, or wait to prompt
          // as part of a critical journey.
          showInAppInstallPromotion();
        });
        console.log('pwa_install = ' + this.pwa_install)
    },

    methods:{
      prompt(){
        this.pwa_install.prompt()
      },

    }
  }).mount('#app')
</script>




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