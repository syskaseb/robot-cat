#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Robot Cat - electronics notes: mounting, control architecture, perception,
compute, power and an honest read on gait smoothness.

Rebuild from the repo root:

    python docs/report/make_uzupelnienie.py docs/uzupelnienie-elektroniki.pdf
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

import os

_FONT_DIRS = [
    os.path.expanduser("~/Library/Fonts"),          # macOS, Homebrew --cask font-dejavu
    "/Library/Fonts",                                # macOS, system-wide
    "/usr/share/fonts/truetype/dejavu",              # Debian/Ubuntu, apt fonts-dejavu-core
    "/usr/share/fonts/dejavu",                        # Fedora/RHEL
]


def _mpl_font_dir():
    try:
        import matplotlib
    except ImportError:
        return None
    return os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")


def _font(filename):
    """Locate one DejaVu face.

    Each face is resolved on its own rather than picking a directory from
    DejaVuSans.ttf and assuming the rest are beside it: Debian's
    fonts-dejavu-core ships the regular and bold weights but not the oblique,
    so that assumption crashes on a stock Ubuntu. matplotlib bundles the full
    set, which is the fallback - and the reason this works in the pixi env
    without installing anything.
    """
    for directory in [*_FONT_DIRS, _mpl_font_dir()]:
        if directory and os.path.exists(os.path.join(directory, filename)):
            return os.path.join(directory, filename)
    sys.exit(
        f"{filename} not found - DejaVu Sans is needed for Polish diacritics, "
        "which reportlab's built-in Helvetica cannot render (they come out as "
        "black boxes).\nInstall it:\n"
        "  brew install --cask font-dejavu          # macOS\n"
        "  apt install fonts-dejavu-core            # Debian/Ubuntu\n"
        "or run this from the ROS pixi env, which bundles it via matplotlib."
    )


pdfmetrics.registerFont(TTFont("DejaVu", _font("DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", _font("DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", _font("DejaVuSans-Oblique.ttf")))

TEAL = colors.HexColor("#1B4B5A")
TEAL_TABLE = colors.HexColor("#1F5C6E")
ORANGE = colors.HexColor("#C8681A")
LIGHT = colors.HexColor("#F2EFEA")
ROW_ALT = colors.HexColor("#F7F7F7")
INK = colors.HexColor("#222222")

DOC_TITLE = "Robot Cat — uzupełnienie elektroniki"
DOC_DATE = "sierpień 2026"
FOOTER_NOTE = "Uzupełnia napedy-v4.pdf, plan-zakupowy.pdf i montaz.pdf — nie zastępuje ich"


# ---------- styles ----------

styles = {}
styles["Title"] = ParagraphStyle(
    "Title", fontName="DejaVu-Bold", fontSize=26, leading=30, textColor=TEAL,
    spaceAfter=4,
)
styles["Subtitle"] = ParagraphStyle(
    "Subtitle", fontName="DejaVu-Bold", fontSize=13.5, leading=17, textColor=INK,
    spaceAfter=10,
)
styles["Body"] = ParagraphStyle(
    "Body", fontName="DejaVu", fontSize=10, leading=14.5, textColor=INK,
    spaceAfter=8,
)
styles["H1"] = ParagraphStyle(
    "H1", fontName="DejaVu-Bold", fontSize=15, leading=19, textColor=TEAL,
    spaceBefore=14, spaceAfter=8,
)
styles["H2"] = ParagraphStyle(
    "H2", fontName="DejaVu-Bold", fontSize=11.5, leading=15, textColor=TEAL,
    spaceBefore=8, spaceAfter=6,
)
styles["CalloutTitle"] = ParagraphStyle(
    "CalloutTitle", fontName="DejaVu-Bold", fontSize=10.5, leading=14,
    textColor=INK, spaceAfter=3,
)
styles["CalloutBody"] = ParagraphStyle(
    "CalloutBody", fontName="DejaVu", fontSize=10, leading=14, textColor=INK,
)
styles["TableHead"] = ParagraphStyle(
    "TableHead", fontName="DejaVu-Bold", fontSize=9, leading=12,
    textColor=colors.white,
)
styles["TableCell"] = ParagraphStyle(
    "TableCell", fontName="DejaVu", fontSize=9, leading=12.5, textColor=INK,
)
styles["TableCellBold"] = ParagraphStyle(
    "TableCellBold", fontName="DejaVu-Bold", fontSize=9, leading=12.5, textColor=INK,
)
styles["FootnoteRef"] = ParagraphStyle(
    "FootnoteRef", fontName="DejaVu-Oblique", fontSize=8.3, leading=11.5,
    textColor=colors.HexColor("#555555"), spaceBefore=4,
)


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def callout(title, body_html):
    inner = Table(
        [[p(title, "CalloutTitle")], [p(body_html, "CalloutBody")]],
        colWidths=[160 * mm],
    )
    inner.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, 0), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
            ]
        )
    )
    wrapper = Table([[inner]], colWidths=[168 * mm])
    wrapper.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return wrapper


def data_table(header, rows, col_widths, bold_row=None):
    body = [[p(h, "TableHead") for h in header]]
    for i, r in enumerate(rows):
        style = "TableCellBold" if bold_row is not None and i == bold_row else "TableCell"
        body.append([p(c, style) for c in r])
    t = Table(body, colWidths=col_widths, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_TABLE),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(body)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    if bold_row is not None:
        ts.append(("BACKGROUND", (0, bold_row + 1), (-1, bold_row + 1),
                    colors.HexColor("#FCEFDD")))
    t.setStyle(TableStyle(ts))
    return t


# ---------- page decoration ----------

def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(TEAL)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("DejaVu-Bold", 9.5)
    canvas.drawString(20 * mm, h - 9.5 * mm, DOC_TITLE)
    canvas.setFont("DejaVu", 9.5)
    canvas.drawRightString(w - 20 * mm, h - 9.5 * mm, DOC_DATE)

    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont("DejaVu", 8)
    canvas.drawString(20 * mm, 10 * mm, FOOTER_NOTE)
    canvas.drawRightString(w - 20 * mm, 10 * mm, str(doc.page))
    canvas.setStrokeColor(colors.HexColor("#DDDDDD"))
    canvas.line(20 * mm, 13 * mm, w - 20 * mm, 13 * mm)
    canvas.restoreState()


def build(path):
    doc = BaseDocTemplate(
        path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    story = []

    # ---------- Title block ----------
    story.append(p("Robot Cat", "Title"))
    story.append(p("Uzupełnienie: montaż, architektura, kompute, zasilanie", "Subtitle"))
    story.append(
        p(
            "Ten dokument <b>uzupełnia</b> napedy-v4.pdf, plan-zakupowy.pdf i montaz.pdf notatkami z "
            "rozmowy, które nie miały jeszcze gdzie trafić: dlaczego montaż napędów jest w stawie, nie "
            "w brzuchu; dlaczego kompute jest jeden centralny, nie per-noga; porównanie z napędami QDD; "
            "i uczciwa ocena płynności chodu. Sekcje 1-8 to skrót ustaleń opisanych szerzej w "
            "napedy-v4.pdf — zachowane dla ciągłości, nie duplikują decyzji."
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        callout(
            "Wniosek w jednym zdaniu",
            "Kot chodzi <b>0,14 m/s</b> i to jest sufit serw pozycyjnych klasy hobby, nie wynik "
            "słabego strojenia. Różnica między chodzeniem a bieganiem to nie kwestia wymiarów ani "
            "parametrów chodu, tylko wyłącznie klasy napędu.",
        )
    )
    story.append(Spacer(1, 6))

    # ---------- 1. Stan projektu ----------
    story.append(p("1. Stan projektu", "H1"))
    story.append(
        p(
            "Symulacja jest dopracowana i nie jest wąskim gardłem. Model ma proporcje "
            "prawdziwego kota, chód jest strojony pomiarowo, a cały stos ma pokrycie testami i CI."
        )
    )
    story.append(
        data_table(
            ["Parametr", "Wartość", "Uwaga"],
            [
                ["Stopnie swobody", "12 (4 nogi × 3)", "biodro 2 DOF + kolano"],
                ["Masa całkowita", "2,10 kg", "korpus 1,04 kg + nogi po 234 g"],
                ["Segment nogi", "0,11 + 0,11 m", "zasięg 0,22 m"],
                ["Wysokość w kłębie", "24,2 cm", "biodro 17,2 cm, rozstaw bioder 22 cm"],
                ["Sylwetka (kłąb / rozstaw)", "1,10", "kot ≈ 1,0 (kwadratowa)"],
                ["Prędkość w symulacji", "0,14 m/s", "na limitach ST3215"],
                ["Kołysanie boczne", "1,6°", "międzyszczytowo"],
                ["Dryf kursu", "≈0,9°/m", "chód otwarty, bez sprzężenia"],
                ["Testy", "581, CI zielone", "matematyka bez symulatora"],
            ],
            [55 * mm, 40 * mm, 73 * mm],
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("2. Symulacja ma limity kupionego serwa", "H1"))
    story.append(
        p(
            "Model deklaruje w każdym przegubie nóg moment <b>2,57 Nm</b> i prędkość "
            "<b>4,7 rad/s</b> — to karta katalogowa ST3215 przy najgorszym stanie pakietu, nie "
            "wartości dobrane tak, żeby chód wyglądał dobrze. Głowa i ogon dostają 0,20 Nm "
            "mikroserwa. Dzięki temu każda godzina strojenia chodu dotyczy robota, który da się "
            "zbudować."
        )
    )

    story.append(
        callout(
            "Uwaga: sam limit w modelu nie wystarczy",
            "Gazebo <b>nie egzekwuje</b> limitu prędkości przy sterowaniu pozycyjnym. Po ustawieniu "
            "limitu 3,5 rad/s przeguby i tak kręciły 10 rad/s. Wpisana wyżej wartość 4,7 rad/s "
            "dokumentuje więc napęd, ale nie chroni przed zadaniem mu czegoś niewykonalnego — "
            "uczciwy pomiar wymaga ograniczenia <i>samego generatora chodu</i>, dokładnie tak, jak "
            "zachowa się prawdziwy sterownik.",
        )
    )
    story.append(Spacer(1, 6))

    # ---------- 3. Co ogranicza predkosc ----------
    story.append(p("3. Co naprawdę ogranicza prędkość", "H1"))
    story.append(
        p(
            "Szczytowa prędkość przegubu w ustalonym chodzie, policzona dla siatki parametrów. "
            "Kolumna „limit” to prędkość, jaką chód może maksymalnie nadać ciału."
        )
    )
    story.append(
        data_table(
            ["Krok [m]", "Cykl [s]", "Limit [m/s]", "Szczyt [rad/s]", "Serwo ~4,8 rad/s"],
            [
                ["0,16", "0,30", "0,533", "24,6", "nie"],
                ["0,12", "0,40", "0,300", "14,8", "nie"],
                ["0,08", "0,50", "0,160", "9,8", "nie"],
                ["0,06", "0,50", "0,120", "9,1", "nie"],
                ["0,04", "0,60", "0,067", "7,2", "nie"],
            ],
            [28 * mm, 28 * mm, 30 * mm, 35 * mm, 47 * mm],
        )
    )
    story.append(
        callout(
            "Kluczowe odkrycie",
            "Nawet najwolniejszy chód z domyślnym wymachem żąda 7,2 rad/s — półtora raza więcej, "
            "niż serwo potrafi. O szczycie decyduje więc <b>unoszenie łapy</b>, a nie długość kroku. "
            "Skrócenie kroku samo z siebie nie pomaga; trzeba obniżyć wymach.",
        )
    )
    story.append(Spacer(1, 6))
    story.append(p("Chód wykonalny na serwach", "H2"))
    story.append(
        p(
            "Po dopuszczeniu wymachu jako trzeciego parametru znaleziono rozwiązania mieszczące się "
            "poniżej 3,4 rad/s — z zapasem na obciążenie, bo katalogowe 4,8 rad/s dotyczy biegu jałowego."
        )
    )
    story.append(
        data_table(
            ["Krok [m]", "Cykl [s]", "Wymach [m]", "Szczyt [rad/s]", "Limit [m/s]"],
            [
                ["0,06", "0,6", "0,012", "3,1", "0,100"],
                ["0,08", "0,8", "0,012", "2,8", "0,100"],
                ["0,08", "1,0", "0,012", "2,3", "0,080"],
            ],
            [28 * mm, 28 * mm, 30 * mm, 35 * mm, 47 * mm],
            bold_row=1,
        )
    )
    story.append(
        p(
            "Wiersz wyróżniony zmierzono następnie w pełnej symulacji: <b>0,143 m/s</b> osiągnięte "
            "(3,42 m w 24 s czasu symulacji).",
            "FootnoteRef",
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("4. Moment — druga granica", "H1"))
    story.append(
        p(
            "Momenty odczytane z interfejsu stanu, przy masie 2,10 kg. Pełne wyliczenie budżetu masy "
            "i doboru napędu jest w napedy-v4.pdf — tu tylko liczby, do których odwołują się dalsze "
            "sekcje."
        )
    )
    story.append(
        data_table(
            ["Stan", "Moment na przegub", "Uwaga"],
            [
                ["Leży", "0,09 Nm", "praktycznie bez obciążenia"],
                ["Stoi", "0,72 Nm", "obciążenie ciągłe"],
                ["Idzie 0,1 m/s — mediana", "0,18 Nm", "przez większość czasu"],
                ["Idzie 0,1 m/s — 95. pct", "1,93 Nm", "liczba do doboru napędu"],
            ],
            [50 * mm, 40 * mm, 78 * mm],
        )
    )

    story.append(
        callout(
            "Dlaczego 95. percentyl, a nie szczyt",
            "Chwilowe szczyty to <b>transjenty kontaktowe</b> — uderzenie łapy o podłoże, nie "
            "zapotrzebowanie ustalone. W prawdziwym robocie amortyzuje je podatność mechaniczna, "
            "czyli miękka nakładka łapy; dlatego montaz.pdf traktuje ją jako element nośny, a nie "
            "ozdobę. Liczbą do doboru napędu jest 95. percentyl: <b>1,93 Nm</b> wobec 2,57 Nm, jakie "
            "ST3215 daje na rozładowanym pakiecie.",
        )
    )
    story.append(Spacer(1, 6))

    # ---------- 5. Porownanie klas napedow (rozszerzona) ----------
    story.append(p("5. Porównanie klas napędów", "H1"))
    story.append(
        p(
            "Kolumna „kot w symulacji” to prędkość zmierzona po nałożeniu ograniczeń danej klasy — "
            "nie przeliczenie z karty katalogowej."
        )
    )
    story.append(
        data_table(
            ["", "ST3215 (wybrane)", "Feetech STS3250", "Dynamixel XM430", "CubeMars AK60-6"],
            [
                ["Prędkość", "~4,7 rad/s", "~7,9 rad/s", "~4,8 rad/s", "~30–60 rad/s"],
                ["Moment (utyk / ciągły)", "2,9 / ~0,7 Nm", "4,9 / ~2,45 Nm", "4,1 / ~1,3 Nm", "9 / 3 Nm"],
                ["Masa ×12", "0,66 kg", "0,89 kg", "1,0 kg", "4,4 kg"],
                ["Kot w symulacji", "0,14 m/s", "0,14 m/s", "0,14 m/s", "0,58–0,64 m/s"],
                ["Bieg (faza lotu)", "niemożliwy", "niemożliwy", "niemożliwy", "realny"],
                ["Koszt 12 szt.", "~1 tys. zł", "~1,5–2 tys. zł", "~12 tys. zł", "~6–7 tys. zł"],
                [
                    "Klasa odniesienia",
                    "SpotMicro, Pupper",
                    "SpotMicro, wersja o wyższym momencie",
                    "roboty badawcze",
                    "MIT Mini Cheetah",
                ],
            ],
            [38 * mm, 32.5 * mm, 32.5 * mm, 32.5 * mm, 32.5 * mm],
            bold_row=3,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        p(
            "Najważniejsze w tej tabeli: <b>Feetech i Dynamixel leżą w tej samej lidze prędkości</b>. "
            "Dynamixel kupuje niezawodność, moment i wsparcie — nie szybszego kota. Skok jakościowy "
            "pojawia się dopiero przy napędach bezszczotkowych quasi-direct-drive, i jest to skok o rząd "
            "wielkości."
        )
    )

    story.append(p("Decyzja: Feetech ST3215", "H2"))
    story.append(
        p(
            "Wymaganie to <b>1,93 Nm</b> w 95. percentylu przy masie 2,10 kg — pełne wyliczenie w "
            "napedy-v4.pdf. ST3215 daje 2,94 Nm utyku przy 12 V i 2,57 Nm przy rozładowanym pakiecie "
            "3S, czyli <b>33% zapasu w najgorszym punkcie</b>. Mocniejsze serwa z tej tabeli kupują "
            "zapas, którego nie ma czym wykorzystać: prędkość kota ogranicza nie moment, tylko "
            "quasi-statyczny charakter chodu."
        )
    )
    story.append(
        p(
            "Zastrzeżenie do sprawdzenia na sprzęcie: przy długo utrzymywanym, <b>unieruchomionym</b> "
            "obciążeniu zabezpieczenie termiczne serw tej klasy ścina moment. Dotyczy to stania w "
            "miejscu przez dłuższy czas oraz póz stretch/lie-down — nie samego chodu, gdzie 95. "
            "percentyl to krótkie, powtarzalne szczyty. Stąd tryb leżenia jest w projekcie także "
            "chłodzeniem: leżący kot obciąża przeguby momentem 0,09 Nm wobec 0,72 Nm w staniu."
        )
    )
    story.append(
        p(
            "Źródło: servodatabase.com oraz karta katalogowa Waveshare ST3215 (30 kg·cm przy 12 V).",
            "FootnoteRef",
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 6. Czy kot moze biegac ----------
    story.append(p("6. Czy ten kot może biegać?", "H1"))
    story.append(
        p(
            "Kryterium przejścia między chodami u zwierząt opisuje liczba Froude’a: kłus przechodzi "
            "w galop przy Fr ≈ 2,5, gdzie Fr = v² / (g · L), a L to długość nogi. Dla naszej nogi "
            "0,16 m daje to próg galopu:"
        )
    )
    story.append(
        p(
            "v = √(2,5 × 9,81 × 0,16) ≈ 2,0 m/s",
            "CalloutBody",
        )
    )
    story.append(
        p(
            "<b>Wymiary nie są przeszkodą</b> — 2,0 m/s to dokładnie tempo, w jakim galopują "
            "zwierzęta tej wielkości. Natura biega w tej skali bez trudu. Przeszkody są trzy i żadna "
            "nie dotyczy geometrii:"
        )
    )
    story.append(
        data_table(
            ["Przeszkoda", "Dlaczego", "Status"],
            [
                [
                    "Moc napędu",
                    "bieg wymaga fazy lotu, czyli impulsu większego niż ciężar — momentu i "
                    "prędkości jednocześnie",
                    "tylko QDD",
                ],
                [
                    "Sprzężenie zwrotne",
                    "lądowania nie da się wykonać na ślepo; potrzebny co najmniej IMU",
                    "do zrobienia",
                ],
                [
                    "Wzorzec chodu",
                    "galop to inne przesunięcia fazowe i kontrola pochylenia — czysta matematyka",
                    "w zasięgu dziś",
                ],
            ],
            [35 * mm, 100 * mm, 33 * mm],
        )
    )
    story.append(
        p(
            "Warto zauważyć: wzorzec galopu można prototypować w symulacji już teraz — podnosząc "
            "limity w modelu do klasy QDD — i mieć go gotowego, zanim takie silniki zostaną kupione."
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("Dlaczego nie od razu QDD?", "H2"))
    story.append(
        data_table(
            ["", "ST3215 (wybrane)", "CubeMars AK60-6 (QDD)"],
            [
                ["Koszt, 12 szt.", "~1,3 tys. zł", "~6-7 tys. zł (5×)"],
                ["Kot w symulacji", "0,14 m/s, chód", "0,58-0,64 m/s, bieg realny"],
                [
                    "Sterowanie",
                    "pozycyjne (docelowy kąt)",
                    "momentowe/impedancyjne (docelowa siła)",
                ],
                [
                    "Architektura",
                    "jeden Raspberry Pi, 100 Hz",
                    "wymaga pętli rzędu 1 kHz — realnie osobny "
                    "kontroler per noga, patrz sekcja 9",
                ],
            ],
            [40 * mm, 60 * mm, 68 * mm],
        )
    )
    story.append(
        p(
            "Różnica kosztu (3-4×) to najmniejszy powód. Większy: <b>QDD wymaga innej architektury "
            "sterowania</b>, nie tylko innych silników. Sterowanie momentem/impedancją potrzebuje pętli "
            "rzędu 1 kHz na przegub — jedno centralne Raspberry Pi tego nie udźwignie (patrz sekcja 9), "
            "więc realnie dochodzi sterownik per noga, co samo w sobie jest osobnym projektem "
            "elektroniki. Do tego bieg wymaga rzeczy, których jeszcze nie mamy: sprzężenia z lądowania "
            "(IMU + regulator, sekcja 10) i wzorca galopu (matematyka gotowa, niewdrożona)."
        )
    )
    story.append(
        p(
            "Skok na QDD teraz oznaczałby budowanie wszystkiego naraz — nowej mechaniki, nowego "
            "sterowania niskopoziomowego, nowego wzorca chodu — bez zweryfikowania żadnego z osobna. "
            "Tanie serwa pozwalają sprawdzić cały tor „symulacja → sprzęt” (mechanika, okablowanie, "
            "interfejs) tanim kosztem błędu: $15 serwo, nie $150+ silnik QDD, jeśli coś w montażu jest "
            "źle. <b>To nie jest droga bez wyjścia</b> — generator chodu, kinematyka i testy przenoszą "
            "się bez zmian na QDD później (sekcja 7); wymiana napędów to wymiana jednego bloku "
            "sprzętowego, nie przepisanie projektu od zera."
        )
    )
    story.append(Spacer(1, 6))

    # ---------- 7. Rekomendacja ----------
    story.append(p("7. Rekomendacja", "H1"))
    story.append(
        p(
            "Zbudować najpierw wersję na tanich serwach, traktując ją jako weryfikację całego toru "
            "„symulacja → sprzęt”: mechaniki, elektroniki, interfejsu sterowania i procesu strojenia. "
            "Kot będzie <i>chodził</i>, nie biegał — i to jest akceptowalny wynik pierwszej iteracji."
        )
    )
    story.append(
        p(
            "Kluczowy argument: <b>wymiana napędów nie unieważnia oprogramowania</b>. Architektura "
            "przewiduje podmianę samego bloku sprzętowego; generator chodu, kinematyka i testy przenoszą "
            "się bez zmian. Przejście na napędy bezszczotkowe to później wymiana silników i ponowne "
            "strojenie parametrów — procedura, którą już wykonaliśmy pomiarowo."
        )
    )
    story.append(p("Kolejne kroki", "H2"))
    story.append(
        data_table(
            ["", "Krok", "Po co"],
            [
                [
                    "1",
                    "Chód serwowy jako nazwany profil w repozytorium",
                    "gotowy punkt odniesienia dla realnego sprzętu",
                ],
                [
                    "2",
                    "✓ Rozstrzygnięte: Feetech ST3215, patrz sekcja 5",
                    "33% zapasu momentu przy masie 2,10 kg",
                ],
                [
                    "3",
                    "✓ Rozstrzygnięte: montaż w stawie, patrz sekcja 8",
                    "prosta mechanika na pierwszą iterację",
                ],
                [
                    "4",
                    "✓ Rozstrzygnięte: IMU BNO085 oraz Pi 5 + AI HAT+, patrz sekcje 9-11",
                    "IMU usuwa dryf; akcelerator daje rozpoznawanie obrazu w czasie rzeczywistym",
                ],
                [
                    "5",
                    "Prototyp galopu w symulacji",
                    "gotowy, zanim pojawią się silniki zdolne go wykonać",
                ],
                [
                    "6",
                    "Interfejs sprzętowy — podmiana bloku hardware",
                    "pierwsze uruchomienie fizycznego robota",
                ],
                [
                    "7",
                    "✓ Rozstrzygnięte: zasilanie i ładowanie, patrz sekcja 13",
                    "3S LiPo + gniazdo w obudowie, bez wyjmowania baterii",
                ],
                [
                    "8",
                    "Stacja dokująca",
                    "odłożone — trudniejsze niż u robota kołowego, patrz sekcja 12",
                ],
            ],
            [10 * mm, 78 * mm, 80 * mm],
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 8. Montaz (nowa sekcja) ----------
    story.append(p("8. Montaż napędów: w stawie, nie w brzuchu", "H1"))
    story.append(
        p(
            "Każda z 4 nóg dostaje 3 identyczne ST3215 w układzie „klastra biodrowego”, "
            "odwzorowującym łańcuch z URDF (<i>hip_link → thigh_link → calf_link</i>):"
        )
    )
    story.append(
        data_table(
            ["Przegub", "Montaż", "Oś wyjścia"],
            [
                [
                    "Biodro / roll",
                    "na sztywno do korpusu, w każdym z 4 rogów",
                    "równoległa do X (przód–tył)",
                ],
                [
                    "Udo / pitch",
                    "na wsporniku hip_link — jedzie razem z silnikiem roll",
                    "równoległa do Y (lewo–prawo)",
                ],
                [
                    "Kolano / calf pitch",
                    "bezpośrednio w stawie kolanowym, na thigh_link",
                    "równoległa do Y (lewo–prawo)",
                ],
            ],
            [38 * mm, 90 * mm, 40 * mm],
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        p(
            "Alternatywą byłby napęd zdalny: silniki w brzuchu, cięgno lub pasek do dalszych przegubów. "
            "Jedyna korzyść — mniejsza bezwładność wymachującej nogi — liczy się w dynamicznym chodzie "
            "przy prędkości (kłus, galop), nie w quasi-statycznym marszu 10 cm/s z sekcji 5. Opłacamy "
            "złożoność mechaniczną bez żadnego zysku na tym etapie."
        )
    )
    story.append(
        p(
            "Koszty, których unikamy: luz i rozciągnięcie paska/cięgna występują <i>za</i> enkoderem "
            "samego serwa, więc komenda i rzeczywisty kąt kolana rozjeżdżają się, chyba że dojdzie drugi "
            "enkoder w stawie; małe paski i kółka pasowe w skali 22 cm to nie część z półki, tylko osobny "
            "projekt mechaniczny — dokładnie ten rodzaj złożoności, przed którym ostrzega rekomendacja "
            "„pierwsza iteracja na tanich serwach” z sekcji 7."
        )
    )
    story.append(
        p(
            "Napęd zdalny zostawiamy na tę samą przyszłą wymianę, co silniki bezszczotkowe QDD z "
            "sekcji 6 (bieg) — przebudowa mechaniki raz, przy okazji zmiany klasy napędu, nie dwa razy."
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 9. Architektura sterowania ----------
    story.append(p("9. Architektura sterowania: jeden procesor centralny", "H1"))
    story.append(
        p(
            "Rozważaliśmy: procesor per noga czy jeden centralny. Odpowiedź jest jednoznaczna — "
            "<b>jeden centralny</b>, i to nie jest uproszczenie na siłę."
        )
    )
    story.append(
        p(
            "Chód wymaga wiedzy o całym ciele naraz: przekątne nogi w przeciwfazie (trot), różnica "
            "długości kroku lewo/prawo przy skręcie, balans na czterech łapach. Rozbicie tego na 4 "
            "niezależne procesory oznaczałoby synchronizowanie fazy chodu <i>między płytkami</i> — "
            "opóźnienia komunikacji i rozjazd zegarów, dokładnie ten problem, którego jedna centralna "
            "pętla unika z definicji. Do tego serwa STS już mają własny mikrokontroler robiący pętlę "
            "pozycji lokalnie — to już jest „procesor per staw”, wbudowany w silnik. Dodanie kolejnego "
            "poziomu (płytka per noga) nic by nie dało ponad to, co serwo robi samo."
        )
    )
    story.append(
        callout(
            "Kiedy per-noga zaczyna mieć sens",
            "Dopiero przy przejściu na napędy bezszczotkowe QDD i bieg z fazą lotu (sekcja 6) — tam "
            "potrzeba pętli sterowania momentem rzędu tysięcy Hz, gdzie centralne Raspberry Pi fizycznie "
            "nie nadąża. To ta sama przyszła wymiana co reszta odłożonych rzeczy, nie dotyczy pierwszej "
            "iteracji.",
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 10. Percepcja ----------
    story.append(p("10. Percepcja: co widzi i czuje kot", "H1"))
    story.append(
        data_table(
            ["Element", "Wybór", "Dlaczego"],
            [
                [
                    "Kamera",
                    "Raspberry Pi Camera HD v3 12MPx (IMX708)",
                    "standard 119,90 zł / szeroki kąt 169,00 zł, w magazynie Botland",
                ],
                [
                    "Odległość / przeszkody",
                    "VL53L5CX, ToF 8×8 stref, 63°",
                    "daje kąt/mapę, nie jedną liczbę jak pojedynczy ToF czy sonar — 69,90 zł, Pololu",
                ],
                [
                    "Orientacja",
                    "BNO085 (Adafruit 4754)",
                    "następca BNO055 (którego Botland nie ma); fuzja sensorów on-chip, 135,00 zł",
                ],
            ],
            [40 * mm, 60 * mm, 68 * mm],
        )
    )
    story.append(
        callout(
            "Czego świadomie nie bierzemy",
            "<b>Bez LiDAR-u</b> — skanuje jedną płaszczyznę na stałej wysokości, a korpus kota buja się "
            "w pionie podczas chodu; zła geometria dla czworonoga, do tego ciężki i drogi w tej skali. "
            "<b>Bez czujników krawędzi/schodów</b> — środowisko docelowe jest płaskie, ewentualnie "
            "nierówne (kamienie), bez schodów. <b>Bez głębi stereo z dwóch „oczu”</b> — wymagałaby "
            "synchronizacji dwóch modułów kamery i własnej kalibracji/dopasowania obrazów; VL53L5CX daje "
            "tę samą informację prościej. <b>IR/NoIR tylko na żądanie</b> — wariant NoIR kamery "
            "i doświetlacz LED 850nm są w katalogu, ale mają sens wyłącznie jeśli kot ma działać po "
            "ciemku.",
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 11. Kompute ----------
    story.append(p("11. Kompute: Raspberry Pi 5 + AI HAT+", "H1"))
    story.append(
        callout(
            "Rozstrzygnięte — kosztem budżetu",
            "Pi 5 8GB (829,90 zł) + AI HAT+ 13 TOPS (329,00 zł) są na liście zakupowej. Powód jest "
            "techniczny, nie preferencyjny: Pi 4B <b>nie ma złącza PCIe</b>, więc akcelerator Hailo "
            "jest z nim fizycznie niemożliwy — nie gorszy, niemożliwy. Ceną jest budżet: cała lista "
            "wychodzi 3788,60 zł wobec pierwotnych 2500 zł, i to jest jedyne miejsce, gdzie ta "
            "różnica powstała.",
        )
    )
    story.append(
        p(
            "System operacyjny: <b>Raspberry Pi OS (64-bit), nie Ubuntu</b> — "
            "mimo że oficjalne pakiety ROS 2 celują w Ubuntu, to Ubuntu nie ma wbudowanej obsługi "
            "czujnika Camera Module 3 (IMX708) i wymaga budowania forka libcamera ze źródeł. Raspberry "
            "Pi OS ma to od ręki. ROS 2 Jazzy stawiamy przez pixi/RoboStack (ten sam mechanizm co w "
            "symulacji na Macu) — RoboStack publikuje gotowe paczki na linux-aarch64, więc nie trzeba "
            "oficjalnych pakietów Ubuntu."
        )
    )
    story.append(
        p(
            "Akcelerator to <b>AI HAT+ 13 TOPS</b> — moduł Hailo-8L na oficjalnej płytce M.2, "
            "wpinany wprost w złącze PCIe Pi 5. Dystanse i taśma PCIe są zwykle w pudełku."
        )
    )
    story.append(
        data_table(
            ["", "YOLOv8n, 640×640"],
            [
                ["Samo CPU Pi 5", "~12 FPS"],
                ["Z Hailo-8L", "~137 FPS"],
            ],
            [70 * mm, 98 * mm],
        )
    )
    story.append(
        p(
            "To ~11× przyspieszenie — ale ważniejsza niż liczba klatek jest ta konsekwencja: bez "
            "akceleratora cała moc obliczeniowa Pi idzie w widzenie i nic nie zostaje na chód ani "
            "resztę węzłów ROS. Z osobnym układem widzenie działa praktycznie za darmo w tle. Jeden "
            "moduł wystarcza: 13 TOPS to zapas o rząd wielkości większy, niż potrzebuje jedna kamera "
            "przy prędkości 10 cm/s. Kolejność prac to nie zmienia — reaktywne omijanie przeszkód "
            "opiera się na ToF i działa, zanim ktokolwiek uruchomi sieć neuronową.",
            "FootnoteRef",
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 12. Interakcja i dokowanie ----------
    story.append(p("12. Interakcja i dokowanie", "H1"))
    story.append(
        data_table(
            ["Funkcja", "Element", "Uwaga"],
            [
                [
                    "Głaskanie",
                    "MPR121, 12 stref pojemnościowych, I2C",
                    "strefy wzdłuż grzbietu/głowy, nie jedno „dotknięto: tak/nie” — ok. 40-60 zł",
                ],
                [
                    "Miauczenie",
                    "MAX98357A + głośnik",
                    "wzmacniacz I2S 3W, 34,90 zł w Botlandzie",
                ],
                [
                    "Kontroler PS4",
                    "Bluetooth wbudowany w Pi + ROS 2 joy/teleop_twist_joy",
                    "zero nowego sprzętu — paruje się jak zwykły gamepad, mapuje na to samo /cmd_vel",
                ],
            ],
            [30 * mm, 68 * mm, 70 * mm],
        )
    )
    story.append(p("Stacja dokująca — odłożone", "H2"))
    story.append(
        p(
            "Odkurzacz najeżdża na styki kołami — precyzyjne pozycjonowanie jest tanie mechanicznie. "
            "Czworonóg musi trafić stopami w styki z dokładnością chodu, który sam w sobie ma dryf i "
            "poślizg — to trudniejszy problem sterowania niż samo dokowanie. Realistyczna droga: styki "
            "pogo-pin na piersi/brzuchu + marker wizyjny (ArUco/AprilTag) na stacji do precyzyjnego "
            "podejścia na ostatnim odcinku, wykrywany już posiadaną kamerą. To krok <b>po</b> tym, jak "
            "chodzenie i nawigacja będą solidne, nie na pierwszą iterację — ten sam porządek co bieganie "
            "w sekcji 6."
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 13. Zasilanie ----------
    story.append(p("13. Zasilanie", "H1"))
    story.append(
        p(
            "<b>3S LiPo</b> (11,1V, mieści się w zakresie 6–12,6 V serwa ST3215 bez przetwornicy). "
            "Pojemność celowo z zapasem, „im dłużej tym lepiej” — ale to nie jest darmowy wybór: "
            "pojemność LiPo skaluje się z wagą niemal liniowo, a cięższy robot podbija z powrotem budżet "
            "momentu w stawach z sekcji 4/5. Realny czas pracy trzeba będzie zmierzyć na gotowym "
            "sprzęcie, nie zakładać z góry."
        )
    )
    story.append(
        data_table(
            ["Pakiet", "Orientacyjny czas ciągłego chodu"],
            [
                ["3S 2200 mAh", "~22-26 min"],
                ["3S 3000 mAh", "~30-36 min"],
                ["3S 5000 mAh", "~50-60 min"],
            ],
            [70 * mm, 98 * mm],
        )
    )
    story.append(
        p(
            "Ładowanie bez wyjmowania baterii: gniazdo <b>XT60 (lub XT30)</b> montowane w obudowie, na "
            "stałe podłączone do pakietu wraz z wyprowadzonymi pinami balansera — zewnętrzna ładowarka "
            "balansująca wpina się z zewnątrz, bateria zostaje w środku. Osobna gałąź 5V (przetwornica) "
            "dla Raspberry Pi, odizolowana od zasilania serw, żeby skoki prądu serw nie resetowały Pi."
        )
    )
    story.append(Spacer(1, 8))

    # ---------- 14. Plynnosc chodu ----------
    story.append(p("14. Płynność chodu: uczciwa ocena", "H1"))
    story.append(
        p(
            "Pytanie wprost: czy to będzie chodzić płynnie, jak prawdziwy kot, czy jak „pokraczne” "
            "roboty z internetu? Odpowiedź jest pośrodku, i wynika z fizyki wyboru napędu, nie z braku "
            "starań."
        )
    )
    story.append(
        p(
            "Trajektorie są już wygładzone i przetestowane (sinusoidalne uniesienie łapy, filtr "
            "dolnoprzepustowy na komendach, brak skoków między taktami), a ST3215 ma metalowe "
            "przekładnie — to eliminuje szarpanie typowe dla tanich serw hobby z luźnym plastikowym "
            "osprzętem. Twardy sufit: <b>to są serwa pozycyjne, nie momentowe</b>. Prawdziwy kot chodzi "
            "płynnie, bo jego stawy są podatne — reagują na siłę jak sprężyna, a nie „jedź do kąta X "
            "bez względu na kontakt z podłożem”. To różnica strukturalna, nie kwestia strojenia. Do tego "
            "chód jest otwarty (bez sprzężenia z kontaktu łapy) — na nierównym podłożu (kamienie) "
            "każde odchylenie od planu pokaże się jako widoczna korekta, nie płynna adaptacja."
        )
    )
    story.append(
        p(
            "Prawdziwa kocia gracja wymaga sterowania momentem (impedancyjnego) — to ta sama granica, "
            "co przejście na napędy QDD do biegania w sekcji 6. Jeśli płynność ruchu ma wysoki priorytet, "
            "to argument za wcześniejszym rozważeniem tej wymiany, nie tylko „żeby biegał” — ale to "
            "świadomy kompromis kosztowy, nie coś przy okazji.",
            "FootnoteRef",
        )
    )
    story.append(Spacer(1, 8))

    # ---------- Co dokument pomija ----------
    story.append(
        callout(
            "Co ten dokument świadomie pomija",
            "Momenty oparto na masach członów z modelu, które są orientacyjne — realna konstrukcja "
            "zmieni budżet w obie strony (lżejsze człony, ale dochodzi bateria i elektronika). Ceny są "
            "rzędu wielkości. Nie analizowano sztywności ramy, przekładni ani zasilania — na tym etapie "
            "decyzja dotyczy klasy napędu i miejsca montażu, nie konkretnego numeru katalogowego wszystkich "
            "śrub.",
        )
    )

    doc.build(story)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/uzupelnienie-elektroniki.pdf")

