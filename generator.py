import json
import re
import urllib.request
from html import escape
from pathlib import Path

OUTPUT_DIR = Path("spb_metro_overlay_site")
STATIONS_DIR = OUTPUT_DIR / "stations"
ASSETS_DIR = OUTPUT_DIR / "assets"

SOURCE_MAP_CANDIDATES = [
    Path("assets/Санкт-Петербург — схема метро.html"),
    Path("Санкт-Петербург — схема метро.html"),
    Path("/mnt/data/Санкт-Петербург — схема метро.html"),
    Path("C:/Users/inhSERVER/Desktop/k/Санкт-Петербург — схема метро.html"),
]
STATION_IMAGE_URL = "https://avatars.mds.yandex.net/i?id=5056857da95e2278d30da10d85decc61_l-5221602-images-thumbs&n=13"
STATION_IMAGE_NAME = "station_image.jpg"
COORDS_FILE = ASSETS_DIR / "station_coordinates.json"
MAP_MARKUP_FILE = ASSETS_DIR / "metro_map_markup.html"

RAW_STATIONS = [
    ("Девяткино", "Линия 1", "l1", 120, 70), ("Гражданский проспект", "Линия 1", "l1", 120, 120),
    ("Академическая", "Линия 1", "l1", 120, 170), ("Политехническая", "Линия 1", "l1", 120, 220),
    ("Площадь Мужества", "Линия 1", "l1", 120, 270), ("Лесная", "Линия 1", "l1", 120, 320),
    ("Выборгская", "Линия 1", "l1", 120, 370), ("Площадь Ленина", "Линия 1", "l1", 120, 420),
    ("Чернышевская", "Линия 1", "l1", 120, 470), ("Площадь Восстания", "Линия 1", "l1", 155, 530),
    ("Владимирская", "Линия 1", "l1", 195, 585), ("Пушкинская", "Линия 1", "l1", 235, 640),
    ("Технологический институт-1", "Линия 1", "l1", 285, 695), ("Балтийская", "Линия 1", "l1", 285, 760),
    ("Нарвская", "Линия 1", "l1", 285, 825), ("Кировский завод", "Линия 1", "l1", 285, 890),
    ("Автово", "Линия 1", "l1", 285, 955), ("Ленинский проспект", "Линия 1", "l1", 285, 1020),
    ("Проспект Ветеранов", "Линия 1", "l1", 285, 1085),

    ("Парнас", "Линия 2", "l2", 380, 70), ("Проспект Просвещения", "Линия 2", "l2", 380, 120),
    ("Озерки", "Линия 2", "l2", 380, 170), ("Удельная", "Линия 2", "l2", 380, 220),
    ("Пионерская", "Линия 2", "l2", 380, 270), ("Чёрная речка", "Линия 2", "l2", 380, 320),
    ("Петроградская", "Линия 2", "l2", 380, 375), ("Горьковская", "Линия 2", "l2", 380, 430),
    ("Невский проспект", "Линия 2", "l2", 380, 535), ("Сенная площадь", "Линия 2", "l2", 380, 635),
    ("Технологический институт-2", "Линия 2", "l2", 380, 695), ("Фрунзенская", "Линия 2", "l2", 380, 760),
    ("Московские ворота", "Линия 2", "l2", 380, 825), ("Электросила", "Линия 2", "l2", 380, 890),
    ("Парк Победы", "Линия 2", "l2", 380, 955), ("Московская", "Линия 2", "l2", 380, 1020),
    ("Звёздная", "Линия 2", "l2", 380, 1085), ("Купчино", "Линия 2", "l2", 380, 1150),

    ("Беговая", "Линия 3", "l3", 690, 130), ("Зенит", "Линия 3", "l3", 690, 190),
    ("Приморская", "Линия 3", "l3", 640, 320), ("Василеостровская", "Линия 3", "l3", 620, 420),
    ("Гостиный двор", "Линия 3", "l3", 535, 535), ("Маяковская", "Линия 3", "l3", 500, 585),
    ("Площадь Александра Невского-1", "Линия 3", "l3", 525, 690), ("Елизаровская", "Линия 3", "l3", 585, 795),
    ("Ломоносовская", "Линия 3", "l3", 645, 875), ("Пролетарская", "Линия 3", "l3", 700, 955),
    ("Обухово", "Линия 3", "l3", 740, 1035), ("Рыбацкое", "Линия 3", "l3", 775, 1115),

    ("Горный институт", "Линия 4", "l4", 170, 905), ("Спасская", "Линия 4", "l4", 330, 635),
    ("Достоевская", "Линия 4", "l4", 405, 585), ("Лиговский проспект", "Линия 4", "l4", 465, 625),
    ("Площадь Александра Невского-2", "Линия 4", "l4", 525, 735), ("Новочеркасская", "Линия 4", "l4", 580, 810),
    ("Ладожская", "Линия 4", "l4", 635, 875), ("Проспект Большевиков", "Линия 4", "l4", 700, 955),
    ("Улица Дыбенко", "Линия 4", "l4", 760, 1035),

    ("Комендантский проспект", "Линия 5", "l5", 760, 75), ("Старая Деревня", "Линия 5", "l5", 760, 135),
    ("Крестовский остров", "Линия 5", "l5", 760, 195), ("Чкаловская", "Линия 5", "l5", 760, 255),
    ("Спортивная", "Линия 5", "l5", 720, 345), ("Адмиралтейская", "Линия 5", "l5", 595, 470),
    ("Садовая", "Линия 5", "l5", 355, 635), ("Звенигородская", "Линия 5", "l5", 320, 735),
    ("Обводный канал", "Линия 5", "l5", 305, 815), ("Волковская", "Линия 5", "l5", 305, 895),
    ("Бухарестская", "Линия 5", "l5", 305, 975), ("Международная", "Линия 5", "l5", 305, 1055),
    ("Проспект Славы", "Линия 5", "l5", 305, 1135), ("Дунайская", "Линия 5", "l5", 305, 1215),
    ("Шушары", "Линия 5", "l5", 305, 1295),
]

LINE_COLORS = {"l1": "#e33d3d", "l2": "#2d8cff", "l3": "#21b35d", "l4": "#ff9d31", "l5": "#8b4dff"}
TRANSFER_STATIONS = {
    "Площадь Восстания", "Владимирская", "Пушкинская", "Технологический институт-1", "Технологический институт-2",
    "Невский проспект", "Гостиный двор", "Сенная площадь", "Спасская", "Садовая", "Достоевская",
    "Площадь Александра Невского-1", "Площадь Александра Невского-2", "Адмиралтейская", "Звенигородская",
    "Маяковская", "Спортивная",
}


def slugify(text: str) -> str:
    translit_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i", "й": "y",
        "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
        "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
        "А": "a", "Б": "b", "В": "v", "Г": "g", "Д": "d", "Е": "e", "Ё": "e", "Ж": "zh", "З": "z", "И": "i", "Й": "y",
        "К": "k", "Л": "l", "М": "m", "Н": "n", "О": "o", "П": "p", "Р": "r", "С": "s", "Т": "t", "У": "u", "Ф": "f",
        "Х": "h", "Ц": "ts", "Ч": "ch", "Ш": "sh", "Щ": "sch", "Ъ": "", "Ы": "y", "Ь": "", "Э": "e", "Ю": "yu", "Я": "ya",
        " ": "-", "—": "-", "–": "-", "/": "-",
    }
    result = "".join(translit_map.get(ch, ch) for ch in text)
    result = re.sub(r"[^a-z0-9\-]+", "", result.lower())
    return re.sub(r"-{2,}", "-", result).strip("-")


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    STATIONS_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)


def try_download(url: str, path: Path) -> bool:
    if path.exists():
        return True
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as exc:
        print(f"Не удалось скачать {url}: {exc}")
        return False


def resolve_source_map_path() -> Path:
    for candidate in SOURCE_MAP_CANDIDATES:
        if candidate.exists():
            return candidate
    checked = "\n".join(f"- {p}" for p in SOURCE_MAP_CANDIDATES)
    raise FileNotFoundError(f"Не найден файл со схемой метро. Проверены пути:\n{checked}")


def extract_scheme_markup(html: str) -> str:
    start = html.find('<div class="metro-scheme-view__scheme-container"')
    if start == -1:
        raise RuntimeError("Не удалось найти контейнер схемы метро в исходном HTML-файле.")
    open_inner = html.find('><div>', start)
    if open_inner == -1:
        raise RuntimeError("Не удалось найти внутренний контейнер схемы метро.")
    open_inner += len('><div>')
    end_marker = '</div></div><div class="metro-zoom-controls"'
    end = html.find(end_marker, open_inner)
    if end == -1:
        raise RuntimeError("Не удалось отделить схему метро от служебных элементов страницы.")
    markup = html[open_inner:end]
    markup = markup.replace(' class="scheme-objects-view__scheme-svg"', "")
    markup = markup.replace(' class="scheme-objects-view__scheme-svg _click-through"', ' class="_click-through"')
    return markup


def extract_map_meta(markup: str) -> tuple[int, int]:
    match = re.search(r'viewBox="\s*[0-9.]+\s+[0-9.]+\s+([0-9.]+)\s+([0-9.]+)\s*"', markup)
    if not match:
        raise RuntimeError("У схемы не найден viewBox.")
    return int(float(match.group(1))), int(float(match.group(2)))


def extract_station_positions(markup: str) -> dict[str, tuple[float, float]]:
    positions: dict[str, tuple[float, float]] = {}
    label_re = re.compile(
        r'<g class="scheme-objects-view__label">.*?<circle[^>]*cx="([0-9.]+)"[^>]*cy="([0-9.]+)"[^>]*>.*?'
        r'<tspan[^>]*>([^<]+)</tspan>',
        re.DOTALL,
    )
    for cx, cy, name in label_re.findall(markup):
        clean_name = re.sub(r"\s+", " ", name).strip()
        if clean_name and clean_name not in positions:
            positions[clean_name] = (float(cx), float(cy))
    return positions


def load_clean_map_markup() -> tuple[str, int, int, Path]:
    source_path = resolve_source_map_path()
    html = source_path.read_text(encoding="utf-8", errors="ignore")
    markup = extract_scheme_markup(html)
    width, height = extract_map_meta(markup)
    return markup, width, height, source_path


def build_station_records() -> list[dict]:
    stations = []
    used = set()
    for name, line, line_id, fallback_x, fallback_y in RAW_STATIONS:
        slug = slugify(name)
        base_slug = slug
        suffix = 2
        while slug in used:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        used.add(slug)
        stations.append({
            "name": name,
            "line": line,
            "line_id": line_id,
            "slug": slug,
            "url": f"stations/{slug}/index.html",
            "fallback_x": fallback_x,
            "fallback_y": fallback_y,
            "is_transfer": name in TRANSFER_STATIONS,
            "description": f"Здесь будет краткое описание станции «{name}». Ты потом сможешь заменить этот текст на свой.",
        })
    return stations


def save_coordinates_file(stations: list[dict], extracted_positions: dict[str, tuple[float, float]], map_width: int, map_height: int) -> None:
    coords_payload = {"map_width": map_width, "map_height": map_height, "stations": []}
    for station in stations:
        x, y = extracted_positions.get(station["name"], (station["fallback_x"], station["fallback_y"]))
        coords_payload["stations"].append({
            "name": station["name"],
            "slug": station["slug"],
            "line_id": station["line_id"],
            "x": round(float(x), 3),
            "y": round(float(y), 3),
        })
    COORDS_FILE.write_text(json.dumps(coords_payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_coordinates_map() -> dict[str, dict]:
    payload = json.loads(COORDS_FILE.read_text(encoding="utf-8"))
    return {item["name"]: item for item in payload.get("stations", [])}


def apply_coordinates(stations: list[dict]) -> list[dict]:
    coords_map = load_coordinates_map()
    prepared = []
    for station in stations:
        coords = coords_map.get(station["name"], {})
        item = dict(station)
        item["x"] = float(coords.get("x", station["fallback_x"]))
        item["y"] = float(coords.get("y", station["fallback_y"]))
        prepared.append(item)
    return prepared


def build_index_html(stations_json: str, map_markup: str, map_width: int, map_height: int) -> str:
    return f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no, maximum-scale=1">
  <title>Метро Санкт-Петербурга — интерактивная карта</title>
  <meta name="description" content="Интерактивная карта метро Санкт-Петербурга для мобильных телефонов">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="phone-only">
    <header class="topbar">
      <h1>Метро Санкт-Петербурга</h1>
      <p class="subtitle">Жесты страницы отключены. Масштабирование работает только внутри карты. Координаты лежат в <code>assets/station_coordinates.json</code>.</p>
      <div class="controls">
        <input id="searchInput" type="text" placeholder="Поиск станции...">
        <div class="filters">
          <button class="filter-btn active" data-line="all">Все</button>
          <button class="filter-btn l1" data-line="l1">1</button>
          <button class="filter-btn l2" data-line="l2">2</button>
          <button class="filter-btn l3" data-line="l3">3</button>
          <button class="filter-btn l4" data-line="l4">4</button>
          <button class="filter-btn l5" data-line="l5">5</button>
        </div>
      </div>
    </header>
    <main class="content">
      <section class="card map-card">
        <div class="map-toolbar">
          <button type="button" class="zoom-btn" id="zoomOutBtn">−</button>
          <button type="button" class="zoom-btn" id="zoomResetBtn">100%</button>
          <button type="button" class="zoom-btn" id="zoomInBtn">+</button>
        </div>
        <div id="mapViewport" class="map-viewport">
          <div id="mapScene" class="map-scene">
            <div id="mapContent" class="map-content" style="width:{map_width}px;height:{map_height}px;">
              <div class="map-image map-image--markup">{map_markup}</div>
            </div>
          </div>
        </div>
      </section>
      <section class="card">
        <div class="section-head"><h2>Список станций</h2><span id="counter" class="counter"></span></div>
        <div id="stationList" class="station-list"></div>
      </section>
    </main>
  </div>
  <div class="desktop-warning"><div class="desktop-warning__box"><h2>Этот сайт сделан только для телефона</h2><p>Открой его на мобильном устройстве или включи мобильный режим в браузере.</p></div></div>
  <script>window.METRO_STATIONS = {stations_json};</script>
  <script src="app.js"></script>
</body>
</html>'''


def build_station_html(station: dict) -> str:
    safe_name = escape(station["name"])
    return f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no, maximum-scale=1">
  <title>{safe_name} — метро Санкт-Петербурга</title>
  <meta name="description" content="Информация о станции {safe_name}">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body class="station-page-body">
  <div class="phone-only">
    <header class="station-header">
      <a href="../../index.html" class="back-link">← Назад к карте</a>
      <span class="line-chip {station['line_id']}">{station['line']}</span>
      <h1>{safe_name}</h1>
    </header>
    <main class="station-main">
      <div class="hero-box"><img src="{station['image_src']}" alt="{safe_name}" class="station-hero"></div>
      <section class="card station-card">
        <h2>Краткая информация</h2>
        <p><strong>{safe_name}</strong> — станция метро Санкт-Петербурга.</p>
        <p>{escape(station['description'])}</p>
      </section>
    </main>
  </div>
</body>
</html>'''


def build_styles_css() -> str:
    return r'''
:root{--bg1:#08101e;--bg2:#101a31;--panel:rgba(18,27,49,.88);--stroke:rgba(255,255,255,.10);--text:#f6f8ff;--muted:#9db0d7;--shadow:0 18px 48px rgba(0,0,0,.34);--l1:#e33d3d;--l2:#2d8cff;--l3:#21b35d;--l4:#ff9d31;--l5:#8b4dff}*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}html,body{margin:0;padding:0;min-height:100%;color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;background:radial-gradient(circle at 15% 10%, rgba(53,118,255,.12), transparent 24%),radial-gradient(circle at 85% 14%, rgba(141,77,255,.12), transparent 24%),linear-gradient(180deg, var(--bg1), var(--bg2));overscroll-behavior:none;touch-action:pan-x pan-y}body{overflow-x:hidden}.phone-only{max-width:560px;margin:0 auto;padding:calc(env(safe-area-inset-top, 0px) + 14px) 14px calc(env(safe-area-inset-bottom, 0px) + 24px)}.topbar{background:var(--panel);border:1px solid var(--stroke);border-radius:24px;padding:16px;box-shadow:var(--shadow);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}h1{margin:0;font-size:30px;line-height:1.05}.subtitle{margin:10px 0 0;font-size:14px;color:var(--muted);line-height:1.45}.subtitle code{color:#fff;background:rgba(255,255,255,.08);padding:2px 6px;border-radius:8px}.controls{margin-top:16px;display:grid;gap:12px}#searchInput{width:100%;padding:14px 16px;border-radius:18px;border:1px solid var(--stroke);background:rgba(255,255,255,.05);color:var(--text);font-size:15px;outline:none}#searchInput::placeholder{color:#7e90ba}.filters{display:flex;flex-wrap:wrap;gap:8px}.filter-btn,.zoom-btn{border:0;height:40px;min-width:46px;padding:0 14px;border-radius:999px;font-weight:800;color:#fff;background:#2a3755;cursor:pointer}.filter-btn.active{box-shadow:0 0 0 2px rgba(255,255,255,.28) inset}.filter-btn.l1{background:var(--l1)}.filter-btn.l2{background:var(--l2)}.filter-btn.l3{background:var(--l3)}.filter-btn.l4{background:var(--l4)}.filter-btn.l5{background:var(--l5)}.content{display:grid;gap:16px;margin-top:16px}.card{background:var(--panel);border:1px solid var(--stroke);border-radius:24px;box-shadow:var(--shadow);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}.map-card{padding:12px}.map-toolbar{display:flex;justify-content:flex-end;gap:8px;margin-bottom:10px}.map-viewport{position:relative;width:100%;height:min(72vh,560px);border-radius:20px;overflow:hidden;border:1px solid rgba(255,255,255,.08);background:#eef6ff;touch-action:none;user-select:none}.map-scene{position:absolute;left:0;top:0;inset:0;overflow:visible}.map-content{position:absolute;left:0;top:0;transform-origin:0 0;will-change:transform}.map-image{display:block;width:100%;height:100%}.map-image--markup{position:absolute;inset:0;background:#eef6ff}.map-image--markup svg{position:absolute;inset:0;width:100%;height:100%;display:block}.map-image--markup ._click-through{pointer-events:none}.stations-layer{position:absolute;inset:0;overflow:visible}.station-pin{position:absolute;transform:translate(-50%,-50%);width:34px;height:34px;border-radius:50%;cursor:pointer;text-decoration:none;background:rgba(255,255,255,0)}.station-pin::before{content:"";position:absolute;left:50%;top:50%;width:16px;height:16px;transform:translate(-50%,-50%);border-radius:50%;border:3px solid #fff;box-shadow:0 6px 16px rgba(0,0,0,.22)}.station-pin.transfer::before{width:20px;height:20px;border-width:4px;background:rgba(255,255,255,.18)}.station-pin-label{position:absolute;top:50%;left:calc(100% + 8px);transform:translateY(-50%);white-space:nowrap;background:rgba(10,16,30,.88);color:#fff;font-size:11px;font-weight:700;line-height:1.2;padding:6px 8px;border-radius:10px;border:1px solid rgba(255,255,255,.08);box-shadow:0 8px 18px rgba(0,0,0,.25);opacity:0;pointer-events:none;transition:opacity .18s ease}.station-pin:hover .station-pin-label,.station-pin:focus .station-pin-label,.station-pin:active .station-pin-label{opacity:1}.station-pin.right .station-pin-label{left:auto;right:calc(100% + 8px)}.section-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:16px 16px 0}.section-head h2{margin:0;font-size:19px}.counter{color:var(--muted);font-size:13px}.station-list{display:grid;gap:10px;padding:16px}.station-item{display:flex;gap:12px;align-items:center;text-decoration:none;color:var(--text);border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.04);border-radius:18px;padding:13px 14px}.station-item__dot{width:15px;height:15px;border-radius:50%;border:2px solid #fff;flex:0 0 15px}.station-item__meta{display:grid;gap:2px}.station-item__name{font-size:15px;font-weight:800}.station-item__line{color:var(--muted);font-size:12px}.station-header{padding:8px 2px 14px}.back-link{display:inline-block;text-decoration:none;color:#d5e0ff;font-weight:800;margin-bottom:14px}.line-chip{display:inline-flex;align-items:center;padding:8px 12px;border-radius:999px;color:#fff;font-size:13px;font-weight:900;margin-bottom:12px}.line-chip.l1{background:var(--l1)}.line-chip.l2{background:var(--l2)}.line-chip.l3{background:var(--l3)}.line-chip.l4{background:var(--l4)}.line-chip.l5{background:var(--l5)}.station-main{display:grid;gap:16px}.hero-box{overflow:hidden;border-radius:24px;border:1px solid var(--stroke);box-shadow:var(--shadow)}.station-hero{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;background:#101a31}.station-card{padding:16px}.desktop-warning{display:none}@media (min-width:768px){.phone-only{display:none}.desktop-warning{display:grid;min-height:100vh;place-items:center;padding:24px}.desktop-warning__box{max-width:520px;border-radius:26px;background:var(--panel);border:1px solid var(--stroke);padding:28px;text-align:center;box-shadow:var(--shadow)}}
'''


def build_app_js() -> str:
    return r'''
const stations = window.METRO_STATIONS || [];
const stationList = document.getElementById('stationList');
const counter = document.getElementById('counter');
const searchInput = document.getElementById('searchInput');
const filterButtons = document.querySelectorAll('.filter-btn');
const mapViewport = document.getElementById('mapViewport');
const mapScene = document.getElementById('mapScene');
const zoomInBtn = document.getElementById('zoomInBtn');
const zoomOutBtn = document.getElementById('zoomOutBtn');
const zoomResetBtn = document.getElementById('zoomResetBtn');
let currentLine = 'all';
let currentSearch = '';

function matchesFilters(station){const q=currentSearch.trim().toLowerCase();return (!q||station.name.toLowerCase().includes(q))&&(currentLine==='all'||station.line_id===currentLine)}
function renderPins(){}
function colorizePins(){}
function renderList(){if(!stationList)return;stationList.innerHTML='';const filtered=stations.filter(matchesFilters);if(counter)counter.textContent=filtered.length+' шт.';if(!filtered.length){stationList.innerHTML='<div class="station-item"><div class="station-item__meta"><div class="station-item__name">Ничего не найдено</div><div class="station-item__line">Попробуй другой запрос</div></div></div>';return}filtered.forEach((station)=>{const a=document.createElement('a');a.className='station-item';a.href=station.url;a.innerHTML=`<span class="station-item__dot" style="background:${station.color}"></span><span class="station-item__meta"><span class="station-item__name">${station.name}</span><span class="station-item__line">${station.line}</span></span>`;stationList.appendChild(a)})}
function rerender(){renderPins();renderList();document.querySelectorAll('.station-pin').forEach((pin)=>{const station=stations.find(s=>s.url===pin.getAttribute('href'));if(station){pin.style.setProperty('--pin-color', station.color);pin.style.setProperty('--dot-color', station.color);pin.style.setProperty('color', station.color);pin.style.setProperty('border-color', station.color);pin.style.setProperty('background', 'transparent');pin.style.setProperty('box-shadow', 'none');pin.style.setProperty('outline', 'none');pin.style.setProperty('opacity', '1');pin.style.setProperty('z-index', '5');pin.style.setProperty('position', 'absolute');pin.style.setProperty('text-decoration', 'none');pin.style.setProperty('cursor', 'pointer');pin.style.setProperty('display', matchesFilters(station)?'block':'none');pin.style.setProperty('--station-color', station.color);pin.style.setProperty('--fill', station.color);pin.style.setProperty('--stroke', '#fff');pin.style.setProperty('--ring', station.color);pin.style.setProperty('--size', station.is_transfer ? '20px' : '16px');
const beforeColor = station.color;
pin.style.background = 'transparent';
pin.style.border = '0';
pin.dataset.color = beforeColor;
}
});}
if(searchInput){searchInput.addEventListener('input',(e)=>{currentSearch=e.target.value||'';rerender()})}
filterButtons.forEach((btn)=>{btn.addEventListener('click',()=>{filterButtons.forEach((b)=>b.classList.remove('active'));btn.classList.add('active');currentLine=btn.dataset.line||'all';rerender()})});

(function(){
  if(!mapViewport || !mapScene || !mapContent) return;
  const state = {scale:1, minScale:1, maxScale:8, x:0, y:0, pointers:new Map(), dragStartX:0, dragStartY:0, startX:0, startY:0, pinchStartDistance:0, pinchStartScale:1, pinchWorldX:0, pinchWorldY:0};
  const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));
  const rect=()=>mapViewport.getBoundingClientRect();
  const sceneW=()=>mapContent.offsetWidth;
  const sceneH=()=>mapContent.offsetHeight;
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const center=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});

  function computeMinScale(){
    const fitX = mapViewport.clientWidth / sceneW();
    const fitY = mapViewport.clientHeight / sceneH();
    state.minScale = Math.min(fitX, fitY);
    if(!isFinite(state.minScale) || state.minScale <= 0) state.minScale = 1;
  }

  function clampPan(){
    const viewportW = mapViewport.clientWidth;
    const viewportH = mapViewport.clientHeight;
    const scaledW = sceneW() * state.scale;
    const scaledH = sceneH() * state.scale;
    const minX = scaledW <= viewportW ? (viewportW - scaledW) / 2 : viewportW - scaledW;
    const maxX = scaledW <= viewportW ? (viewportW - scaledW) / 2 : 0;
    const minY = scaledH <= viewportH ? (viewportH - scaledH) / 2 : viewportH - scaledH;
    const maxY = scaledH <= viewportH ? (viewportH - scaledH) / 2 : 0;
    state.x = clamp(state.x, minX, maxX);
    state.y = clamp(state.y, minY, maxY);
  }

  function applyTransform(){
    clampPan();
    mapContent.style.transform = `translate(${state.x}px, ${state.y}px) scale(${state.scale})`;
    if(zoomResetBtn) zoomResetBtn.textContent = Math.round((state.scale / state.minScale) * 100) + '%';
  }

  function zoomAt(clientX, clientY, nextScale){
    const r = rect();
    const localX = clientX - r.left;
    const localY = clientY - r.top;
    const worldX = (localX - state.x) / state.scale;
    const worldY = (localY - state.y) / state.scale;
    state.scale = clamp(nextScale, state.minScale * 0.35, state.maxScale);
    state.x = localX - worldX * state.scale;
    state.y = localY - worldY * state.scale;
    applyTransform();
  }

  function resetView(){
    computeMinScale();
    state.scale = state.minScale;
    state.x = (mapViewport.clientWidth - sceneW() * state.scale) / 2;
    state.y = (mapViewport.clientHeight - sceneH() * state.scale) / 2;
    applyTransform();
  }

  mapViewport.addEventListener('pointerdown', (e)=>{
    mapViewport.setPointerCapture(e.pointerId);
    state.pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
    if(state.pointers.size === 1){
      state.dragStartX = e.clientX; state.dragStartY = e.clientY; state.startX = state.x; state.startY = state.y;
    } else if(state.pointers.size === 2){
      const [p1,p2] = [...state.pointers.values()];
      const c = center(p1,p2);
      state.pinchStartDistance = distance(p1,p2);
      state.pinchStartScale = state.scale;
      const r = rect();
      state.pinchWorldX = (c.x - r.left - state.x) / state.scale;
      state.pinchWorldY = (c.y - r.top - state.y) / state.scale;
    }
    e.preventDefault();
  }, {passive:false});

  mapViewport.addEventListener('pointermove', (e)=>{
    if(!state.pointers.has(e.pointerId)) return;
    state.pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
    if(state.pointers.size === 1){
      state.x = state.startX + (e.clientX - state.dragStartX);
      state.y = state.startY + (e.clientY - state.dragStartY);
      applyTransform();
    } else if(state.pointers.size === 2){
      const [p1,p2] = [...state.pointers.values()];
      const c = center(p1,p2);
      const d = distance(p1,p2);
      state.scale = clamp(state.pinchStartScale * (d / Math.max(state.pinchStartDistance, 1)), state.minScale * 0.35, state.maxScale);
      const r = rect();
      state.x = (c.x - r.left) - state.pinchWorldX * state.scale;
      state.y = (c.y - r.top) - state.pinchWorldY * state.scale;
      applyTransform();
    }
    e.preventDefault();
  }, {passive:false});

  const release = (e)=>{ state.pointers.delete(e.pointerId); if(state.pointers.size === 1){ const p=[...state.pointers.values()][0]; state.dragStartX=p.x; state.dragStartY=p.y; state.startX=state.x; state.startY=state.y; } };
  mapViewport.addEventListener('pointerup', release);
  mapViewport.addEventListener('pointercancel', release);
  mapViewport.addEventListener('pointerleave', release);

  mapViewport.addEventListener('wheel', (e)=>{ e.preventDefault(); zoomAt(e.clientX, e.clientY, state.scale * (e.deltaY < 0 ? 1.12 : 0.88)); }, {passive:false});
  mapViewport.addEventListener('dblclick', (e)=>{ e.preventDefault(); zoomAt(e.clientX, e.clientY, state.scale * 1.3); });

  if(zoomInBtn) zoomInBtn.addEventListener('click', ()=>{ const r=rect(); zoomAt(r.left+r.width/2, r.top+r.height/2, state.scale*1.2); });
  if(zoomOutBtn) zoomOutBtn.addEventListener('click', ()=>{ const r=rect(); zoomAt(r.left+r.width/2, r.top+r.height/2, state.scale/1.2); });
  if(zoomResetBtn) zoomResetBtn.addEventListener('click', resetView);

  document.addEventListener('gesturestart', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('gesturechange', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('gestureend', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('touchmove', (e)=>{ if(e.touches && e.touches.length > 1) e.preventDefault(); }, {passive:false});

  window.addEventListener('resize', resetView);
  resetView();
})();

rerender();

'''


def write_site(stations: list[dict], map_markup: str, map_width: int, map_height: int) -> None:
    stations_public = [{
        "name": s["name"], "line": s["line"], "line_id": s["line_id"], "url": s["url"],
        "x": s["x"], "y": s["y"], "is_transfer": s["is_transfer"], "color": LINE_COLORS[s["line_id"]],
    } for s in stations]
    MAP_MARKUP_FILE.write_text(map_markup, encoding="utf-8")
    (OUTPUT_DIR / "index.html").write_text(build_index_html(json.dumps(stations_public, ensure_ascii=False, indent=2), map_markup, map_width, map_height), encoding="utf-8")
    (OUTPUT_DIR / "styles.css").write_text(build_styles_css(), encoding="utf-8")
    (OUTPUT_DIR / "app.js").write_text(build_app_js(), encoding="utf-8")

    for station in stations:
        station_dir = STATIONS_DIR / station["slug"]
        station_dir.mkdir(parents=True, exist_ok=True)
        downloaded = try_download(STATION_IMAGE_URL, station_dir / STATION_IMAGE_NAME)
        station["image_src"] = f"./{STATION_IMAGE_NAME}" if downloaded else STATION_IMAGE_URL
        (station_dir / "image_source.txt").write_text(STATION_IMAGE_URL + "\n", encoding="utf-8")
        (station_dir / "index.html").write_text(build_station_html(station), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    map_markup, map_width, map_height, source_path = load_clean_map_markup()
    station_templates = build_station_records()
    extracted_positions = extract_station_positions(map_markup)
    if not COORDS_FILE.exists():
        save_coordinates_file(station_templates, extracted_positions, map_width, map_height)
    stations = apply_coordinates(station_templates)
    write_site(stations, map_markup, map_width, map_height)
    matched = sum(1 for station in station_templates if station["name"] in extracted_positions)
    print("Готово.")
    print(f"Сайт создан в папке: {OUTPUT_DIR.resolve()}")
    print(f"Карта взята из файла: {source_path}")
    print(f"Координаты станций лежат здесь: {COORDS_FILE.resolve()}")
    print(f"Автоматически найдено координат из схемы: {matched} из {len(station_templates)}")


if __name__ == "__main__":
    main()
