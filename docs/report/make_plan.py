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

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Cal", rf"{F}\calibri.ttf"))
pdfmetrics.registerFont(TTFont("Cal-B", rf"{F}\calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Cal-I", rf"{F}\calibrii.ttf"))
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


BASE = [
    ("12 × Waveshare ST3215 + adapter magistrali", "napęd nóg", "1327,90"),
    ("BNO085 — 9-DoF IMU", "równowaga, kurs", "135,00"),
    ("3 × mikroserwo + Grove PCA9685", "głowa 2 osie, ogon", "138,60"),
    ("TTP223 + MAX98357A + głośnik YD36", "głaskanie, miauczenie", "47,70"),
    ("Pololu D24V50F5 + LiPo 3S 2200 + ładowarka B6AC", "zasilanie", "449,00"),
    ("PETG czarny 1 kg + microSD 16 GB", "obudowa, system", "119,90"),
]


def money_rows(items, total_label, total, tone=GOOD):
    rows = [[a, b, Paragraph(c, Cell)] for a, b, c in items]
    rows.append([Paragraph(f"<b>{total_label}</b>", CellB), "",
                 Paragraph(f'<b><font color="{tone.hexval()}">{total}</font></b>', CellB)])
    return rows


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
    s.append(para("Plan zakupowy — dwie wersje i decyzja",
                  st("s2", fontName="Cal-B", fontSize=13.5, leading=17,
                     textColor=INK, spaceBefore=2)))
    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Wersja A buduje chodzącego kota bez wzroku. Wersja B dokłada kamerę "
        "i czujnik odległości. Obie mieszczą się w budżecie 2500 zł, bo "
        "Raspberry Pi 4B jest już w domu i nie trzeba go kupować.", Sub))
    s.append(Spacer(1, 5 * mm))

    s.append(callout(
        "Decyzja: wersja B — 2451 zł",
        "Kamerę <b>kupić teraz, używać później</b>. To dwie różne rzeczy. "
        "Kupno teraz, bo wersja standardowa ma dostawę dopiero pod koniec "
        "października, a szerokokątna jest na stanie — odkładanie zakupu grozi "
        "tym, że blokada wróci wtedy, gdy będzie zatrzymywać gotowy projekt. "
        "Używanie później, bo debugowanie chodu i wizji naraz jest trudniejsze "
        "niż po kolei — i to jest realny koszt, nie te 233 zł.",
        GOOD))
    s.append(Spacer(1, 5 * mm))

    # ------------------------------------------------------------ kamera
    s.append(para("Dostępność kamery przesądza wybór modelu", H1))
    s.append(para(
        "Plan zakładał kamerę Camera Module 3 w wersji standardowej. Ta jest "
        "obecnie niedostępna — sklep podaje oczekiwaną dostawę na okolice "
        "23 października. Wersja szerokokątna jest na stanie z wysyłką w 24 h.", Body))

    s.append(table(
        ["Wariant", "Pole widzenia", "Cena", "Dostępność"],
        [
            ["Camera Module 3 standard", "76°", "~116 zł",
             Paragraph('<font color="#b3541e">ok. 23.10.2026</font>', Cell)],
            [Paragraph("<b>Camera Module 3 Wide</b>", CellB),
             Paragraph("<b>120°</b>", CellB),
             Paragraph("<b>~163 zł</b>", CellB),
             Paragraph('<b><font color="#1c6b45">wysyłka 24 h</font></b>', CellB)],
        ],
        [56 * mm, 30 * mm, 28 * mm, 44 * mm],
        aligns={1: "CENTER", 2: "CENTER", 3: "CENTER"},
        highlight=[2]))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Różnica 47 zł kupuje przy okazji <b>szersze pole widzenia</b>, co dla "
        "robota rozglądającego się po mieszkaniu jest zaletą, nie kompromisem: "
        "120° obejmuje niemal wszystko przed kotem bez obracania głowy. Wybór "
        "wersji Wide to więc nie ustępstwo wobec braku towaru — to lepszy "
        "wariant, który akurat jest dostępny.", Body))

    # ------------------------------------------------------------ wersja A
    s.append(para("Wersja A — bez wizji", H1))
    s.append(table(
        ["Pozycja", "Rola", "Koszt"],
        money_rows(BASE, "RAZEM", "2218,10 zł"),
        [82 * mm, 44 * mm, 32 * mm],
        aligns={2: "RIGHT"},
        highlight=[len(BASE) + 1]))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "<b>Umie:</b> chodzić i skręcać na czterech łapach, ruszać głową w "
        "dwóch osiach i ogonem, reagować na głaskanie, miauczeć, wiedzieć że "
        "się przechyla, łączyć się przez Wi-Fi i Bluetooth (pad PS4).", Body))
    s.append(para(
        "<b>Nie umie:</b> widzieć, omijać przeszkód, podchodzić do człowieka.", Body))

    # ------------------------------------------------------------ wersja B
    s.append(para("Wersja B — z wizją", H1))
    s.append(table(
        ["Pozycja", "Rola", "Koszt"],
        money_rows(
            [("Wszystko z wersji A", "chód, dotyk, dźwięk, IMU", "2218,10"),
             ("Camera Module 3 Wide 120°", "wzrok, podgląd w aplikacji", "~163,00"),
             ("VL53L5CX — ToF 8×8, zasięg 4 m", "omijanie przeszkód", "69,90")],
            "RAZEM", "≈ 2451,00 zł"),
        [82 * mm, 44 * mm, 32 * mm],
        aligns={2: "RIGHT"},
        highlight=[4]))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "<b>Dochodzi:</b> podgląd obrazu na żywo, świecące oczy z kamerą jak w "
        "briefie, reaktywne omijanie przeszkód, fundament pod wykrywanie "
        "człowieka i tryb „chodź za mną”.", Body))

    s.append(callout(
        "Dlaczego czujnik ToF, a nie sama kamera",
        "Pierwszy krok autonomii <b>nie wymaga wcale kamery</b>. VL53L5CX "
        "zwraca mapę odległości 8×8 stref do 4 m — to wystarcza, żeby robot "
        "omijał przeszkody, i działa bez rozpoznawania obrazu, bez uczenia "
        "maszynowego i bez obciążania procesora. Za 70 zł to najtańsza "
        "funkcja w całym zestawie.",
        ACCENT))

    # ------------------------------------------------------------ decyzja
    s.append(para("Uzasadnienie decyzji", H1))

    s.append(para("Co przemawia za kupnem teraz", H2))
    s.append(table(
        ["Argument", "Liczba"],
        [
            ["Kamera nie zmienia analizy mechanicznej", "waży 4 g"],
            ["Mieści się w pierwotnym budżecie", "2451 zł z 2500 zł"],
            ["Raspberry Pi z domu finansuje wizję", "oszczędność 268 zł"],
            ["Wersja standardowa wraca dopiero jesienią", "ok. 2 miesiące"],
        ],
        [110 * mm, 48 * mm],
        aligns={1: "CENTER"}))

    s.append(para("Co przemawia za używaniem dopiero później", H2))
    s.append(para(
        "Pierwsza iteracja ma zweryfikować mechanikę, okablowanie i chód. "
        "Prawdziwym kosztem wizji nie są pieniądze ani masa, tylko "
        "<b>uwaga</b>: szukanie przyczyny, gdy robot kuleje i jednocześnie nie "
        "widzi, jest trudniejsze niż rozwiązanie tych spraw po kolei. Kamera "
        "może poczekać w pudełku, aż kot będzie pewnie chodził.", Body))

    s.append(callout(
        "Co się właśnie zmieniło na korzyść wizji",
        "Dotąd wizja czekała także z powodu technicznego: <b>Gazebo nie "
        "uruchamia kamer na macOS</b> — Cocoa wymaga tworzenia okna "
        "renderującego w głównym wątku (gz-sim#960). Ale środowisko "
        "kontenerowe zbudowane dla Windowsa to Linux z dostępem do GPU, gdzie "
        "kamery działają. Oczy w modelu są już posadzone tam, gdzie siedziałaby "
        "para stereo — była to świadoma decyzja podjęta z myślą właśnie o tym "
        "momencie.<br/><br/>"
        "Oznacza to, że <b>oprogramowanie wizyjne można rozwijać w symulacji, "
        "zanim kamera dojedzie</b>, nie zabierając uwagi budowie mechaniki. "
        "Zastrzeżenie: renderowanie kamer w tym kontenerze nie zostało jeszcze "
        "sprawdzone pomiarem — to jedyny punkt tego dokumentu oparty na "
        "przesłance, a nie na teście.",
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
             "wymagałaby synchronizacji dwóch modułów i własnej kalibracji; "
             "VL53L5CX daje tę samą informację prościej"],
            ["Akcelerator AI (Hailo-8L)",
             "wymaga Raspberry Pi 5, a w tej wersji jest Pi 4B. Do podglądu "
             "obrazu i omijania przeszkód niepotrzebny"],
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
            ["1", "Pakiet LiPo 3S 2200 mAh był oznaczony jako chwilowo "
                  "niedostępny — potwierdzić stan lub wybrać zamiennik o tych "
                  "samych parametrach (11,1 V, min. 25C)"],
            ["2", "Ceny i dostępność potrafią się zmienić — otworzyć każdy link "
                  "ponownie przed płatnością"],
            ["3", "Kamera wymaga Raspberry Pi OS, nie Ubuntu: obsługa czujnika "
                  "IMX708 jest tam od ręki, na Ubuntu trzeba budować libcamera "
                  "ze źródeł"],
            ["4", "Wersja Wide ma inny obiektyw — jeśli obudowa oczu jest już "
                  "projektowana, sprawdzić wymiary montażowe"],
        ],
        [10 * mm, 148 * mm],
        aligns={0: "CENTER"}))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/plan-zakupowy.pdf")
