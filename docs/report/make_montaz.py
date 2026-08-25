"""Robot Cat - instrukcja montazu, obudowa i pierwsze uruchomienie.

Rebuild from the repo root:

    python docs/report/make_montaz.py docs/montaz.pdf

Dimensions come from src/robot_cat_description/urdf/cat.urdf.xacro at
scale 1.0 - that file is the source of truth, not this document. If the model
changes, regenerate.
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
pdfmetrics.registerFont(TTFont("Mono", _font(
    _WIN / "consola.ttf",
    pathlib.Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
    _LIN / "dejavu/DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily("Cal", normal="Cal", bold="Cal-B", italic="Cal-I")

INK = colors.HexColor("#16191d")
ACCENT = colors.HexColor("#0f4c5c")
WARM = colors.HexColor("#b3541e")
MUTED = colors.HexColor("#5f6b73")
RULE = colors.HexColor("#d3dade")
PANEL = colors.HexColor("#f2f5f6")
GOOD = colors.HexColor("#1c6b45")
DANGER = colors.HexColor("#a3251e")

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
Mono = st("Mono", fontName="Mono", fontSize=8.6, leading=12.5)


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


def code(lines):
    t = Table([[Paragraph("<br/>".join(lines), Mono)]], colWidths=[158 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 3 * mm)])


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
    canvas.drawString(26 * mm, 287.5 * mm, "Robot Cat — montaż i uruchomienie")
    canvas.drawRightString(184 * mm, 287.5 * mm, "sierpień 2026")
    canvas.line(26 * mm, 17 * mm, 184 * mm, 17 * mm)
    canvas.drawString(26 * mm, 12.5 * mm,
                      "Wymiary z cat.urdf.xacro — model jest źródłem prawdy")
    canvas.drawRightString(184 * mm, 12.5 * mm, f"{doc.page}")
    canvas.restoreState()


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=26 * mm, rightMargin=26 * mm,
                          topMargin=24 * mm, bottomMargin=22 * mm,
                          title="Robot Cat — montaż i uruchomienie", author="analiza")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=header_footer)])
    s = []

    s.append(Spacer(1, 4 * mm))
    s.append(para("Robot Cat", Title))
    s.append(para("Montaż, obudowa i pierwsze uruchomienie",
                  st("s2", fontName="Cal-B", fontSize=13.5, leading=17,
                     textColor=INK, spaceBefore=2)))
    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Uzupełnienie planu zakupowego o rzeczy, których w nim nie ma: kable, "
        "złączki, narzędzia, wymiary obudowy i kolejność uruchamiania. "
        "Wszystkie wymiary pochodzą z modelu w repozytorium — jeśli model się "
        "zmieni, ten dokument trzeba wygenerować od nowa.", Sub))
    s.append(Spacer(1, 5 * mm))

    s.append(callout(
        "Najważniejsza rzecz przed podłączeniem czegokolwiek",
        "Wszystkie serwa magistralowe wychodzą z fabryki z <b>tym samym "
        "adresem</b>. Podłączenie dwunastu naraz i próba nadania adresów "
        "kończy się tym, że każde odpowiada jednocześnie i nie da się ich "
        "rozróżnić. Adresy nadaje się <b>pojedynczo</b>, podłączając po jednym "
        "serwie do adaptera — zanim cokolwiek trafi do nogi. Opisane w kroku 1.",
        DANGER))
    s.append(Spacer(1, 4 * mm))

    # -------------------------------------------------- brakujace czesci
    s.append(para("1. Czego brakuje w liście zakupowej", H1))
    s.append(para(
        "Plan zakupowy jawnie pomijał „śrubki, tulejki i przewody specyficzne "
        "dla finalnego CAD-u”. Poniżej to, co trzeba dokupić, żeby dało się "
        "cokolwiek połączyć. Ceny orientacyjne — to drobnica, w sumie rzędu "
        "150–250 zł.", Body))

    s.append(table(
        ["Element", "Ile", "Po co"],
        [
            [Paragraph("<b>Przejściówka XT60 → DC 5,5/2,1 mm</b>", CellB), "1",
             "adapter magistrali pobiera zasilanie serw <b>przez gniazdo DC</b>, "
             "a bateria kończy się wtyczką XT60 — bez tego nie ma jak ich połączyć"],
            ["Kable magistrali serw (3-pin)", "12+",
             "adapter jest sprzedawany <b>bez żadnych kabli</b>; serwa zwykle mają "
             "po jednym w zestawie, ale do nóg potrzeba dłuższych — sprawdzić "
             "zawartość opakowania po dostawie"],
            ["Przewód Grove → DuPont 4-pin", "2–3",
             "PCA9685 i TTP223 to moduły Grove, a Raspberry Pi nie ma takich "
             "złącz; HAT nie jest potrzebny, wystarczy przejściówka"],
            ["Przewód silikonowy 16 AWG, czarny i czerwony", "1 m",
             "rozprowadzenie zasilania; cieńszy będzie się grzał przy 12 serwach"],
            ["Gniazdo XT60 montażowe + wtyk", "1 kpl.",
             "ładowanie bez wyjmowania baterii, jak zakładał plan"],
            ["Śruby M2 × 6 i M2,5 × 8", "po ~50",
             "mocowanie serw i orczyków; ST3215 ma śruby w zestawie, ale "
             "zapas się przydaje"],
            ["Wkładki gwintowane M3 do PETG", "~20",
             "gwint nacięty w druku wyrywa się po kilku odkręceniach; wkładki "
             "wtapiane lutownicą rozwiązują to raz na zawsze"],
            ["Koszulki termokurczliwe + opaski zaciskowe", "kpl.",
             "kable w nogach muszą przetrwać zginanie przy każdym kroku"],
        ],
        [46 * mm, 14 * mm, 98 * mm],
        aligns={1: "CENTER"},
        highlight=[1]))

    # ------------------------------------------------------- narzedzia
    s.append(para("2. Narzędzia do montażu w domu", H1))
    s.append(table(
        ["Narzędzie", "Konieczne?", "Uwaga"],
        [
            ["Drukarka 3D (PETG)", "tak",
             "albo usługa druku — PETG, nie PLA: mniej kruchy przy obciążeniach "
             "udarowych"],
            ["Lutownica", "tak",
             "do zasilania i wtapiania wkładek gwintowanych; grot stożkowy "
             "wystarczy"],
            ["Ściągacz izolacji i obcinaczki boczne", "tak", ""],
            ["Wkrętaki krzyżowe PH0 i PH1", "tak", "małe śruby serw"],
            ["Multimetr", "tak",
             "sprawdzić polaryzację <b>przed</b> pierwszym podłączeniem — "
             "odwrotna zabija 12 serw naraz"],
            ["Klucze imbusowe 1,5–3 mm", "zwykle", "zależnie od projektu obudowy"],
            ["Pęseta", "wygodnie", "wtyki magistrali w ciasnych miejscach"],
            ["Ładowarka LiPo z balanserem", "tak",
             "jest w planie zakupowym (B6AC) — nie ładować LiPo byle czym"],
        ],
        [52 * mm, 24 * mm, 82 * mm],
        aligns={1: "CENTER"}))

    s.append(callout(
        "O bezpieczeństwie LiPo",
        "Pakiet 3S 2200 mAh potrafi oddać kilkadziesiąt amperów w zwarciu. "
        "Ładować w torbie ognioodpornej i nie zostawiać bez nadzoru; nie "
        "rozładowywać poniżej 3,3 V na ogniwo; przy montażu odłączać baterię "
        "za każdym razem, gdy coś się przekłada. To jedyny element w tym "
        "projekcie, który potrafi zrobić krzywdę."))

    # -------------------------------------------------------- obudowa
    s.append(para("3. Obudowa — specyfikacja wymiarowa", H1))
    s.append(para(
        "Poniższe wymiary są <b>wprost z modelu symulacyjnego</b>, na którym "
        "policzono momenty i chód. Konstrukcja mechaniczna musi je odwzorować, "
        "inaczej wyniki symulacji przestają obowiązywać.", Body))

    s.append(para("Korpus", H2))
    s.append(table(
        ["Wymiar", "Wartość", "Uwaga"],
        [
            ["Pudełko tułowia", "300 × 111 × 141 mm", "dł. × szer. × wys."],
            ["Osie bioder od środka", "x = ±110 mm, y = ±55 mm", "cztery narożniki"],
            ["Rozstaw bioder", "220 mm wzdłuż, 110 mm w poprzek", ""],
            ["Wypełnienie wnętrza", "ok. 7%", "serwa + bateria + Pi = 323 cm³ z 4695"],
        ],
        [46 * mm, 54 * mm, 58 * mm]))
    s.append(para(
        "Wnętrze jest zajęte w kilku procentach, więc rozmieszczenie "
        "elektroniki nie jest problemem — <b>ale tułów jest głębszy niż "
        "szerszy</b> (141 wobec 111 mm) i to trzeba zachować. Kot ma klatkę "
        "pionowo owalną; odwrócenie tych proporcji daje sylwetkę płyty na "
        "nogach, co było błędem wcześniejszej wersji modelu.", Body))

    s.append(para("Noga (×4, wszystkie identyczne)", H2))
    s.append(table(
        ["Wymiar", "Wartość", "Uwaga"],
        [
            ["Biodro → udo, w bok", "25 mm", "oś obrotu roll do osi pitch"],
            ["Udo, oś–oś", "110 mm", "od osi uda do osi kolana"],
            ["Goleń, oś–łapa", "110 mm", "od osi kolana do środka łapy"],
            ["Promień łapy", "12 mm", "kula styku, warto obłożyć TPU"],
        ],
        [46 * mm, 30 * mm, 82 * mm]))

    s.append(para("Postawa wynikowa", H2))
    s.append(table(
        ["Miara", "Wartość"],
        [
            ["Biodro nad ziemią", "172 mm"],
            [Paragraph("<b>Kłąb (wysokość w barku)</b>", CellB),
             Paragraph("<b>242 mm</b>", CellB)],
            ["Brzuch nad ziemią", "102 mm"],
            ["Głowa (promień kuli)", "50 mm"],
        ],
        [110 * mm, 48 * mm],
        aligns={1: "CENTER"},
        highlight=[2]))

    s.append(para("Głowa — gniazda kamery i doświetlacza", H2))
    s.append(para(
        "Oczy nie są już tylko ozdobą: w jednym siedzi kamera, w drugim "
        "doświetlacz podczerwieni (patrz plan zakupowy). Pozycje oczu są "
        "wprost z modelu, liczone od środka kuli głowy.", Body))
    s.append(table(
        ["Wymiar", "Wartość", "Uwaga"],
        [
            ["Promień kuli głowy", "50 mm", ""],
            ["Oko — do przodu", "36 mm", "od środka głowy"],
            ["Oko — w bok", "±22 mm", "rozstaw oczu 44 mm"],
            ["Oko — w górę", "18 mm", ""],
            [Paragraph("<b>Płytka kamery</b>", CellB),
             Paragraph("<b>25 × 24 × 12,4 mm</b>", CellB),
             "Camera Module 3 <b>Wide</b> — wersja nie-szerokokątna jest "
             "o 0,9 mm płytsza, więc gniazdo projektować pod Wide"],
            ["Doświetlacz IR", "moduł 850 nm 3 W", "rozsył 100°, ma fotorezystor"],
        ],
        [46 * mm, 40 * mm, 72 * mm]))
    s.append(para(
        "Kamera NoIR i zwykła mają <b>identyczną płytkę</b>, więc gniazdo "
        "zaprojektowane raz obsłuży obie — to celowe wyjście awaryjne, gdyby "
        "różowe kolory w dzień okazały się nie do przyjęcia. Taśmę FFC "
        "poprowadzić przez szyję z zapasem na pełny obrót głowy: pan ±0,6 rad "
        "i tilt od −0,3 do +0,5 rad, więc taśma zgina się przy każdym "
        "rozejrzeniu i to ona, nie kamera, zużyje się pierwsza.", Body))

    s.append(callout(
        "Czego ten dokument nie zawiera i dlaczego",
        "<b>Gotowego CAD-u ani plików STL.</b> Powyższe to specyfikacja "
        "wymiarowa — wejście do projektowania, nie jego wynik. Uczciwie: "
        "zaprojektowanie uchwytów, które faktycznie trzymają serwo i "
        "przenoszą obciążenia, wymaga pracy w CAD z częściami w ręku, i "
        "wygenerowanie czegoś „na oko” byłoby gorsze niż nic, bo nie "
        "pasowałoby do prawdziwych elementów."))

    s.append(para(
        "Jest natomiast dobra wiadomość: <b>ST3215 ma niestandardowy rozstaw "
        "otworów</b>, co jest znanym utrapieniem — i społeczność już to "
        "rozwiązała. Gotowe uchwyty do druku są dostępne na Printables "
        "(model 653674) i Thingiverse (7074577); mocują się śrubami z zestawu "
        "serwa i nie wymagają dokupowania osprzętu. To oszczędza "
        "najżmudniejszą część projektowania — resztę obudowy można zbudować "
        "wokół nich.", Body))

    s.append(para("Parametry druku", H2))
    s.append(table(
        ["Parametr", "Zalecenie", "Dlaczego"],
        [
            ["Materiał", "PETG", "mniej kruchy od PLA przy uderzeniach łapą"],
            ["Ścianki", "3–4 obrysy", "obciążenia idą przez ścianki, nie wypełnienie"],
            ["Wypełnienie", "30–40%", "wyżej to już tylko masa, która podbija moment"],
            ["Warstwa", "0,2 mm", "kompromis czasu i wytrzymałości"],
            ["Orientacja", "wzdłuż obciążenia", "warstwy rozwarstwiają się w poprzek"],
        ],
        [34 * mm, 40 * mm, 84 * mm]))

    # ------------------------------------------------------ montaz
    s.append(para("4. Kolejność montażu", H1))
    s.append(para(
        "Kolejność nie jest dowolna: każdy krok kończy się czymś, co da się "
        "sprawdzić, zanim stanie się trudno dostępne.", Body))

    s.append(para("Krok 1 — adresacja serw (przed montażem czegokolwiek)", H2))
    s.append(para(
        "Podłączyć <b>jedno</b> serwo do adaptera, nadać adres, opisać "
        "naklejką, odłączyć, wziąć następne. Kolejność adresów musi odpowiadać "
        "kolejności z <font name='Mono' size='8.6'>controllers.yaml</font>, "
        "bo węzeł chodu pakuje komendy dokładnie w tej kolejności:", Body))

    s.append(table(
        ["Przegub", "Przód lewy", "Przód prawy", "Tył lewy", "Tył prawy"],
        [
            ["Biodro (roll)", "ID 1", "ID 4", "ID 7", "ID 10"],
            ["Udo (pitch)", "ID 2", "ID 5", "ID 8", "ID 11"],
            ["Kolano (pitch)", "ID 3", "ID 6", "ID 9", "ID 12"],
        ],
        [38 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm],
        aligns={1: "CENTER", 2: "CENTER", 3: "CENTER", 4: "CENTER"}))
    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "Adresy rosną wzdłuż nogi (biodro, udo, kolano) i nogami w kolejności "
        "przód-lewy, przód-prawy, tył-lewy, tył-prawy. Ta kolejność jest "
        "<b>kontraktem z oprogramowaniem</b>, nie konwencją — zapisana jest w "
        "<font name='Mono' size='8.6'>controllers.yaml</font> i w "
        "<font name='Mono' size='8.6'>JOINT_ORDER</font>. Pomylenie dwóch "
        "adresów objawi się nogą ruszającą się nie w tę stronę co reszta.", Body))

    s.append(para("Krok 2 — nogi pojedynczo", H2))
    s.append(para(
        "Złożyć jedną nogę w całości i sprawdzić zakresy ruchu <b>bez "
        "obciążenia</b>, zanim powstaną pozostałe trzy. Błąd w uchwycie "
        "wykryty na pierwszej nodze kosztuje jeden wydruk; wykryty na "
        "czwartej — cztery.", Body))
    s.append(para(
        "Przednie i tylne nogi są <b>identyczne</b>. Wcześniejsza wersja "
        "modelu miała lustrzane kolana, jak u prawdziwego kota, ale zostało to "
        "celowo wycofane na rzecz układu, jaki mają prawdziwe roboty "
        "czworonożne — cztery takie same nogi to jeden wydruk w czterech "
        "egzemplarzach i jedna część zamienna.", Body))

    s.append(para("Krok 3 — korpus i elektronika", H2))
    s.append(para(
        "Kolejność: rozprowadzenie zasilania → Raspberry Pi → adapter "
        "magistrali → IMU → reszta czujników. Zasilanie najpierw, bo to "
        "jedyna rzecz, która może uszkodzić resztę. <b>Zmierzyć polaryzację "
        "multimetrem przed podłączeniem czegokolwiek.</b>", Body))
    s.append(para(
        "Raspberry Pi <b>musi mieć własną gałąź 5 V</b> z przetwornicy, "
        "odseparowaną od linii serw. Dwanaście serw ruszających jednocześnie "
        "powoduje zapad napięcia, który zresetuje komputer w połowie kroku.", Body))

    s.append(para("Krok 4 — złożenie i kalibracja zera", H2))
    s.append(para(
        "Przykręcić nogi do korpusu, ustawić wszystkie serwa w pozycji "
        "neutralnej i zamontować orczyki tak, by noga stała w pozycji "
        "wyprostowanej zgodnie z modelem. To jest moment, w którym mechanika "
        "spotyka się z symulacją — jeśli zero jest przesunięte, kot będzie "
        "chodził krzywo, a wina będzie wyglądała na programową.", Body))

    # ------------------------------------------------- uruchomienie
    s.append(para("5. Pierwsze uruchomienie", H1))
    s.append(para(
        "System na Raspberry Pi: <b>Raspberry Pi OS 64-bit</b>, nie Ubuntu. "
        "Powód jest konkretny — obsługa czujnika kamery IMX708 jest w Pi OS od "
        "ręki, a na Ubuntu wymaga budowania libcamera ze źródeł. ROS 2 Jazzy "
        "instaluje się przez RoboStack, który publikuje paczki na "
        "linux-aarch64.", Body))

    s.append(para("Kolejność testów — od najmniej ryzykownego", H2))
    s.append(table(
        ["", "Test", "Co sprawdza"],
        [
            ["1", "Serwa pojedynczo, noga w powietrzu",
             "adresacja, kierunki obrotu, zakresy — bez ryzyka upadku"],
            ["2", "Pozycja stojąca, kot podparty ręką",
             "czy zero jest dobrze skalibrowane i czy nogi ustawiają się "
             "symetrycznie"],
            ["3", "Stanie o własnych siłach",
             "obciążenie ciągłe 0,70 Nm na przegub — sprawdzić, czy serwa się "
             "nie grzeją"],
            ["4", "Chód na uwięzi (ręka nad grzbietem)",
             "pierwszy ruch; szczyty ok. 1,87 Nm"],
            ["5", "Chód swobodny 0,1 m/s",
             "dopiero teraz robot chodzi sam"],
        ],
        [10 * mm, 52 * mm, 96 * mm],
        aligns={0: "CENTER"}))

    s.append(callout(
        "Czego się spodziewać — i czego nie",
        "Kot będzie chodził <b>powoli i sztywno</b>. To nie jest wada montażu: "
        "serwa są pozycyjne, więc jadą do zadanego kąta niezależnie od tego, co "
        "napotkają, a chód jest sterowany bez sprzężenia zwrotnego. Prawdziwa "
        "kocia miękkość wymaga sterowania momentem, czyli innej klasy napędów. "
        "Pierwszym krokiem w tę stronę jest <b>IMU, które jest już w koszyku</b> "
        "— pozwoli chodowi wiedzieć, gdzie faktycznie znajduje się ciało."))

    s.append(para("Co mierzyć, żeby wiedzieć, że działa", H2))
    s.append(para(
        "Serwa raportują przez magistralę pozycję, obciążenie, prędkość i "
        "napięcie. Warto od początku logować <b>obciążenie</b> i "
        "<b>napięcie zasilania</b>: pierwsze powie, czy montaż nie stawia "
        "oporu, drugie — czy bateria nie siada. Wartości odniesienia z "
        "symulacji, do porównania:", Body))

    s.append(table(
        ["Stan", "Moment na przegub"],
        [
            ["Leży", "0,09 Nm"],
            ["Stoi", "0,70 Nm"],
            ["Idzie 0,1 m/s — typowo", "0,17 Nm"],
            ["Idzie 0,1 m/s — szczyty", "1,87 Nm"],
        ],
        [110 * mm, 48 * mm],
        aligns={1: "CENTER"}))

    s.append(para(
        "Jeśli zmierzone wartości będą <b>wyraźnie wyższe</b>, najbardziej "
        "prawdopodobne przyczyny to opory w przegubach (za ciasne uchwyty, "
        "brak luzu na łożyskach) albo cięższy wydruk niż zakładane 700 g. "
        "Oba są do naprawienia mechanicznie i oba lepiej wykryć na tym etapie "
        "niż po tygodniu chodzenia.", Body))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/montaz.pdf")
