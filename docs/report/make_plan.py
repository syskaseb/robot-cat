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
        spaceBefore=16, spaceAfter=6)
H2 = st("H2", fontName="Cal-B", fontSize=11.5, leading=15, textColor=INK,
        spaceBefore=10, spaceAfter=4)
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
    canvas.drawRightString(184 * mm, 287.5 * mm, "sierpień 2026")
    canvas.line(26 * mm, 17 * mm, 184 * mm, 17 * mm)
    canvas.drawString(26 * mm, 12.5 * mm,
                      "Ceny orientacyjne — sprawdzić każdy link przed zapłatą")
    canvas.drawRightString(184 * mm, 12.5 * mm, f"{doc.page}")
    canvas.restoreState()


# Prices checked in August 2026. The ones marked "szac." below are the only
# estimates - everything else came off a shop page. Re-check every line before
# paying; this is a snapshot, not a quote.
PARTS = [
    ("NAPĘD", None, None),
    ("12 × Waveshare ST3215 + adapter magistrali", "napęd nóg", "1327,90"),
    ("CZUJNIKI I INTERAKCJA", None, None),
    ("BNO085 — 9-DoF IMU", "równowaga, kurs", "135,00"),
    ("VL53L5CX — ToF 8×8, zasięg 4 m", "omijanie przeszkód", "69,90"),
    ("3 × mikroserwo + Grove PCA9685", "głowa 2 osie, ogon", "138,60"),
    ("TTP223 + MAX98357A + głośnik YD36", "głaskanie, miauczenie", "47,70"),
    ("WZROK", None, None),
    ("Camera Module 3 NoIR Wide 120°", "wzrok, także po ciemku", "199,00"),
    ("2 × doświetlacz IR 850 nm 3 W", "drugie oko, nocny wzrok", "19,90"),
    ("Kabel CSI 22-pin ↔ 15-pin", "Pi 5 ma węższe złącze — szac.", "19,90"),
    ("KOMPUTER", None, None),
    ("Raspberry Pi 5 8 GB", "sterowanie i wizja", "829,90"),
    ("AI HAT+ 13 TOPS (Hailo-8L)", "rozpoznawanie obrazu", "329,00"),
    ("Active Cooler do Pi 5", "chłodzenie — szac.", "29,90"),
    ("microSD 64 GB", "system i modele — szac.", "49,00"),
    ("ZASILANIE", None, None),
    ("Pololu D24V50F5 + LiPo 3S 2200 + ładowarka B6AC", "zasilanie", "449,00"),
    ("Druga przetwornica 5 V / 3 A", "gałąź serw i audio — szac.", "49,00"),
    ("OBUDOWA", None, None),
    ("PETG czarny 1 kg", "wydruk", "94,90"),
]

TOTAL = "3788,60 zł"


def parts_rows():
    """Group headers are rows with no price; they render as a band."""
    rows, bands = [], []
    for i, (name, role, cost) in enumerate(PARTS, start=1):
        if cost is None:
            rows.append([Paragraph(f"<b>{name}</b>", CellB), "", ""])
            bands.append(len(rows))
        else:
            rows.append([name, role, Paragraph(cost, Cell)])
    rows.append([Paragraph("<b>RAZEM</b>", CellB), "",
                 Paragraph(f'<b><font color="{ACCENT.hexval()}">{TOTAL}</font></b>',
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
        "Wszystko, co trzeba kupić, żeby kot chodził, widział — także po "
        "ciemku — i rozpoznawał, co widzi. Ta lista nie obejmuje drobnicy "
        "montażowej: kabli, śrub, wkładek i narzędzi. Te są w "
        "<b>montaz.pdf</b>, rozdział 1, i dokładają rzędu 250–400 zł.", Sub))
    s.append(Spacer(1, 5 * mm))

    s.append(callout(
        f"Razem: {TOTAL}",
        "Budżet wyjściowy wynosił 2500 zł i zakładał, że komputerem będzie "
        "Raspberry Pi 4B leżące już w domu. <b>Ta lista go przekracza o "
        "1289 zł</b>, i cała różnica siedzi w jednej decyzji: Pi 5 z "
        "akceleratorem AI zamiast Pi 4B. Powód jest w następnym rozdziale — "
        "krótko, Pi 4B nie ma złącza PCIe, więc rozpoznawanie obrazu jest z "
        "nim nie tyle wolniejsze, co niemożliwe.<br/><br/>"
        "Reszta listy mieści się w pierwotnym założeniu. Jeśli budżet ma "
        "zostać dotrzymany, jedynym miejscem, gdzie da się go szukać, jest "
        "właśnie komputer — nie serwa i nie czujniki.",
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
        "<b>Umie:</b> chodzić i skręcać na czterech łapach, ruszać głową w "
        "dwóch osiach i ogonem, reagować na głaskanie, miauczeć, wiedzieć że "
        "się przechyla, omijać przeszkody, patrzeć — także w ciemności — "
        "rozpoznawać obiekty w czasie rzeczywistym i łączyć się przez Wi-Fi "
        "oraz Bluetooth (pad PS4).", Body))

    # -------------------------------------------------------- komputer
    s.append(para("Komputer: Raspberry Pi 5 z akceleratorem", H1))
    s.append(para(
        "Rozpoznawanie obrazu na samym procesorze Pi zjada całą moc "
        "obliczeniową i nic nie zostaje na chód ani na resztę węzłów ROS. "
        "Akcelerator przenosi sieć neuronową na osobny układ, gdzie widzenie "
        "działa praktycznie za darmo w tle.", Body))

    s.append(table(
        ["YOLOv8n, 640×640", "Klatek na sekundę"],
        [
            ["Samo CPU Pi 5", "~12"],
            [Paragraph("<b>Pi 5 + AI HAT+ (Hailo-8L)</b>", CellB),
             Paragraph('<b><font color="#1c6b45">~137</font></b>', CellB)],
        ],
        [110 * mm, 48 * mm],
        aligns={1: "CENTER"},
        highlight=[2]))

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Dlaczego nie Pi 4B, skoro leży w domu",
        "<b>Pi 4B nie ma złącza PCIe.</b> Akcelerator Hailo wpina się wyłącznie "
        "w PCIe, więc z Pi 4B jest nie „wolniejszy”, tylko fizycznie "
        "niemożliwy — nie ma przejściówki, która by to obeszła. Wybór jest "
        "binarny: albo Pi 5 i rozpoznawanie obrazu, albo Pi 4B i wzrok "
        "ograniczony do podglądu plus omijanie przeszkód z czujnika ToF.<br/><br/>"
        "Przy okazji Pi 5 ma <b>dwa złącza CSI</b> zamiast jednego, więc para "
        "stereo pozostaje otwarta na przyszłość. Nie jest potrzebna: głębię "
        "daje VL53L5CX, a drugie oko zajmuje doświetlacz.",
        ACCENT))

    s.append(para(
        "Wersja 13 TOPS wystarcza z dużym zapasem — jedna kamera przy "
        "prędkości 10 cm/s nie zbliża się do tego pułapu. Mocniejsza 26 TOPS "
        "kosztuje ok. 230 zł więcej i nie ma tu czego przyspieszyć.", Body))

    s.append(callout(
        "Trzy rzeczy, które Pi 5 dokłada poza swoją ceną",
        "<b>Chłodzenie.</b> Pi 5 grzeje się bardziej niż 4B i pod HAT-em nie "
        "ma jak oddać ciepła samo — Active Cooler nie jest opcjonalny.<br/>"
        "<b>Inny kabel do kamery.</b> Camera Module 3 przychodzi z kablem "
        "15-pinowym pod Pi 4B; Pi 5 ma węższe złącze 22-pinowe. Bez "
        "przejściówki kamery nie da się podłączyć.<br/>"
        "<b>Prąd.</b> Pi 5 z akceleratorem potrafi wziąć blisko tyle, ile daje "
        "cała przetwornica D24V50F5 — dlatego na liście jest druga, patrz "
        "rozdział o zasilaniu w montaz.pdf.",
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
        "nim <b>doświetlacz</b>. Pole widzenia 120° obejmuje niemal wszystko "
        "przed kotem bez obracania głowy.", Body))

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
        "innego już je załatwia albo należą do późniejszego etapu.", Body))

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

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Kiedy czujniki w łapach zaczną mieć sens",
        "Gdy chód przestanie być sterowany wyłącznie pozycyjnie. Pomiary "
        "pokazały, że przy takim sterowaniu nogi <b>napierają na podłoże</b>, "
        "bo ciało nie porusza się dokładnie tak, jak zakłada plan — i to "
        "zjawisko odpowiada za większość obciążenia przegubów podczas chodu. "
        "Lekarstwem jest sprzężenie zwrotne, a pierwszym jego źródłem jest "
        "IMU, które <b>jest już w koszyku</b>. Dopiero gdyby to nie "
        "wystarczyło — na przykład przy chodzeniu po nierównym terenie — "
        "dedykowany czujnik w łapie byłby następnym krokiem.",
        MUTED))

    s.append(para("Zanim klikniesz „zamawiam”", H2))
    s.append(table(
        ["", "Do sprawdzenia"],
        [
            ["1", "Pakiet LiPo 3S 2200 mAh bywał oznaczany jako chwilowo "
                  "niedostępny — potwierdzić stan lub wybrać zamiennik o tych "
                  "samych parametrach (11,1 V, min. 25C)"],
            ["2", "Cztery pozycje oznaczone „szac.” nie były sprawdzone w "
                  "sklepie, tylko oszacowane. Reszta pochodzi ze stron ofert, "
                  "ale ceny się zmieniają — otworzyć każdy link ponownie"],
            ["3", "Kamera wymaga Raspberry Pi OS, nie Ubuntu: obsługa czujnika "
                  "IMX708 jest tam od ręki, na Ubuntu trzeba budować libcamera "
                  "ze źródeł"],
            ["4", "<b>Sprawdzić, co jest w pudełku z AI HAT+</b> — dystanse i "
                  "taśma PCIe zwykle są w zestawie, więc nie trzeba ich "
                  "dokupywać osobno"],
            ["5", "Kabel CSI kupić <b>razem z kamerą</b>. Bez niego kamera nie "
                  "wepnie się w Pi 5, a to najłatwiejsza pozycja do przeoczenia "
                  "na całej liście"],
            ["6", "Doświetlacz ma 3 W przy 3,3 V, czyli ok. 0,9 A na sztukę. "
                  "<b>Nie zasilać go z pinu 3,3 V Raspberry Pi</b> — ten daje "
                  "kilkadziesiąt miliamperów. Ciągnąć z przetwornicy, przez "
                  "własny stabilizator lub rezystor"],
        ],
        [10 * mm, 148 * mm],
        aligns={0: "CENTER"}))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/plan-zakupowy.pdf")
