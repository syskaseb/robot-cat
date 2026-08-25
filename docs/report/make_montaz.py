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
            [Paragraph("<b>Wyłącznik główny</b>", CellB), "1",
             "bez niego jedynym sposobem odcięcia zasilania jest wyszarpanie "
             "XT60 — uciążliwe i ryzykowne przy każdej zmianie czegokolwiek. "
             "Musi wytrzymać prąd serw, więc nie byle przełącznik sygnałowy"],
            [Paragraph("<b>Bezpiecznik 20–30 A + oprawka</b>", CellB), "1",
             "szeregowo zaraz za baterią. Pakiet 3S 2200 mAh 25C odda w "
             "zwarciu kilkadziesiąt amperów i stopi przewód, zanim zdążysz "
             "zareagować"],
            [Paragraph("<b>Cyna lutownicza</b>", CellB), "1 rolka",
             "z topnikiem w rdzeniu, 0,7–1,0 mm. Oczywiste, a nie było jej "
             "nigdzie na liście"],
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
             "do wkładek gwintowanych i drobnych goldpinów wystarczy "
             "najtańsza. Do <b>XT60</b> już nie: mosiądz i przewód 16 AWG "
             "wysysają ciepło szybciej, niż 30 W zdąży je oddać, i wychodzi "
             "zimny lut albo stopiona obudowa złącza. Tam trzeba mocniejszej "
             "i <b>grotu ściętego</b>, nie cienkiego stożka — albo kupić "
             "gotowe przewody z wlutowanym XT60 i łączyć już tylko miedź "
             "z miedzią"],
            ["Ściągacz izolacji i obcinaczki boczne", "tak", ""],
            ["Wkrętaki krzyżowe PH0 i PH1", "tak", "małe śruby serw"],
            ["Multimetr", "tak",
             "sprawdzić polaryzację <b>przed</b> pierwszym podłączeniem — "
             "odwrotna zabija 12 serw naraz"],
            ["Klucze imbusowe 1,5–3 mm", "zwykle", "zależnie od projektu obudowy"],
            ["Pęseta", "wygodnie", "wtyki magistrali w ciasnych miejscach"],
            ["Trzecia ręka / imadełko", "wygodnie",
             "XT60 trzeba trzymać nieruchomo, a obie ręce są zajęte grotem "
             "i cyną"],
            ["Ładowarka LiPo z balanserem", "tak",
             "jest w planie zakupowym (B6AC) — nie ładować LiPo byle czym"],
        ],
        [52 * mm, 24 * mm, 82 * mm],
        aligns={1: "CENTER"}))

    s.append(para("Co się wpina, a co trzeba przylutować", H2))
    s.append(para(
        "Większość tego robota składa się bez lutownicy — cała mechanika i "
        "wszystkie dwanaście serw to wtyk w wtyk. Lutowanie skupia się w "
        "jednym miejscu: <b>w zasilaniu</b>.", Body))
    s.append(table(
        ["Element", "Jak się łączy"],
        [
            ["12 serw, adapter magistrali", "kabelki 3-pin w łańcuch — wtyk"],
            ["Bateria LiPo", "ma fabryczny XT60 — wtyk"],
            ["Mikroserwa głowy i ogona → PCA9685", "wtyk"],
            ["Moduły Grove (PCA9685, dotyk)", "wtyk"],
            ["Kamera", "taśma FFC — wsuwana"],
            ["Głośnik", "zwykle listwa na śrubki"],
            [Paragraph("<b>Przetwornica Pololu D24V50F5</b>", CellB),
             Paragraph("<b>lutowanie</b> — ma gołe otwory; goldpiny są w "
                       "zestawie, ale nielutowane", CellB)],
            [Paragraph("<b>Gniazdo XT60 do ładowania</b>", CellB),
             Paragraph("<b>lutowanie</b> — kubki lutownicze, przewód 16 AWG", CellB)],
            ["IMU, wzmacniacz audio",
             "zwykle goldpiny do wlutowania — <b>sprawdzić w ofercie</b>, "
             "część wersji bywa gotowa"],
            ["Wkładki gwintowane M3",
             "nie lutowanie, ale wtapiane lutownicą"],
        ],
        [58 * mm, 100 * mm],
        highlight=[7, 8]))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "To lutowanie dla początkującego: grube przewody, duże pola, żadnego "
        "montażu powierzchniowego. Jedyna uciążliwość to XT60 — mosiądz "
        "odprowadza ciepło, więc słaba lutownica sobie nie poradzi. Pocynować "
        "osobno przewód i kubek, potem złączyć.", Body))

    s.append(callout(
        "Wariant bez lutownicy",
        "Da się prawie w całości: przejściówkę XT60 → DC <b>kupić gotową</b> "
        "(jest na liście wyżej), zamiast Pololu wziąć przetwornicę z "
        "<b>listwą zaciskaną na śrubki</b> — jest ich sporo w tej klasie mocy, "
        "traci się na kompaktowości — i zrezygnować z ładowania bez wyjmowania "
        "baterii. Zostają wkładki gwintowane, a te można zastąpić nakrętkami "
        "zatapianymi w druku.",
        GOOD))

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
            ["Promień łapy", "12 mm", "kula styku — <b>musi być obłożona</b>, "
                                        "patrz niżej"],
        ],
        [46 * mm, 30 * mm, 82 * mm]))

    s.append(para("Łapy — nakładki nie są ozdobą", H2))
    s.append(para(
        "Model zakłada <b>gumowe łapy</b>: w pliku stoi współczynnik tarcia "
        "<font name='Mono' size='8.6'>foot_mu = 1.2</font> z komentarzem, że "
        "to guma i że dzięki niej kot się odpycha, zamiast ślizgać. Goły PETG "
        "na panelach ma jakieś 0,3–0,4, czyli trzy razy mniej — a to znaczy, "
        "że <b>wszystkie zmierzone prędkości i dryf obowiązują tylko z "
        "nakładkami</b>. Bez nich pomiary z symulacji przestają cokolwiek "
        "mówić.", Body))
    s.append(para(
        "Drugie zadanie jest mniej oczywiste. Raport o napędach dobiera serwa "
        "95. percentylem momentu, a nie chwilowym szczytem, uzasadniając to "
        "tym, że szczyty są transjentami kontaktowymi i „w prawdziwym robocie "
        "amortyzuje je podatność mechaniczna”. <b>Tą podatnością jest miękka "
        "łapa.</b> Bez niej uderzenie idzie wprost w przekładnię serwa, a "
        "założenie, na którym oparto wybór ST3215, przestaje obowiązywać.", Body))

    s.append(table(
        ["Materiał", "Tarcie (orientacyjnie)", "Uwaga"],
        [
            ["Goły PETG", "0,3–0,4",
             Paragraph('<font color="#a3251e">za mało — ślizga się i klika</font>',
                       Cell)],
            ["TPU 95A, drukowane", "0,6–0,9",
             "drukowalne, ale <b>TPU nie ma na liście zakupowej</b>, a drukarka "
             "musi je ogarniać — z napędem bezpośrednim łatwiej niż z bowdenem"],
            [Paragraph("<b>Miękki silikon / guma</b>", CellB),
             Paragraph("<b>1,0–1,5</b>", CellB),
             "najbliżej założonych 1,2; gotowe stopki meblowe albo opony do "
             "modeli RC"],
            ["Guma w płynie (Plasti Dip)", "ok. 1,0",
             "najtańsze — obleje kulkę samo, bez projektowania nakładki"],
        ],
        [40 * mm, 32 * mm, 86 * mm],
        aligns={1: "CENTER"},
        highlight=[3]))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "Na hałas działa dokładnie to samo co na tarcie: twardy plastik o "
        "podłogę <b>klika</b>, miękka łapa tłumi uderzenie.", Body))

    s.append(callout(
        "Zaprojektować jako wymienne",
        "Łapy zużywają się szybciej niż cokolwiek innego w tym robocie — to "
        "jedyny element, który przez cały czas ociera się o podłogę. Nakładka "
        "<b>nakręcana albo wciskana, nie klejona na stałe</b>. To decyzja do "
        "podjęcia teraz, w CAD-zie, bo po wydrukowaniu goleni jest już za "
        "późno. Wartości tarcia w tabeli są orientacyjne, z literatury — "
        "jeśli kot będzie się ślizgał mimo nakładek, to pierwszy podejrzany.",
        GOOD))

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

    s.append(para("Chłodzenie", H2))
    s.append(para(
        "Obudowa jest zamknięta, a w środku siedzi dwanaście serw i komputer. "
        "Wentylacji nie da się dorobić po fakcie bez przewiercania gotowego "
        "wydruku, więc otwory trzeba zaplanować od razu.", Body))
    s.append(table(
        ["Źródło ciepła", "Kiedy grzeje", "Uwaga"],
        [
            ["Raspberry Pi 4B", "cały czas",
             "ogranicza wydajność przy <b>80°C</b> — kot zacząłby zwalniać po "
             "kilkunastu minutach, a objaw wyglądałby na błąd w kodzie"],
            ["12 serw", "gdy stoi",
             "obciążenie ciągłe 0,70 Nm na przegub; w ruchu grzeją mniej, bo "
             "mediana to 0,17 Nm"],
            [Paragraph("<b>Sam PETG</b>", CellB), "—",
             "mięknie w okolicach <b>80°C</b>, czyli w tej samej temperaturze, "
             "przy której ogranicza się Pi — materiał obudowy nie daje tu "
             "zapasu"],
        ],
        [40 * mm, 30 * mm, 88 * mm]))
    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "Minimum: <b>radiator na Pi</b> i otwory nisko oraz wysoko w korpusie, "
        "żeby ciepłe powietrze uchodziło górą samo. Nie przykręcać Pi "
        "bezpośrednio do serwa ani do ścianki, o którą opiera się serwo.", Body))
    s.append(callout(
        "Tryb snu jest też chłodzeniem",
        "Leżący kot obciąża napędy praktycznie wcale — 0,09 Nm wobec 0,70 Nm "
        "w staniu. Kładzenie się, gdy nic nie robi, to nie tylko oszczędność "
        "baterii: to jedyny moment, w którym serwa naprawdę stygną.",
        GOOD))

    # ------------------------------------------------------ montaz
    s.append(para("4. Kolejność montażu", H1))
    s.append(para(
        "Kolejność nie jest dowolna: każdy krok kończy się czymś, co da się "
        "sprawdzić, zanim stanie się trudno dostępne.", Body))

    s.append(callout(
        "Co da się zrobić, zanim cokolwiek zostanie wydrukowane",
        "Krok 2 zakłada złożoną nogę, więc od niego w dół <b>wszystko jest "
        "zablokowane projektem obudowy</b> — a tego projektu jeszcze nie ma. "
        "Nie znaczy to jednak, że do tego czasu nie ma co robić. Bez jednego "
        "wydrukowanego elementu da się:<br/><br/>"
        "• <b>zaadresować wszystkie dwanaście serw</b> (krok 1) — potrzeba "
        "tylko serwa, adaptera i kabla;<br/>"
        "• <b>zestawić całą elektronikę na stole</b>: Pi, magistrala, IMU, "
        "ToF, kamera, dźwięk — i sprawdzić, że wszystko się widzi;<br/>"
        "• <b>uruchomić ROS 2 i węzeł chodu</b> na serwach leżących luzem — "
        "nogi w powietrzu nie potrzebują obudowy, a to weryfikuje adresację, "
        "kierunki obrotu i zakresy;<br/>"
        "• <b>zmierzyć realny czas odczytu z magistrali</b> — liczba, na którą "
        "czeka rozdział 6, i jedyna, która wyznacza sufit częstotliwości pętli "
        "sterowania.<br/><br/>"
        "To pokrywa się z testami 1 i 2 z rozdziału 5. Projektowanie obudowy i "
        "uruchamianie elektroniki są <b>niezależne</b> — mogą iść równolegle, "
        "zamiast czekać jedno na drugie.",
        ACCENT))

    s.append(para("Minimum, które trzeba wydrukować, żeby ruszyć dalej", H2))
    s.append(table(
        ["Element", "Stan", "Uwaga"],
        [
            ["Uchwyty serw ST3215", "gotowe",
             "Printables 653674 / Thingiverse 7074577 — najżmudniejsza część "
             "jest już zrobiona przez społeczność"],
            ["Segment uda i goleni", "do zaprojektowania",
             "po 110 mm oś–oś, łączą uchwyty"],
            ["Nakładka łapy", "do zaprojektowania", "wymienna, patrz rozdział 3"],
            ["Mocowanie biodra do korpusu", "do zaprojektowania",
             "wystarczy prowizoryczne, żeby przetestować jedną nogę"],
        ],
        [44 * mm, 34 * mm, 80 * mm],
        aligns={1: "CENTER"}))
    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "Korpus, głowa i pozostałe trzy nogi mogą poczekać. <b>Jedna noga "
        "wystarczy</b>, żeby sprawdzić uchwyty, długości segmentów i to, czy "
        "serwa w ogóle mieszczą się tak, jak zakłada projekt.", Body))

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

    s.append(para("Drzewo zasilania", H2))
    s.append(para(
        "Osobnego projektu elektroniki ani płytki drukowanej ten robot nie "
        "wymaga — wszystko to gotowe moduły łączone kablami. Potrzebny jest "
        "natomiast <b>plan połączeń</b>, bo napięcia są trzy i nie wolno ich "
        "pomylić:", Body))

    s.append(table(
        ["Odbiornik", "Napięcie", "Skąd"],
        [
            ["12 serw ST3215", "11,1 V", "wprost z pakietu, przez gniazdo DC "
                                          "adaptera magistrali"],
            [Paragraph("<b>Raspberry Pi 4B</b>", CellB),
             Paragraph("<b>5 V</b>", CellB),
             "<b>własna gałąź</b> z przetwornicy, grubym przewodem, blisko niej"],
            ["3 mikroserwa (głowa, ogon)", "5–6 V", "z przetwornicy, przez PCA9685"],
            ["Wzmacniacz audio", "5 V", "z przetwornicy"],
            ["2 × doświetlacz IR", "3,3 V",
             "ok. <b>0,9 A na sztukę</b> — <b>nie z pinu 3,3 V w Pi</b>, ten "
             "daje kilkadziesiąt mA. Własny stabilizator albo rezystor"],
        ],
        [46 * mm, 24 * mm, 88 * mm],
        aligns={1: "CENTER"},
        highlight=[2]))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "<b>Masa musi być wspólna dla wszystkiego.</b> Przy adapterze "
        "magistrali warto dołożyć kondensator elektrolityczny — dwanaście serw "
        "ruszających naraz pobiera prąd skokowo.", Body))

    s.append(callout(
        "Wyłącznik i bezpiecznik nie są opcjonalne",
        "Oba są na liście części w rozdziale 1, ale warto powiedzieć wprost, "
        "po co: <b>wyłącznik</b> to jedyny wygodny sposób odcięcia zasilania "
        "przy każdej przeróbce, a <b>bezpiecznik</b> szeregowo zaraz za "
        "baterią jest jedyną rzeczą stojącą między zwarciem a stopionym "
        "przewodem. Razem koszt rzędu kilkunastu złotych — najtańsze "
        "ubezpieczenie w całym projekcie.",
        DANGER))

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

    # ------------------------------------------------ budzet obliczeniowy
    s.append(para("6. Co uciągnie Raspberry Pi 4B", H1))
    s.append(para(
        "Sterowanie jest obliczeniowo tanie i procesor nie jest tu wąskim "
        "gardłem. Ograniczeniem jest <b>przepustowość magistrali serw</b> — "
        "jednego kabla, po którym rozmawia dwanaście napędów.", Body))

    s.append(table(
        ["Zadanie", "Obciążenie", "Uwaga"],
        [
            ["Chód: 12 × kinematyka odwrotna, 100 Hz", "znikome",
             "czysta trygonometria, mikrosekundy na cykl"],
            ["IMU BNO085", "znikome",
             "fuzja czujników dzieje się <b>w samym układzie</b>; Pi odczytuje "
             "gotowe kąty"],
            ["Czujnik ToF", "znikome", "64 strefy po I2C"],
            ["Dźwięk, dotyk", "znikome", ""],
            ["Podgląd obrazu z kamery", "małe",
             "Pi 4B ma sprzętowy koder H.264"],
            [Paragraph("<b>Rozpoznawanie obrazu</b>", CellB),
             Paragraph('<b><font color="#a3251e">nie w czasie rzeczywistym</font></b>',
                       CellB),
             "kilka klatek na sekundę bez akceleratora — dlatego omijanie "
             "przeszkód oparto na ToF, a nie na kamerze"],
        ],
        [56 * mm, 34 * mm, 68 * mm],
        aligns={1: "CENTER"},
        highlight=[6]))

    s.append(Spacer(1, 3 * mm))
    s.append(para("Magistrala serw — tu jest granica", H2))
    s.append(para(
        "Magistrala chodzi do <b>1 Mb/s</b> i obsługuje <b>zapis zbiorczy</b>: "
        "jedna ramka ustawia wszystkie dwanaście serw. Odczyt jest droższy, bo "
        "każde serwo trzeba zapytać osobno i poczekać na odpowiedź.", Body))

    s.append(table(
        ["Operacja", "Czas na cykl", "Przy 100 Hz (budżet 10 ms)"],
        [
            ["Komendy do 12 serw (zapis zbiorczy)", "ok. 0,5 ms",
             Paragraph('<font color="#1c6b45">bez problemu</font>', Cell)],
            [Paragraph("<b>Odczyt z 12 serw (po kolei)</b>", CellB),
             Paragraph("<b>4–10 ms</b>", CellB),
             Paragraph('<b><font color="#a3251e">zjada cały cykl</font></b>',
                       CellB)],
        ],
        [62 * mm, 30 * mm, 66 * mm],
        aligns={1: "CENTER"},
        highlight=[2]))

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Komendy szybko, odczyt wolniej",
        "Rozwiązanie jest standardowe: <b>komendy 100 Hz, informacja zwrotna "
        "20–50 Hz</b>. Chód sterowany pozycyjnie i tak nie potrzebuje odczytu "
        "sto razy na sekundę — a to właśnie odczyt obciążenia ma powiedzieć, "
        "czy montaż nie stawia oporu. Gdyby okazało się za wolno, pierwszym "
        "krokiem jest odczyt zbiorczy, jeśli firmware serwa go wspiera.",
        ACCENT))

    s.append(Spacer(1, 2 * mm))
    s.append(para(
        "Czasy powyżej to oszacowanie z długości ramek przy 1 Mb/s, nie pomiar "
        "— zweryfikować na sprzęcie, bo zależą od opóźnienia odpowiedzi serwa. "
        "Wynik warto zapisać w tym dokumencie, bo wyznacza maksymalną "
        "częstotliwość pętli sterowania.", Body))

    s.append(para("Zanim złożysz elektronikę", H2))
    s.append(table(
        ["", "Do sprawdzenia"],
        [
            ["1", "<b>Ile RAM ma Twoje Pi 4B.</b> Są wersje 2, 4 i 8 GB. ROS 2 "
                  "z kamerą na 2 GB będzie ciasno; od 4 GB w górę spokojnie"],
            ["2", "Karta microSD kończy się szybciej niż sprzęt, jeśli system "
                  "dużo loguje — a logowanie obciążenia serw jest tu zalecane. "
                  "Warto ograniczyć zapis albo logować na pendrive"],
        ],
        [10 * mm, 148 * mm],
        aligns={0: "CENTER"}))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/montaz.pdf")
