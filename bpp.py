from flask import Flask, render_template_string
import requests
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
        response = requests.get(service['url'], timeout=10, allow_redirects=False)
        return {
            'status_code': response.status_code,
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except requests.exceptions.RequestException as e:
        return {
            'status_code': 'Error',
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
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
}
h1{
font-weight:400;
text-align:center;
}
table {
font-size:10px;
margin: 0 auto;
  border: 1px solid #000;
}

table th {
  padding:8px;
  border: 1px solid #000;
}

table td {
  padding:8px;
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
      <th><a href="{{ service.url }}">{{ service.url }}</a></th>
      <td>{{ service.name }}</td>
      <td><div class="{{ service.status_class }}">{{ service.status_display }}</div></td>
    </tr>
    {% endfor %}
  </tbody>
</table>
<div class="timestamp">最終更新: {{ last_update }}</div>
</body>
</html>'''

@app.route('/')
def index():
    """メインページ"""
    services_data = []
    
    for service in SERVICES:
        status = service_status.get(service['url'], {'status_code': 'Pending', 'last_check': 'N/A'})
        status_code = status['status_code']
        
        services_data.append({
            'url': service['url'],
            'name': service['name'],
            'status_class': get_status_class(status_code),
            'status_display': str(status_code)
        })
    
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(HTML_TEMPLATE, services=services_data, last_update=last_update)

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
