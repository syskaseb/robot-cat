"""Read-only primary-source image/link discovery; no purchases or hardware I/O."""
import json
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
import hashlib

if sys.argv[1:] == ['--save-figures']:
    out = Path(__file__).resolve().parents[2] / 'hardware/electronics/full-cat/connection-map-e4-r1/sources'
    out.mkdir(parents=True, exist_ok=True)
    sources = {
        'st3215-details-9.jpg': 'https://www.waveshare.com/img/devkit/accessories/ST3215-Servo/ST3215-Servo-details-9.jpg?v=26061202',
        'st3215-details-23.jpg': 'https://www.waveshare.com/img/devkit/accessories/ST3215-Servo/ST3215-Servo-details-23.jpg?v=26061202',
        'st3215-factory-pack.jpg': 'https://www.waveshare.com/img/devkit/accessories/ST3215-Servo/ST3215-Servo-details-pack.jpg?v=26061203',
        'st3215-rear.jpg': 'https://www.waveshare.com/media/catalog/product/s/t/st3215-servo-3_5.jpg',
        'mg92b-factory.jpg': 'https://cdn-shop.adafruit.com/970x728/2307-00.jpg',
        'p309-rear.jpg': 'https://cdn3.botland.com.pl/72469-large_default/wskaznik-napiecia-li-pol-1-8s-z-buzzerem-p309.jpg',
        'p309-labels.jpg': 'https://cdn3.botland.com.pl/72470-large_default/wskaznik-napiecia-li-pol-1-8s-z-buzzerem-p309.jpg',
        'pack-balance.jpg': 'https://gensace.de/cdn/shop/files/4_44_11.jpg?v=1729759094&width=1214',
    }
    report = []
    for name, url in sources.items():
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read()
            (out / name).write_bytes(data)
            report.append(dict(file=name, url=url, sha256=hashlib.sha256(data).hexdigest(), visual_review=False))
        except Exception as exc:
            report.append(dict(file=name, url=url, error=str(exc), visual_review=False))
    (out / 'retrieval.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))
    sys.exit(0)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'img':
            self.items.append({k: a[k] for k in ('src', 'data-src', 'alt') if k in a})


for url in sys.argv[1:]:
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(request, timeout=20).read().decode('utf-8', errors='replace')
        parser = Links()
        parser.feed(html)
        relevant = [i for i in parser.items if any(s in str(i).lower() for s in
                    ('st3215', '2307', '05015', 'p309', 'gea223', 'g-tech'))]
        print(json.dumps({'url': url, 'images': relevant}))
    except Exception as exc:
        print(json.dumps({'url': url, 'error': str(exc)}))
