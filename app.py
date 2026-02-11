from flask import Flask, render_template_string,request, Response
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import html
from datetime import datetime
import threading
import time

app = Flask(__name__)

# サービスの状態を保存
service_status = {}

# 監視するサービスのリスト
SERVICES = [
    {
        'url': 'https://keitagames.com',
        'name': 'ポートフォリオ'
    },
    {
        'url': 'https://keitagames.com/midi-okiba',
        'name': 'midi置き場'
    },
    {
        'url': 'https://keitagames.com/midi',
        'name': 'midiプレイヤー'
    },
    {
        'url': 'https://keitagames.com/FAMICOMU',
        'name': 'ファミコンエミュレータgithub'
    },
    {
        'url': 'https://nes.keitagames.com',
        'name': 'ファミコンエミュレータ'
    },
    {
        'url': 'https://taiko.keitagames.com',
        'name': 'frankey'
    },
     {
        'url': 'https://keitagames.com/frasite',
        'name': '初代フランクなホームページ'
    },
    {
        'url': 'https://wiki-g0g9.onrender.com',
        'name': 'frawiki'
    },
      {
        'url': 'https://moecounter-gms6.onrender.com',
        'name': 'moecounter'
    },
    {
        'url': 'https://postr-d8u0.onrender.com',
        'name': '掲示板Postr'
    },
    {
        'url': 'https://shinya-bbs.onrender.com',
        'name': '深夜テンションの掲示板'
    },
    {
        'url': 'https://code.keitagames.com',
        'name': '開発環境'
    },
    {
        'url': 'https://keita-status.onrender.com/',
        'name': '自ら'
    },
    {
        'url': 'https://atlas-1fck.onrender.com',
        'name': '検索エンジン'
    },
    {
        'url': 'https://taiko-j9b7.onrender.com/',
        'name': '太鼓web'
    },
    {
        'url': 'https://catblog-5so7.onrender.com',
        'name': 'ブログ兼wiki'
    },
    {
        'url': 'https://atlas-news.onrender.com',
        'name': '地震速報'
    },
    {
        'url': 'https://frank-community.github.io',
        'name': 'フランクのサイト'
    }
]

def check_service(service):
    """サービスの状態をチェック"""
    try:
        start = time.time()
        response = requests.get(service['url'], timeout=10, allow_redirects=False)
        elapsed = round((time.time() - start) * 1000, 2)  # ms

        return {
            'status_code': response.status_code,
            'reason': response.reason,  # ← OK や Not Found
            'elapsed': elapsed,
            'headers': dict(response.headers),
            'redirect': response.headers.get('Location'),
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except requests.exceptions.RequestException as e:
        return {
            'status_code': 'Error',
            'reason': '',
            'elapsed': None,
            'redirect': None,
            'error': str(e),
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def get_status_class(status_code):
    """ステータスコードに応じたCSSクラスを返す"""
    if isinstance(status_code, str):
        return 'e'
    elif 200 <= status_code < 300:
        return 'ok'
    elif 300 <= status_code < 400:
        return 'r'
    elif 400 <= status_code < 500:
        return 'n'
    else:
        return 'e'

def get_status_display(status_code):
    """ステータスコードの表示形式を返す"""
    if isinstance(status_code, str):
        return status_code
    elif 200 <= status_code < 300:
        return str(status_code)
    elif 300 <= status_code < 400:
        return '3xx'
    elif 400 <= status_code < 500:
        return '4xx'
    else:
        return '5xx'

def monitor_services():
    """バックグラウンドでサービスを監視"""
    while True:
        for service in SERVICES:
            status = check_service(service)
            service_status[service['url']] = status
        time.sleep(60)  # 60秒ごとにチェック

# HTMLテンプレート
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Service Monitor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60">

<style>
body{
text-align:center;
background:white;
font-family:sans-serif;
}
h1{
font-weight:400;
text-align:center;
}
table {
font-size:8px;
margin: 0 auto;
  border: 1px solid #000;
}

table th {
  padding:5px;
  border: 1px solid #000;
}

table td {
  padding:5px;
  border: 1px solid #000;
}
.ok{
color:rgb(0, 183, 0);
}
.n{
color:rgb(0, 0, 0);
}
.r{
color:rgb(255, 128, 0);
}
.e{
  color:rgb(255, 12, 12);
}
.timestamp {
  font-size: 0.8em;
  color: #666;
  margin-top: 20px;
}
</style>
</head>

<body>
<h1>Keita's System Status</h1>
<P>このサイトは、私のサービスの監視を目的とする</P>
<table>
  <tbody>
    {% for service in services %}
    <tr>
      <td><a href="{{ service.url }}" target="_blank">{{ service.url }}</a></td>
      <td>{{ service.name }}</td>

      <td>
        <div class="{{ service.status_class }}">
          {{ service.status_display }}
        </div>
      </td>

      <td>
        {% if service.elapsed %}
          {{ service.elapsed }} ms
        {% else %}
          -
        {% endif %}
      </td>

      <td>{{ service.last_check }}</td>

      <td>
        {% if service.redirect %}
          Redirect → {{ service.redirect }}
        {% endif %}
        {% if service.error %}
          Error: {{ service.error }}
        {% endif %}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
<div class="timestamp">最終更新: {{ last_update }}</div>
</body>
</html>'''

@app.route('/')
def index():
    services_data = []

    for service in SERVICES:
        status = service_status.get(service['url'], {
            'status_code': 'Pending',
            'last_check': 'N/A'
        })

        status_code = status['status_code']

        # ステータス全文表示
        if isinstance(status_code, int):
            full_status = f"{status_code} {status.get('reason','')}"
        else:
            full_status = status_code

        services_data.append({
            'url': service['url'],
            'name': service['name'],
            'status_class': get_status_class(status_code),
            'status_display': full_status,
            'elapsed': status.get('elapsed'),
            'last_check': status.get('last_check'),
            'error': status.get('error'),
            'redirect': status.get('redirect')
        })

    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template_string(
        HTML_TEMPLATE,
        services=services_data,
        last_update=last_update
    )
@app.route('/svg')
def svg_status():
    url = request.args.get('url')

    if not url:
        return Response("URL parameter is required", status=400)

    # URLをチェック
    service = {"url": url}
    status = check_service(service)
    status_code = status['status_code']

    if isinstance(status_code, int):
        text = f"{status_code} {status.get('reason','')}"
    else:
        text = str(status_code)

    # 色決定
    if isinstance(status_code, int) and 200 <= status_code < 300:
        color = "#00b700"
    elif isinstance(status_code, int) and 300 <= status_code < 400:
        color = "#ff8000"
    else:
        color = "#ff0c0c"

    text = html.escape(text)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="40">
<rect width="220" height="40" fill="white" stroke="black"/>
<text x="10" y="25" font-family="monospace" font-size="16" fill="{color}">
{text}
</text>
</svg>'''

    return Response(svg, mimetype='image/svg+xml')
@app.route('/png')
def png_status():
    url = request.args.get('url')

    if not url:
        return Response("URL parameter is required", status=400)

    service = {"url": url}
    status = check_service(service)
    status_code = status['status_code']

    if isinstance(status_code, int):
        text = f"{status_code} {status.get('reason','')}"
    else:
        text = str(status_code)

    # 色決定
    if isinstance(status_code, int) and 200 <= status_code < 300:
        color = (0, 183, 0)
    elif isinstance(status_code, int) and 300 <= status_code < 400:
        color = (255, 128, 0)
    else:
        color = (255, 12, 12)

    # 画像生成
    width = 300
    height = 50
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((10, 15), text, fill=color, font=font)

    # バイト変換
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    return Response(img_io.getvalue(), mimetype='image/png')
@app.route('/status')
def status_page():
    url = request.args.get('url')

    if not url:
        return "URL parameter is required", 400

    service = {"url": url}
    status = check_service(service)
    status_code = status['status_code']

    if isinstance(status_code, int):
        full_status = f"{status_code} {status.get('reason','')}"
    else:
        full_status = status_code

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Status - {url}</title>
        <style>
        body {{
            font-family: monospace;
            text-align: center;
            background: white;
        }}
        .ok {{ color: #00b700; }}
        .r {{ color: #ff8000; }}
        .e {{ color: #ff0c0c; }}
        </style>
    </head>
    <body>
        <h1>Status Detail</h1>
        <p><b>URL:</b> {url}</p>
        <p><b>Status:</b> {full_status}</p>
        <p><b>Response Time:</b> {status.get('elapsed','-')} ms</p>
        <p><b>Last Check:</b> {status.get('last_check','-')}</p>
        <p><a href="/svg?url={url}">SVGで表示</a></p>
        <p><a href="/png?url={url}">PNGで表示</a></p>
        <p><a href="/">← 戻る</a></p>
    </body>
    </html>
    """

    return html

if __name__ == '__main__':
    # 初回チェック
    for service in SERVICES:
        status = check_service(service)
        service_status[service['url']] = status
    
    # バックグラウンド監視スレッドを開始
    monitor_thread = threading.Thread(target=monitor_services, daemon=True)
    monitor_thread.start()
    
    # Flaskアプリを起動
    app.run(host='0.0.0.0', port=8000, debug=True)