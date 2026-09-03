"""Robot Cat - plan zakupowy: dwie wersje i decyzja.

Rebuild from the repo root:

    python docs/report/make_plan.py docs/plan-zakupowy.pdf

Needs reportlab and Calibri, so it runs on Windows, not in the ROS container.
Prices are a snapshot; re-check every link before paying.
"""

import pathlib
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

# Calibri on Windows, where these documents are normally built. Carlito is
# metrically identical to Calibri, so rebuilding on macOS or Linux repaginates
# to exactly the same pages; DejaVu Sans Mono stands in for Consolas. A font
# with Polish glyphs is not optional - reportlab's built-in Helvetica has no
# l-stroke or ogonek and renders every "l", "a" and "e" as a black box.
_WIN = pathlib.Path(r"C:\Windows\Fonts")
_MAC = pathlib.Path.home() / "Library" / "Fonts"
_LIN = pathlib.Path("/usr/share/fonts/truetype")


def _font(*candidates):
    for c in candidates:
        if pathlib.Path(c).exists():
            return str(c)
    raise FileNotFoundError(
        "no usable font. Install Calibri (Windows) or Carlito "
        "(brew install --cask font-carlito / apt install fonts-crosextra-carlito). "
        f"Looked in: {[str(c) for c in candidates]}"
    )


pdfmetrics.registerFont(TTFont("Cal", _font(
    _WIN / "calibri.ttf", _MAC / "Carlito-Regular.ttf",
    _LIN / "crosextra/Carlito-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Cal-B", _font(
    _WIN / "calibrib.ttf", _MAC / "Carlito-Bold.ttf",
    _LIN / "crosextra/Carlito-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Cal-I", _font(
    _WIN / "calibrii.ttf", _MAC / "Carlito-Italic.ttf",
    _LIN / "crosextra/Carlito-Italic.ttf")))
pdfmetrics.registerFontFamily("Cal", normal="Cal", bold="Cal-B", italic="Cal-I")

INK = colors.HexColor("#16191d")
ACCENT = colors.HexColor("#0f4c5c")
WARM = colors.HexColor("#b3541e")
MUTED = colors.HexColor("#5f6b73")
RULE = colors.HexColor("#d3dade")
PANEL = colors.HexColor("#f2f5f6")
GOOD = colors.HexColor("#1c6b45")

ss = getSampleStyleSheet()


def st(name, **kw):
    base = dict(fontName="Cal", fontSize=10, leading=14.5, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, parent=ss["Normal"], **base)


Title = st("Title", fontName="Cal-B", fontSize=25, leading=29, textColor=ACCENT)
Sub = st("Sub", fontSize=12.5, leading=17, textColor=MUTED)
H1 = st("H1", fontName="Cal-B", fontSize=15.5, leading=19, textColor=ACCENT,
        spaceBefore=16, spaceAfter=6, keepWithNext=True)
H2 = st("H2", fontName="Cal-B", fontSize=11.5, leading=15, textColor=INK,
        spaceBefore=10, spaceAfter=4, keepWithNext=True)
Body = st("Body", alignment=TA_JUSTIFY, spaceAfter=7)
Small = st("Small", fontSize=8.7, leading=12, textColor=MUTED)
Cell = st("Cell", fontSize=9.2, leading=12.5)
CellB = st("CellB", fontName="Cal-B", fontSize=9.2, leading=12.5)
CellH = st("CellH", fontName="Cal-B", fontSize=9, leading=12, textColor=colors.white)


def para(txt, style=Body):
    return Paragraph(txt, style)


def callout(title, text, tone=WARM):
    inner = [
        [Paragraph(f'<font color="{tone.hexval()}"><b>{title}</b></font>',
                   st("cot", fontName="Cal-B", fontSize=10.5, leading=14))],
        [Paragraph(text, st("cob", fontSize=9.6, leading=13.5, alignment=TA_JUSTIFY))],
    ]
    t = Table(inner, colWidths=[158 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, tone),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, 1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
    ]))
    return KeepTogether([t])


def table(header, rows, widths, aligns=None, highlight=None):
    data = [[Paragraph(h, CellH) for h in header]]
    for r in rows:
        data.append([c if isinstance(c, Paragraph) else Paragraph(str(c), Cell)
                     for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, ACCENT),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafb")))
    if aligns:
        for col, al in aligns.items():
            style.append(("ALIGN", (col, 0), (col, -1), al))
    if highlight:
        for i in highlight:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#e6f0f2")))
    t.setStyle(TableStyle(style))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(26 * mm, 285 * mm, 184 * mm, 285 * mm)
    canvas.setFont("Cal", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(26 * mm, 287.5 * mm, "Robot Cat — plan zakupowy")
    canvas.drawRightString(184 * mm, 287.5 * mm, "wrzesień 2026")
    canvas.line(26 * mm, 17 * mm, 184 * mm, 17 * mm)
    canvas.drawString(26 * mm, 12.5 * mm,
                      "Ceny orientacyjne — sprawdzić każdy link przed zapłatą")
    canvas.drawRightString(184 * mm, 12.5 * mm, f"{doc.page}")
    canvas.restoreState()


# Prices checked in September 2026. The ones marked "szac." below are the only
# estimates - everything else came off a shop page. Re-check every line before
# paying; this is a snapshot, not a quote.
PARTS = [
    ("NAPĘD I MAGISTRALA", None, None),
    ("12 × Waveshare ST3215 + Bus Servo Adapter (A)",
     "napęd nóg; USB-UART ↔ TTL, komendy i telemetria", "1327,90"),
    ("3 × mikroserwo + Grove PCA9685", "głowa 2 osie, ogon", "138,60"),
    ("CZUJNIKI I INTERAKCJA", None, None),
    ("BNO085 — 9-DoF IMU", "równowaga, kurs", "135,00"),
    ("VL53L5CX — ToF 8×8, zasięg 4 m", "omijanie przeszkód", "69,90"),
    ("TTP223 + MAX98357A + głośnik 5 W (100×45×21 mm)",
     "głaskanie, miauczenie, mowa", "60,80"),
    ("ReSpeaker Lite USB 2-Mic", "słuch — komendy głosowe", "116,00"),
    ("WZROK", None, None),
    ("Camera Module 3 NoIR Wide 120°", "wzrok, także po ciemku", "199,00"),
    ("Doświetlacz IR 850 nm 3 W — para", "drugie oko, nocny wzrok", "19,90"),
    ("microSD 64 GB", "system i modele — szac.", "49,00"),
    ("KOMPUTER POCZĄTKOWY", None, None),
    ("Raspberry Pi 4B", "Raspberry Pi OS 64-bit; już posiadany", "0,00"),
    ("ZASILANIE", None, None),
    ("LiPo 3S 2200 mAh, min. 30C + ładowarka B6AC",
     "lekki pakiet bazowy — szac.", "259,00"),
    ("Botland PLL-02580 — Pololu D24V90F5, 5 V / 9 A",
     "Pi 4B/Pi 5; złącza ARK trzeba wlutować", "149,00"),
    ("Druga przetwornica 5 V / 3 A", "z gotowymi zaciskami; mikroserwa i audio - szac.", "49,00"),
    ("Botland KAB-06897 — listwa zaciskowa 30 A",
     "zaciski śrubowe prototypowej dystrybucji", "7,40"),
    ("Botland KAB-05473 — 10 × oprawka bezpiecznika 5×20 mm / 10 A",
     "4 zabezpieczone gałęzie nóg", "10,60"),
    ("Botland JUS-22264 — zestaw bezpieczników WTA 5×20 mm",
     "wkładki 10 A dla gałęzi + zapas", "24,90"),
    ("Botland KAB-07515 — wtyk XT60 z przewodem 10 cm",
     "wejście pakietu do instalacji robota", "15,90"),
    ("Botland NSZ-05375 — zestaw rurek termokurczliwych",
     "izolacja lutowanych połączeń wiązki", "9,95"),
    ("4 × para XT30U (wtyk + gniazdo), Kamami 581960",
     "odłączane zasilanie każdej nogi; 4 × 5,13 zł", "20,52"),
    ("Wyłącznik i oprawka bezpiecznika głównego 30 A",
     "wymagane; brak pasującego gotowego kompletu w Botland", "do wyceny"),
    ("4 × wiązka zasilania nogi z wtryskiem 5264-3P",
     "przewody i złącza sygnału; XT30U wycenione osobno", "do wyceny"),
    ("MECHANIKA", None, None),
    ("PETG czarny 1 kg", "pierwszy komplet wydruków", "94,90"),
    ("PÓŹNIEJSZA WYMIANA KOMPUTERA", None, None),
    ("Raspberry Pi 5 8 GB", "sterowanie i wizja", "829,90"),
    ("AI HAT+ 13 TOPS (Hailo-8L)", "rozpoznawanie obrazu", "329,00"),
    ("Active Cooler do Pi 5", "chłodzenie — szac.", "29,90"),
    ("Kabel CSI 22-pin ↔ 15-pin", "kamera po zmianie na Pi 5 — szac.", "19,90"),
]

PI4_TOTAL = "2757,27 zł"
PI5_UPGRADE_TOTAL = "1208,70 zł"
TOTAL = "3965,97 zł"
WORKSHOP_TOTAL = "308,60 zł"


def parts_rows():
    """Group headers are rows with no price; they render as a band."""
    rows, bands = [], []
    for i, (name, role, cost) in enumerate(PARTS, start=1):
        if cost is None:
            rows.append([Paragraph(f"<b>{name}</b>", CellB), "", ""])
            bands.append(len(rows))
        else:
            rows.append([name, role, Paragraph(cost, Cell)])
    rows.append([Paragraph("<b>RAZEM PO WYMIANIE NA PI 5 + AI HAT+</b>", CellB), "",
                 Paragraph(f'<b><font color="{ACCENT.hexval()}">{TOTAL} + pozycje niewycenione</font></b>',
                           CellB)])
    return rows, bands


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=26 * mm, rightMargin=26 * mm,
                          topMargin=24 * mm, bottomMargin=22 * mm,
                          title="Robot Cat — plan zakupowy",
                          author="analiza")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=header_footer)])
    s = []

    s.append(Spacer(1, 4 * mm))
    s.append(para("Robot Cat", Title))
    s.append(para("Plan zakupowy",
                  st("s2", fontName="Cal-B", fontSize=13.5, leading=17,
                     textColor=INK, spaceBefore=2)))
    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Plan zakupowy robota bez narzuconej kolejności zakupów. Komputerem "
        "początkowym jest posiadane Raspberry Pi 4B; później zostanie wymienione "
        "na Pi 5 z AI HAT+. Obie konfiguracje używają Raspberry Pi OS 64-bit. "
        "Lista nie obejmuje szczegółowych śrub i mocowań, których rozmiary "
        "wynikną z nowego CAD-u.", Sub))
    s.append(Spacer(1, 5 * mm))

    s.append(callout(
        f"Pi 4B: {PI4_TOTAL}  |  wymiana na Pi 5 + AI HAT+: {PI5_UPGRADE_TOTAL}",
        f"Suma wszystkich zakupów po wymianie: {TOTAL}. Posiadane Pi 4B ma "
        "koszt 0 zł. W cenie wymiany są Pi 5, AI HAT+, chłodzenie i właściwy "
        "kabel CSI. "
        "Suma obejmuje sześć pozycji zasilania z Botlandu oraz cztery pary XT30U. "
        "Do wyceny pozostają: główny wyłącznik i oprawka bezpiecznika 30 A, "
        "przewody i złącza sygnału czterech wiązek nóg oraz elementy montażowe. "
        "Plan opisuje docelowy komplet, ale nie ustala, w jakiej kolejności "
        "pozostałe elementy mają zostać zamówione.",
        WARM))
    s.append(Spacer(1, 5 * mm))

    rows, bands = parts_rows()
    s.append(table(
        ["Pozycja", "Rola", "Koszt"],
        rows,
        [82 * mm, 44 * mm, 32 * mm],
        aligns={2: "RIGHT"},
        highlight=bands + [len(rows)]))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        '<b>XT30U:</b> cztery pary, po jednej na nogę, pozwalają odłączyć jej '
        'zasilanie od korpusu. Sygnał TTL biegnie osobno. Fabryczne przewody '
        '5264-3P serw nie zastępują tego rozłączenia. '
        'Cena pary 5,13 zł, sprawdzona 03.09.2026: '
        '<link href="https://kamami.pl/zlacza-adaptery/581960-xt30u-zlacze-wysokopradowe-wtyk-gniazdo-5906623459131.html" color="#167d9a">Kamami 581960</link>.', Body))
    s.append(para(
        "<b>Umie:</b> chodzić i skręcać na czterech łapach, ruszać głową w "
        "dwóch osiach i ogonem, reagować na głaskanie, miauczeć, wiedzieć że "
        "się przechyla, omijać przeszkody, patrzeć — także w ciemności — "
        "rozpoznawać obiekty w czasie rzeczywistym i łączyć się przez Wi-Fi "
        "oraz Bluetooth (pad PS4).", Body))

    # -------------------------------------------------------- komputer
    s.append(para("Komputer: Pi 4B teraz, Pi 5 później", H1))
    s.append(para(
        "Pierwszy robot działa na Raspberry Pi 4B z Raspberry Pi OS 64-bit: "
        "obsługuje chód, magistralę serw, IMU, ToF, audio i kamerę. Konstrukcja "
        "od początku dostaje wymienną tackę komputera, dostęp do USB i CSI, "
        "zapas wysokości na HAT oraz wentylację. Późniejsza zmiana na Pi 5 z "
        "AI HAT+ zachowuje ten sam system bazowy i ma wymagać przełożenia tacki "
        "oraz wiązek, nie przebudowy kota.", Body))

    s.append(table(
        ["Konfiguracja", "Zakres"],
        [
            ["Początkowo: Pi 4B", "Raspberry Pi OS 64-bit; sterowanie, sensory, kamera"],
            [Paragraph("<b>Pi 5 + AI HAT+ 13 TOPS</b>", CellB),
             Paragraph('<b><font color="#1c6b45">Raspberry Pi OS 64-bit; lokalne rozpoznawanie obrazu</font></b>', CellB)],
        ],
        [68 * mm, 90 * mm],
        highlight=[2]))

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Co musi pozostać wymienne",
        "Pi 4B i Pi 5 mają inne rozmieszczenie części złączy i inne potrzeby "
        "chłodzenia. Kamera na Pi 4B używa taśmy 15-pinowej, a po zmianie na "
        "Pi 5 dostaje przewód 22-pin ↔ 15-pin. Magistrala serw pozostaje na "
        "USB z oboma komputerami. Pi 5 i HAT wymagają też zapasu przestrzeni nad "
        "płytką oraz mocniejszej gałęzi 5 V.",
        ACCENT))

    s.append(para(
        "AI HAT+ 13 TOPS pozostaje docelowym wariantem dla Pi 5. Nie działa z "
        "Pi 4B, ponieważ wymaga interfejsu PCIe dostępnego w Pi 5. Do czasu "
        "wymiany komputera omijanie przeszkód realizuje VL53L5CX, a kamera "
        "służy do podglądu i lżejszych eksperymentów wizyjnych.", Body))

    s.append(callout(
        "Zasilanie przygotowane pod oba komputery",
        "Pi 4B wymaga mniej prądu, ale główna gałąź komputera od początku ma "
        "dawać 5 V z zapasem pod Pi 5. Wybieramy Pololu D24V90F5 5 V / 9 A; "
        "do płytki trzeba wlutować dołączone zaciski śrubowe ARK. Mikroserwa i audio pozostają "
        "na osobnej gałęzi 5 V, żeby ich skoki prądu nie resetowały komputera. "
        "Do BOM-u weszły też KAB-06897, KAB-05473, JUS-22264, KAB-07515 i "
        "NSZ-05375. Listwa wymaga krótkich mostków przewodowych. Poza Botlandem "
        "trzeba dobrać główny wyłącznik z bezpiecznikiem 30 A oraz złącza i "
        "przewody do czterech lutowanych wiązek wtrysku 5264-3P.",
        WARM))

    s.append(callout(
        "Rola Bus Servo Adapter (A)",
        "Adapter jest konwerterem USB-UART dla półdupleksowej magistrali TTL "
        "serw ST3215. Raspberry Pi wylicza ruch i przez adapter wysyła polecenia "
        "do serw oznaczonych unikalnymi ID; tą samą magistralą odbiera ich "
        "pozycję, prędkość, obciążenie i napięcie. Adapter działa tak samo z "
        "Pi 4B i Pi 5, ale nie jest głównym rozdzielaczem prądu napędu. Jego tor "
        "zasilania ma limit 5 A, więc pakiet 3S zasila cztery osobno zabezpieczone "
        "gałęzie nóg przez wysokoprądowy rozdzielacz i wspólną masę.<br/><br/>"
        "Źródła: docs.waveshare.com/Bus_Servo_Adapter_A/FAQ oraz "
        "raspberrypi.com/documentation/computers/getting-started.html.",
        ACCENT))

    s.append(callout(
        "Pakiet bazowy: 3S 2200 mAh",
        "Napięcie 11,1 V nominalnie i 12,6 V po naładowaniu pasuje bezpośrednio "
        "do ST3215. Wybieramy markowy pakiet min. 30C z XT60 i projektujemy "
        "regulowaną kieszeń także pod 3000 mAh. Dwa lekkie pakiety 2200 mAh "
        "wymieniane kolejno są lepsze niż wożenie jednego ciężkiego 5000 mAh. "
        "Pakiet musi mieć balanser, bezpiecznik i kontrolę rozładowania.",
        WARM))

    # ------------------------------------------------------------ noc
    s.append(para("Widzenie w ciemności", H1))
    s.append(para(
        "Kamera jest w wersji <b>NoIR</b>. Nazwa myli: nie znaczy „bez "
        "podczerwieni”, tylko <i>no IR filter</i> — bez filtra, który w "
        "zwykłej kamerze podczerwień <b>odcina</b>. Wersja NoIR podczerwień "
        "więc <b>widzi</b>, a doświetlona diodą IR pokazuje ciemny pokój tak, "
        "jakby był oświetlony. Kot dostaje nocny wzrok, a przy okazji "
        "świecące oczy — dosłownie, bo dioda 850 nm daje słaby czerwony "
        "poblask.", Body))
    s.append(para(
        "Kamerą jest tylko jedno oko. Drugi oczodół nie marnuje się: siedzi w "
        "nim <b>doświetlacz</b>. Moduły są sprzedawane <b>parą</b>, bo "
        "normalnie flankują obiektyw kamery CCTV z obu stron — tutaj oczodoły "
        "są dwa i jeden zajmuje kamera, więc <b>drugi doświetlacz zostaje "
        "zapasem</b>. Pole widzenia 120° obejmuje niemal wszystko przed kotem "
        "bez obracania głowy.", Body))

    s.append(callout(
        "Dioda musi być 850 nm, nie 940 nm",
        "Czujnik odległości VL53L5CX pracuje <b>na 940 nm</b>. Doświetlacz "
        "940 nm świeciłby prosto w jego pasmo, podnosząc mu tło i skracając "
        "zasięg — dwa elementy tego samego zestawu przeszkadzałyby sobie "
        "nawzajem. 850 nm leży obok, a ToF ma filtr wąskopasmowy, więc się "
        "mijają. Wybrany moduł ma <b>100° rozsyłu</b> pod kamerę 120° i "
        "fotorezystor z progiem, czyli zapala się sam po zmroku.",
        ACCENT))

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Czym się płaci i jak się z tego wycofać",
        "Brak filtra psuje <b>kolory w dzień</b> — obraz robi się różowawy, bo "
        "podczerwień z otoczenia zanieczyszcza kanały RGB. Do omijania "
        "przeszkód, rozpoznawania obiektów i podglądu to bez znaczenia, do "
        "ładnych zdjęć — tak.<br/><br/>"
        "Wyjście awaryjne jest tanie: <b>wersja NoIR i zwykła mają identyczną "
        "płytkę</b> (25 × 24 × 12,4 mm, to samo złącze, ten sam sensor "
        "IMX708), więc zamiana to wyjęcie jednej i włożenie drugiej. Obudowy "
        "ani kodu się nie rusza. Warunek: obudowę projektować pod wariant "
        "<b>Wide</b> — wersja nie-szerokokątna jest o 0,9 mm płytsza.",
        MUTED))

    s.append(callout(
        "Dlaczego czujnik ToF, a nie sama kamera",
        "Omijanie przeszkód <b>nie wymaga wcale kamery</b>. VL53L5CX zwraca "
        "mapę odległości 8×8 stref do 4 m — to wystarcza, żeby robot nie "
        "wchodził w ściany, i działa bez rozpoznawania obrazu, bez uczenia "
        "maszynowego i bez obciążania procesora. Za 70 zł to najtańsza "
        "funkcja w całym zestawie, i jedyna warstwa bezpieczeństwa, która "
        "działa nawet wtedy, gdy widzenie się pomyli.",
        ACCENT))

    # -------------------------------------------------- czego nie ma
    s.append(para("Czego świadomie nie ma na liście", H1))
    s.append(para(
        "Kilku rzeczy brakuje nie przez przeoczenie, tylko dlatego, że coś "
        "innego już je załatwia albo należą do późniejszej rozbudowy.", Body))

    s.append(table(
        ["Element", "Dlaczego nie"],
        [
            [Paragraph("<b>Czujniki nacisku w łapach</b>", CellB),
             "Serwa ST3215 raportują przez magistralę <b>pozycję, obciążenie, "
             "prędkość i napięcie</b>. Obciążenie na przegubie mówi, kiedy "
             "łapa dotknęła podłoża — czyli mamy czujnik siły w każdej nodze "
             "bez dokładania czegokolwiek. Osobne czujniki FSR wymagałyby "
             "przetwornika analogowo-cyfrowego, bo Raspberry Pi nie ma wejść "
             "analogowych: cztery czujniki plus MCP3008 to ok. 120 zł i "
             "kolejny układ do okablowania"],
            ["LiDAR",
             "skanuje jedną płaszczyznę na stałej wysokości, a korpus kota "
             "buja się w pionie podczas chodu — zła geometria dla czworonoga, "
             "do tego ciężki i drogi w tej skali"],
            ["Głębia stereo z dwóch oczu",
             "wymagałaby synchronizacji dwóch modułów i własnej kalibracji na "
             "maszynie, która trzęsie się przy każdym kroku; VL53L5CX daje tę "
             "samą informację prościej, a drugie oko jest zajęte przez "
             "doświetlacz. Pi 5 ma dwa złącza CSI, więc opcja zostaje otwarta"],
            ["Stacja dokująca",
             "czworonóg musi trafić stopami w styki z dokładnością chodu, "
             "który sam ma dryf — trudniejszy problem sterowania niż samo "
             "dokowanie. Po tym, jak chodzenie będzie solidne"],
        ],
        [40 * mm, 118 * mm]))

    s.append(para("Zanim klikniesz „zamawiam”", H2))
    s.append(table(
        ["", "Do sprawdzenia"],
        [
            ["1", "Pakiet: 3S 2200 mAh, 11,1 V, min. 30C, XT60. Sprawdzić "
                  "rzeczywiste wymiary konkretnego modelu przed CAD-em kieszeni"],
            ["2", "Botland: PLL-02580, KAB-06897, KAB-05473, JUS-22264, "
                  "KAB-07515 i NSZ-05375. "
                  "Oddzielnie dobrać główny wyłącznik z bezpiecznikiem 30 A oraz "
                  "cztery wiązki wtrysku zasilania 5264-3P"],
            ["3", "Pozycje oznaczone „szac.” nie były sprawdzone w "
                  "sklepie, tylko oszacowane. Reszta pochodzi ze stron ofert, "
                  "ale ceny się zmieniają — otworzyć każdy link ponownie"],
            ["4", "Instalujemy Raspberry Pi OS 64-bit na Pi 4B i zachowujemy go "
                  "po zmianie na Pi 5. Kamera wymaga Raspberry Pi OS, nie Ubuntu: obsługa czujnika "
                  "IMX708 jest tam od ręki, na Ubuntu trzeba budować libcamera "
                  "ze źródeł"],
            ["5", "Po wymianie Pi 4B na Pi 5 kamera wymaga kabla CSI 22↔15, a "
                  "AI HAT+ wymaga chłodzenia i miejsca nad płytką"],
            ["6", "Doświetlacz ma 3 W przy 3,3 V, czyli ok. 0,9 A na sztukę. "
                  "<b>Nie zasilać go z pinu 3,3 V Raspberry Pi</b> — ten daje "
                  "kilkadziesiąt miliamperów. Ciągnąć z przetwornicy, przez "
                  "własny stabilizator lub rezystor"],
        ],
        [10 * mm, 148 * mm],
        aligns={0: "CENTER"}))

    s.append(para("Co lutujemy, a co nie", H1))
    s.append(table(
        ["Element", "Sposób montażu"],
        [
            ["Pololu D24V90F5", "Lutujemy dwa dołączone zaciski ARK do płytki. Przewody przykręcamy, nie lutujemy na stałe."],
            ["4 pary XT30U", "Lutujemy przewody do obu połówek złączy, izolujemy każdy styk i mocujemy wiązkę przeciw zginaniu przy lucie."],
            ["Rozgałęzienia wiązek nóg", "Lutujemy przewód-przewód i doprowadzenia do gotowych przewodów 5264-3P. Nie lutujemy do serw ani samych styków 5264."],
            ["Czujniki i moduł audio", "Wlutowujemy goldpiny/ARK, gdy płytka ma je luzem. Fabrycznych złączy nie ruszamy. Przewody pozostają odłączane."],
            ["XT60 i LiPo", "Bez lutowania: gotowy przewód KAB-07515 i fabryczne złącze pakietu. Nie przerabiamy przewodów baterii."],
            ["Listwa, oprawki, wyłącznik", "Bez lutowania: końcówki zaciskane i śruby. Wyłącznik dobieramy ze śrubami lub konektorami, z właściwą obciążalnością DC."],
            ["Druga przetwornica 5 V", "Wybieramy wersję z fabrycznie zamontowanymi zaciskami śrubowymi."],
            ["Pi, HAT, kamera, USB, Grove, mikroserwa", "Gotowe przewody i złącza. Niczego nie lutujemy do Raspberry Pi."],
            ["Głośnik i doświetlacz", "Wersje z przewodem lub złączem. Ewentualne przedłużenie lutujemy w wiązce, nie na elemencie."],
        ], [52 * mm, 106 * mm]))
    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "<b>Ważne:</b> linek pod śrubami nie pobielamy cyną. Używamy końcówek "
        "dobranych do zacisku i przewodu oraz właściwej zaciskarki. Rozgałęzienia "
        "mocujemy poza miejscami zginania. Nie prowadzimy prądu trzech serw przez "
        "jeden cienki przewód 5264; zasilanie doprowadzamy z wiązki do każdego serwa. "
        "Pinout sprawdzamy z dokumentacją, nie tylko kolorem przewodów. "
        "Źródło montażu ARK: "
        '<link href="https://www.pololu.com/product/2866" color="#167d9a">Pololu D24V90F5</link>.', Body))
    s.append(para("Czym to polutować", H2))
    s.append(para(
        "Jeżeli nie masz jeszcze stanowiska, poniższy zestaw warsztatowy jest "
        "służy do przetwornicy, XT30U i wiązek. To zakup jednorazowy i "
        "nie jest wliczony w koszt robota. Poza nim potrzebne są ściągacz izolacji, "
        "zaciskarka do wybranych końcówek, multimetr i gorące powietrze. "
        "Końcówki, zaciskarka oraz brakujące przewody nadal wymagają wyceny.", Body))
    s.append(table(
        ["Botland", "Zastosowanie", "Koszt"],
        [
            ["LUT-06271 — Zhaoxin 936DH 75 W", "stacja z regulacją temperatury", "189,90"],
            ["LUT-09601 — zestaw grotów 900M", "dłuto dobrane do pola, zwykle 2-3 mm", "29,90"],
            ["NSZ-03249 — Cynel LC60 1,0 mm", "cyna Sn60Pb40 z topnikiem", "65,90"],
            ["TRP-16727 — topnik RMA w żelu", "zwilżanie grubych przewodów i pól", "22,90"],
            [Paragraph("<b>RAZEM, JEŚLI NICZEGO NIE MASZ</b>", CellB), "",
             Paragraph(f"<b>{WORKSHOP_TOTAL}</b>", CellB)],
        ],
        [68 * mm, 58 * mm, 32 * mm],
        aligns={2: "RIGHT"},
        highlight=[5]))
    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Ustawienia i bezpieczeństwo lutowania",
        "Sn60Pb40: zacznij od około 340-360°C i dopasowanego grota dłutowego. "
        "Nie zastępuj właściwego grota długim grzaniem. Dla połączeń lutowanych "
        "najpierw załóż termokurczkę, pobiel oba elementy, "
        "zlutuj i obkurcz gorącym powietrzem. Pakiet LiPo musi być odłączony. "
        "Nie używaj otwartego płomienia przy akumulatorze; zapewnij wentylację, "
        "nie jedz przy stanowisku i po pracy umyj ręce.",
        WARM))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/plan-zakupowy.pdf")
