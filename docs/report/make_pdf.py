"""Robot Cat v4 - actuator decision, rebuilt after the size and mass questions
were settled. Every figure is measured in Gazebo unless marked otherwise.

Rebuild the whole report from the repo root:

    python docs/report/charts.py
    python docs/report/chart_decision.py
    python docs/report/make_pdf.py docs/napedy-v4.pdf

Needs reportlab, matplotlib and pillow, and Calibri - so this runs on the
Windows box, not inside the ROS container.
"""

import pathlib

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Cal", rf"{F}\calibri.ttf"))
pdfmetrics.registerFont(TTFont("Cal-B", rf"{F}\calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Cal-I", rf"{F}\calibrii.ttf"))
pdfmetrics.registerFont(TTFont("Mono", rf"{F}\consola.ttf"))
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
        spaceBefore=17, spaceAfter=7)
H2 = st("H2", fontName="Cal-B", fontSize=11.5, leading=15, textColor=INK,
        spaceBefore=11, spaceAfter=4)
Body = st("Body", alignment=TA_JUSTIFY, spaceAfter=7)
Small = st("Small", fontSize=8.7, leading=12, textColor=MUTED)
Cell = st("Cell", fontSize=9.2, leading=12.5)
CellB = st("CellB", fontName="Cal-B", fontSize=9.2, leading=12.5)
CellH = st("CellH", fontName="Cal-B", fontSize=9, leading=12, textColor=colors.white)
Code = st("Code", fontName="Mono", fontSize=8.6, leading=12.5)

HERE = pathlib.Path(__file__).resolve().parent


def figure(name, caption, width=158 * mm):
    path = str(HERE / name)
    w, h = PILImage.open(path).size
    img = Image(path, width=width, height=width * h / w)
    cap = Paragraph(caption, st("cap", fontSize=8.4, leading=11.5,
                                textColor=MUTED, spaceBefore=3))
    return KeepTogether([img, cap, Spacer(1, 4 * mm)])


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
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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
    canvas.drawString(26 * mm, 287.5 * mm, "Robot Cat — dobór napędów, wersja 4")
    canvas.drawRightString(184 * mm, 287.5 * mm, "sierpień 2026")
    canvas.line(26 * mm, 17 * mm, 184 * mm, 17 * mm)
    canvas.drawString(26 * mm, 12.5 * mm,
                      "Liczby zmierzone w symulacji Gazebo Harmonic")
    canvas.drawRightString(184 * mm, 12.5 * mm, f"{doc.page}")
    canvas.restoreState()


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=26 * mm, rightMargin=26 * mm,
                          topMargin=24 * mm, bottomMargin=22 * mm,
                          title="Robot Cat — dobór napędów v4",
                          author="analiza symulacyjna")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame],
                                       onPage=header_footer)])
    s = []

    # ---------------------------------------------------------------- cover
    s.append(Spacer(1, 5 * mm))
    s.append(para("Robot Cat", Title))
    s.append(para("Dobór napędów — wersja 4, po rozstrzygnięciu rozmiaru i masy",
                  st("s2", fontName="Cal-B", fontSize=13.5, leading=17,
                     textColor=INK, spaceBefore=2)))
    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Wersja 3 rekomendowała Feetech STS3250 i ostrzegała, że przy większym "
        "robocie trzeba będzie sięgnąć po napędy bezszczotkowe za kilkanaście "
        "tysięcy złotych. Obie te rzeczy okazały się <b>niepotrzebne</b>. "
        "Ten dokument pokazuje, co się zmieniło i dlaczego.", Sub))
    s.append(Spacer(1, 5 * mm))

    s.append(callout(
        "Wnioski",
        "<b>1.</b> Symulacja zakładała robota o masie <b>3,7 kg</b>. Realna "
        "konstrukcja — druk z PETG, 12 serw, bateria, elektronika — waży "
        "<b>2,0 kg</b>. Prawdziwy kot waży 4-5 kg, bo jest z mięsa i kości; "
        "pusty w środku wydruk waży o połowę mniej.<br/><br/>"
        "<b>2.</b> Przy realnej masie wymagany moment spada z 3,46 do "
        "<b>1,87 Nm</b>. Najtańsze serwo z półki (<b>Waveshare ST3215</b>, "
        "109 zł) ma <b>39% zapasu nawet na rozładowanej baterii</b>.<br/><br/>"
        "<b>3.</b> Zapis w briefie „ok. 50 cm wysokości” to nie jest kot, tylko "
        "ryś: 24 kg i 28,6 Nm na przegub. Zwykły kot ma 24 cm w kłębie i tyle ma "
        "model.",
        ACCENT))
    s.append(Spacer(1, 5 * mm))

    # ------------------------------------------------------------ rozmiar
    s.append(para("1. Rozmiar: co znaczy „kot”", H1))
    s.append(para(
        "To była pierwsza rzecz do rozstrzygnięcia, bo od niej zależy wszystko "
        "inne. Brief prosi o zwierzę „ok. 50 cm wysokości”, ale kot o kocich "
        "proporcjach i takiej wysokości to inne zwierzę.", Body))

    s.append(table(
        ["", "Zwykły kot", "Wersja 50 cm"],
        [
            ["Wysokość w kłębie", "24,2 cm", "45,3 cm"],
            ["Długość tułowia", "30 cm", "56 cm"],
            ["Wysokość całkowita", "29 cm", "55 cm"],
            ["Masa (proporcjonalnie)", "3,7 kg", "24,2 kg"],
            [Paragraph("<b>Moment na przegub</b>", CellB),
             Paragraph('<b><font color="#1c6b45">3,46 Nm</font></b>', CellB),
             Paragraph('<b><font color="#b3541e">28,6 Nm</font></b>', CellB)],
            ["Klasa napędu", "serwo hobby, ~110 zł/szt.", "bezszczotkowy, ~1500 zł/szt."],
        ],
        [46 * mm, 56 * mm, 56 * mm],
        aligns={1: "CENTER", 2: "CENTER"},
        highlight=[5]))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Moment rośnie z <b>3,4 potęgą</b> wymiaru, więc zwierzę dwa razy "
        "wyższe potrzebuje napędów ośmiokrotnie mocniejszych. Kociokształtne "
        "zwierzę o 40 cm w kłębie istnieje w naturze — to ryś, i faktycznie "
        "waży ok. 20 kg. Model przy domyślnych ustawieniach ma 24,2 cm w "
        "kłębie wobec 24 cm żywego kota, więc niczego nie trzeba skalować. "
        "Punkt porównawczy zmierzono przy skali 1,87, co daje 55 cm wysokości "
        "całkowitej — czyli mniej więcej to, o co prosi brief.", Body))

    s.append(figure(
        "chart_scale.png",
        "Oba punkty zmierzone, krzywa dopasowana do nich. Wersja 50 cm leży w "
        "paśmie napędów klasy Unitree Go2."))

    # -------------------------------------------------------------- masa
    s.append(para("2. Masa realnej konstrukcji", H1))
    s.append(para(
        "Symulacja liczyła 3,7 kg, bo skalowała gęstość żywego kota. To był "
        "<b>błąd metodyczny</b>: robot nie jest z mięsa. Budżet masy policzony "
        "z listy zakupowej:", Body))

    s.append(table(
        ["Grupa", "Masa", "Uwaga"],
        [
            [Paragraph("<b>12 × ST3215</b>", CellB),
             Paragraph("<b>828 g</b>", CellB), "69 g/szt. — 41% całości"],
            ["Obudowa PETG", "~700 g", "szacunek, nie pomiar"],
            ["Bateria 3S 2200 mAh", "185 g", ""],
            ["Okablowanie", "~125 g", "magistrala + zasilanie"],
            ["Śruby, tulejki, łożyska", "~80 g", ""],
            ["Raspberry Pi 4B + karta", "47 g", ""],
            ["3 × mikroserwo (głowa, ogon)", "27 g", ""],
            ["Elektronika (IMU, PWM, audio, zasilanie)", "~31 g", ""],
            ["Kamera + czujnik ToF", "~6 g", "bez znaczenia dla wyniku"],
            [Paragraph("<b>RAZEM</b>", CellB),
             Paragraph('<b><font color="#1c6b45">≈ 2,0 kg</font></b>', CellB),
             "widełki 1,9-2,3 kg"],
        ],
        [66 * mm, 30 * mm, 62 * mm],
        aligns={1: "CENTER"},
        highlight=[10]))

    s.append(Spacer(1, 3 * mm))
    s.append(callout(
        "Dlaczego to zmienia wszystko",
        "Przy tej skali moment skaluje się z masą <b>niemal liniowo</b>: "
        "redukcja masy o 45% dała spadek momentu o 46%. Zmierzone, nie "
        "założone — i warto to podkreślić, bo przy wersji 50&nbsp;cm było "
        "<i>inaczej</i>: tam redukcja masy o 38% dała tylko 5%, bo dominował "
        "artefakt sterowania, a nie ciężar. Wniosek z dużego robota nie "
        "przenosi się na małego.", GOOD))

    # ------------------------------------------------------------ moment
    s.append(para("3. Co naprawdę wyznacza wymagany moment", H1))
    s.append(para(
        "Zanim padła odpowiedź, sprawdzono i <b>odrzucono</b> trzy hipotezy. "
        "Każda wydawała się oczywista i każda okazała się nieprawdziwa:", Body))

    s.append(table(
        ["Hipoteza", "Test", "Wynik"],
        [
            ["Szybszy chód obciąża bardziej",
             "0,94 m/s wobec 0,1 m/s",
             Paragraph('<font color="#b3541e">bez różnicy</font>', Cell)],
            ["Twarde lądowanie łapy",
             "wymach złagodzony 10×",
             Paragraph('<font color="#b3541e">bez różnicy</font>', Cell)],
            ["Nogi więżą się przez podłoże",
             "duty 0,65 wobec 0,50",
             Paragraph('<font color="#b3541e">bez różnicy</font>', Cell)],
            ["Decyduje po prostu ciężar",
             "3,7 kg wobec 2,03 kg",
             Paragraph('<b><font color="#1c6b45">−46%</font></b>', CellB)],
        ],
        [52 * mm, 46 * mm, 60 * mm],
        highlight=[4]))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Prędkość jest nieistotna, bo chód przy 0,1 m/s jest quasi-statyczny — "
        "łapa dotyka podłoża tak samo często, tylko robot przesuwa się między "
        "krokami wolniej. To praktyczny wniosek: <b>zwolnienie kota nie "
        "oszczędza napędów</b>, więc nie ma powodu ograniczać prędkości poniżej "
        "tego, co wygląda naturalnie.", Body))

    s.append(figure(
        "chart_speed.png",
        "Prędkość zależy od iloczynu kroku i tempa, nie od samego kroku — "
        "dłuższy krok przy wolnym tempie jest wolniejszy, bo noga przy granicy "
        "zasięgu ślizga się zamiast odpychać."))

    # --------------------------------------------------------- napiecie
    s.append(para("4. Napięcie baterii — pułapka katalogowa", H1))
    s.append(para(
        "Katalogowe „30 kg·cm” dla ST3215 to wartość <b>przy 12 V</b>. Pakiet "
        "3S ma 12,6 V po naładowaniu, 11,1 V nominalnie i ok. 10,5 V pod "
        "koniec. Dla silnika prądu stałego moment utyku jest proporcjonalny do "
        "napięcia, więc realny moment maleje w trakcie pracy.", Body))

    s.append(table(
        ["Stan pakietu 3S", "Napięcie", "ST3215", "Zapas wobec 1,87 Nm"],
        [
            ["Świeżo naładowany", "12,6 V", "3,08 Nm",
             Paragraph('<font color="#1c6b45">+65%</font>', Cell)],
            ["Większość rozładowania", "11,8 V", "2,87 Nm",
             Paragraph('<font color="#1c6b45">+53%</font>', Cell)],
            ["Pod koniec / duże obciążenie", "10,5 V", "2,57 Nm",
             Paragraph('<b><font color="#1c6b45">+39%</font></b>', CellB)],
        ],
        [50 * mm, 26 * mm, 26 * mm, 56 * mm],
        aligns={1: "CENTER", 2: "CENTER", 3: "CENTER"}))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "To wyjaśnia znany objaw robotów na tanich serwach: <b>chodzą coraz "
        "gorzej, im bardziej rozładowana bateria</b>. Nie z przegrzania, tylko "
        "ze spadku napięcia. Tutaj zapas jest na tyle duży, że zjawisko nie "
        "powinno być odczuwalne.", Body))

    s.append(figure(
        "chart_decision.png",
        "Krzywa serwa wobec wymagania. Linia pomarańczowa pokazuje, gdzie "
        "leżałby próg, gdyby robot faktycznie ważył 3,7 kg — i dlaczego wersja "
        "3 tego dokumentu wybrała droższe serwo."))

    # ------------------------------------------------------------ termika
    s.append(para("5. Przegrzewanie i czas pracy", H1))
    s.append(para(
        "Serwa nie mają problemu z ciepłem w tym zastosowaniu, ale nie dlatego, "
        "że robot pracuje tylko 30-60 minut — stałe czasowe nagrzewania małych "
        "serw to minuty, więc godzina to dla nich „w nieskończoność”. Powód "
        "jest inny:", Body))

    s.append(table(
        ["Stan", "Moment", "Uwaga"],
        [
            ["Leży (poza „loaf”)", "0,09 Nm", "spoczywa na podłodze"],
            ["Stoi", "0,70 Nm", "obciążenie ciągłe"],
            ["Idzie 0,1 m/s — mediana", "0,17 Nm", "przez większość czasu"],
            ["Idzie 0,1 m/s — 95. percentyl", "1,87 Nm", "krótkie szczyty"],
        ],
        [56 * mm, 30 * mm, 72 * mm],
        aligns={1: "CENTER"}))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Obciążenie ciągłe występuje tylko w <b>staniu</b>, i wynosi 0,70 Nm. "
        "Kot leżący nie obciąża napędów praktycznie wcale. Brief i tak zakłada "
        "tryb snu, więc jeśli robot kładzie się, gdy nic nie robi, problem "
        "znika z definicji — a nie przez ograniczenie czasu pracy.", Body))

    # ------------------------------------------------------------- serwa
    s.append(para("6. Co jest dostępne od ręki", H1))
    s.append(para(
        "Kryterium: magistrala szeregowa (12 napędów na jednej linii), "
        "sprzężenie zwrotne z pozycji, dostawa w dniach, nie tygodniach. "
        "Wszystkie poniższe są w Botlandzie z wysyłką w 24 h.", Body))

    s.append(table(
        ["Model", "Moment @12 V", "Napięcie", "Cena/szt.", "12 szt."],
        [
            ["ST3020", "2,45 Nm", "6–14 V", "~111 zł", "1332 zł"],
            [Paragraph("<b>ST3215</b>", CellB),
             Paragraph("<b>2,94 Nm</b>", CellB), "6–12,6 V",
             Paragraph("<b>109 zł</b>", CellB),
             Paragraph('<b><font color="#1c6b45">1308 zł</font></b>', CellB)],
            ["ST3215-HS", "1,96 Nm", "6–12,6 V", "—", "— (to wersja szybka)"],
            ["ST3235", "2,94 Nm", "—", "~240 zł", "2880 zł"],
            ["ST3025", "3,92 Nm", "6–12,6 V", "~415 zł", "4980 zł"],
        ],
        [30 * mm, 30 * mm, 28 * mm, 28 * mm, 42 * mm],
        aligns={1: "CENTER", 2: "CENTER", 3: "CENTER", 4: "CENTER"},
        highlight=[2]))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "Sprawdzono też, czy <b>wyższe napięcie</b> nie otworzyłoby taniej "
        "drogi do większego momentu. Nie otwiera: jedyne serwo z zapasem "
        "napięciowym (ST3020, do 14 V) ma najniższy moment bazowy i nawet "
        "wyciśnięte do 14 V daje 2,86 Nm — tyle samo co ST3215 przy 12 V, ale "
        "wymaga pakietu 4S z przetwornicą. ST3215-HS to pułapka nazwy: „HS” "
        "znaczy <i>high speed</i>, nie większa siła.", Body))

    # ------------------------------------------------------------ decyzja
    s.append(para("7. Decyzja", H1))
    s.append(callout(
        "Waveshare ST3215 — 12 sztuk, 1308 zł",
        "Wymaganie 1,87 Nm wobec 2,57 Nm na najgorszym możliwym poziomie "
        "naładowania. To <b>39% zapasu</b> w najgorszym punkcie i 65% na "
        "świeżej baterii. Robot zachowuje pełną postawę 24,2 cm — nie trzeba "
        "go przykucać ani zwężać rozstawu łap, choć obie te sztuczki zostały "
        "sprawdzone i działają, gdyby zapas okazał się potrzebny.",
        GOOD))

    s.append(Spacer(1, 3 * mm))
    s.append(para(
        "<b>Wersja 3 tego dokumentu rekomendowała Feetech STS3250</b>, bo "
        "liczyła zapotrzebowanie 3,42 Nm dla masy z symulacji. Ta liczba była "
        "poprawna dla robota ważącego 3,7 kg — tyle że taki robot nie "
        "powstanie. Rekomendacja STS3250 zostaje <b>wycofana</b>; nie jest "
        "błędna, jest po prostu policzona dla cięższego zwierzęcia.", Body))

    s.append(para(
        "Gabaryt i magistrala ST3215 i mocniejszych modeli są zgodne, więc "
        "jeśli gotowa konstrukcja okaże się cięższa niż zakładany szacunek, "
        "wymiana na ST3025 nie wymaga przeprojektowania mechaniki.", Body))

    s.append(para("Co zostaje otwarte", H2))
    s.append(table(
        ["", "Sprawa", "Dlaczego to jeszcze nie jest domknięte"],
        [
            ["1", "Masa wydruku PETG",
             "700 g to szacunek. Zważyć pierwszy wydruk — przy 1,2 kg "
             "całość rośnie do 2,5 kg, a wymóg do ~2,3 Nm (nadal w ST3215)"],
            ["2", "Wysokość z briefu",
             "„ok. 50 cm” kłóci się z „przypominał kota”. Potwierdzić, że "
             "chodziło o zwykłego kota, a nie o zwierzę wielkości rysia"],
            ["3", "IMU i zamknięcie pętli",
             "BNO085 jest na liście zakupowej, ale nie ma go jeszcze w "
             "symulacji — to następny krok programistyczny"],
            ["4", "Opory mechaniczne",
             "symulacja zakłada tarcie w przegubach bliskie zeru; realne "
             "łożyska i przekładnie dołożą obciążenia"],
        ],
        [10 * mm, 40 * mm, 108 * mm],
        aligns={0: "CENTER"}))

    s.append(Spacer(1, 5 * mm))
    s.append(callout(
        "Metodyka i jej granice",
        "Momenty odczytano z interfejsu stanu symulacji, po 9-15 tysięcy "
        "próbek na konfigurację; liczbą do doboru napędu jest 95. percentyl "
        "najbardziej obciążonego przegubu, nie chwilowy szczyt — szczyty to "
        "transjenty kontaktowe, które w prawdziwym robocie amortyzuje "
        "podatność mechaniczna. Odczyty potwierdzono niezależnie: moment w "
        "staniu skaluje się z masą liniowo i zgadza się z ręcznym rachunkiem "
        "z ciężaru i ramienia sił. Ceny są orientacyjne i pochodzą ze "
        "sprawdzenia ofert w sierpniu 2026.",
        MUTED))

    doc.build(s)
    print("written:", path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1])
