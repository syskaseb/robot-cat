#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Robot Cat - ekspansja: mapa domu i rozpoznawanie wizyjne."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

import os

_FONT_CANDIDATES = [
    os.path.expanduser("~/Library/Fonts"),          # macOS, Homebrew --cask font-dejavu
    "/Library/Fonts",                                # macOS, system-wide
    "/usr/share/fonts/truetype/dejavu",              # Debian/Ubuntu, apt fonts-dejavu-core
    "/usr/share/fonts/dejavu",                        # Fedora/RHEL
]


def _find_font_dir():
    for candidate in _FONT_CANDIDATES:
        if os.path.exists(os.path.join(candidate, "DejaVuSans.ttf")):
            return candidate
    try:
        import matplotlib
        mpl_dir = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
        if os.path.exists(os.path.join(mpl_dir, "DejaVuSans.ttf")):
            return mpl_dir
    except ImportError:
        pass
    sys.exit(
        "DejaVu Sans not found - needed for Polish diacritics, which reportlab's "
        "built-in Helvetica cannot render (they come out as black boxes).\n"
        "Install it:\n"
        "  brew install --cask font-dejavu          # macOS\n"
        "  apt install fonts-dejavu-core            # Debian/Ubuntu\n"
        "or run this from the ROS pixi env, which bundles it via matplotlib."
    )


FONT_DIR = _find_font_dir()
pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))

TEAL = colors.HexColor("#1B4B5A")
TEAL_TABLE = colors.HexColor("#1F5C6E")
ORANGE = colors.HexColor("#C8681A")
LIGHT = colors.HexColor("#F2EFEA")
ROW_ALT = colors.HexColor("#F7F7F7")
INK = colors.HexColor("#222222")

DOC_TITLE = "Robot Cat — ekspansja wizyjna"
DOC_DATE = "sierpień 2026"
FOOTER_NOTE = "Plan na przyszłość, zależny od decyzji Pi 5 — nic tu nie jest jeszcze kupione ani wdrożone"

styles = {}
styles["Title"] = ParagraphStyle("Title", fontName="DejaVu-Bold", fontSize=24, leading=28, textColor=TEAL, spaceAfter=4)
styles["Subtitle"] = ParagraphStyle("Subtitle", fontName="DejaVu-Bold", fontSize=12.5, leading=16, textColor=INK, spaceAfter=10)
styles["Body"] = ParagraphStyle("Body", fontName="DejaVu", fontSize=10, leading=14.5, textColor=INK, spaceAfter=8)
styles["H1"] = ParagraphStyle("H1", fontName="DejaVu-Bold", fontSize=14.5, leading=18, textColor=TEAL, spaceBefore=13, spaceAfter=7)
styles["H2"] = ParagraphStyle("H2", fontName="DejaVu-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=7, spaceAfter=5)
styles["CalloutTitle"] = ParagraphStyle("CalloutTitle", fontName="DejaVu-Bold", fontSize=10.5, leading=14, textColor=INK, spaceAfter=3)
styles["CalloutBody"] = ParagraphStyle("CalloutBody", fontName="DejaVu", fontSize=10, leading=14, textColor=INK)
styles["TableHead"] = ParagraphStyle("TableHead", fontName="DejaVu-Bold", fontSize=9, leading=12, textColor=colors.white)
styles["TableCell"] = ParagraphStyle("TableCell", fontName="DejaVu", fontSize=9, leading=12.5, textColor=INK)
styles["FootnoteRef"] = ParagraphStyle("FootnoteRef", fontName="DejaVu-Oblique", fontSize=8.3, leading=11.5, textColor=colors.HexColor("#555555"), spaceBefore=4)


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def callout(title, body_html):
    inner = Table([[p(title, "CalloutTitle")], [p(body_html, "CalloutBody")]], colWidths=[160 * mm])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
    ]))
    wrapper = Table([[inner]], colWidths=[168 * mm])
    wrapper.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return wrapper


def data_table(header, rows, col_widths):
    body = [[p(h, "TableHead") for h in header]]
    for r in rows:
        body.append([p(c, "TableCell") for c in r])
    t = Table(body, colWidths=col_widths, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_TABLE),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(body)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(ts))
    return t


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
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=18 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    story = []

    story.append(p("Robot Cat", "Title"))
    story.append(p("Ekspansja: mapa domu i rozpoznawanie wizyjne", "Subtitle"))
    story.append(p(
        "Punkt wyjścia: kamera (Camera Module 3), VL53L5CX i BNO085 są w planie zakupowym. "
        "<b>Raspberry Pi 5 + Raspberry Pi AI HAT+ 13 TOPS (Hailo-8L) nie są jeszcze zdecydowane</b> "
        "— plan zakupowy wciąż zakłada Pi 4B bez akceleratora (patrz plan-zakupowy.pdf). Cała "
        "ekspansja opisana tu wymaga tej zmiany, bo Pi 4B nie ma złącza PCIe na Hailo. Ten "
        "dokument rozpisuje, czego jeszcze brakuje, żeby dojść od „ma kamerę” do „idź do pokoju A, "
        "zobacz co jest na stole” — <b>pod warunkiem</b>, że Pi 5 + HAT zostaną kupione."
    ))
    story.append(Spacer(1, 4))
    story.append(callout(
        "Wniosek w jednym zdaniu",
        "Brakujące warstwy to mapowanie (SLAM wizyjny), nazwane miejsca na mapie, rozpoznawanie "
        "obiektów i prosty sekwencer łączący je w jedną komendę — żadna z nich nie wymaga nowego "
        "sprzętu ponad Pi 5 + Hailo-8L, którego zakup jest osobną, wciąż otwartą decyzją, i żadna "
        "nie działa w izolacji od reszty.",
    ))
    story.append(Spacer(1, 6))

    story.append(p("1. Cztery warstwy między „ma kamerę” a „rozumie dom”", "H1"))
    story.append(data_table(
        ["Warstwa", "Zadanie", "Bez tego..."],
        [
            ["Mapowanie (SLAM)", "zbudować mapę pomieszczeń z kamery + IMU", "robot nie wie, gdzie jest ani jak wygląda dom"],
            ["Nazwane miejsca", "powiązać obszar mapy z etykietą „pokój A”", "mapa jest, ale nie da się do niej odwołać po nazwie"],
            ["Rozpoznawanie obiektów", "wykryć i zaklasyfikować to, co widzi kamera", "robot dojedzie, ale nie powie, co widzi na stole"],
            ["Sekwencer zadań", "połączyć „jedź” + „rozpoznaj” w jedną komendę", "trzeba by to odpalać ręcznie, krok po kroku"],
        ],
        [40 * mm, 68 * mm, 60 * mm],
    ))
    story.append(Spacer(1, 8))

    story.append(p("2. Mapowanie: SLAM wizyjny", "H1"))
    story.append(p(
        "Bez LiDAR-u (decyzja podjęta wcześniej) mapowanie musi iść z kamery i IMU, które już mamy "
        "w planie. To dokładnie do czego służy <b>RTAB-Map</b> — pakiet ROS 2 do wizyjnego SLAM-u, z "
        "potwierdzonym wsparciem dla Jazzy. Buduje mapę 3D albo czystą siatkę zajętości 2D (do "
        "nawigacji) z jednej kamery RGB i danych IMU, wykorzystując wykrywanie zamknięć pętli "
        "(rozpoznawanie „już tu byłem”), żeby mapa się nie rozjeżdżała przy dłuższym chodzeniu."
    ))
    story.append(p(
        "<b>Przykład:</b> rtabmap_ros odbiera obraz z kamery i dane z BNO085, i publikuje gotową "
        "siatkę zajętości na topicu, którego Nav2 używa bezpośrednio do planowania trasy — nie trzeba "
        "pisać własnego mapowania od zera.",
        "FootnoteRef",
    ))
    story.append(Spacer(1, 6))

    story.append(p("3. Nazwane miejsca i dojście do nich", "H1"))
    story.append(p(
        "Gdy mapa istnieje, Nav2 (standardowy stos nawigacji ROS 2) umie dojechać do zadanej pozycji "
        "(x, y) na tej mapie. „Pokój A” to w praktyce współrzędne zapisane raz — najprościej: "
        "przejechać robotem po domu ręcznie jeden raz, zaznaczyć środek każdego pokoju jako punkt "
        "nazwany, i zapisać. Komenda „idź do pokoju A” to wtedy jedno wywołanie Nav2 z zapisanymi "
        "współrzędnymi, nie nowy problem nawigacyjny."
    ))
    story.append(Spacer(1, 8))

    story.append(p("4. Rozpoznawanie obiektów — z jednym uczciwym zastrzeżeniem", "H1"))
    story.append(p(
        "Standardowy <b>YOLOv8</b>, skompilowany pod Hailo-8L (ten sam model, którego FPS mierzyliśmy "
        "wcześniej — ~137 FPS dla wariantu n) rozpoznaje 80 klas ze zbioru COCO, co obejmuje większość "
        "typowych przedmiotów na stole: kubek, telefon, laptop, książkę, pilot, klawiaturę, butelkę. "
        "To jest gotowe do użycia dziś, bez dodatkowego treningu."
    ))
    story.append(callout(
        "Czego jeszcze nie da się zrobić",
        "Prawdziwie otwarte rozpoznawanie „zobacz cokolwiek, po nazwie, bez wcześniej ustalonej listy” "
        "(modele typu YOLO-World) <b>nie jest jeszcze wspierane na Hailo-8/8L</b> — Ultralytics "
        "wprost odrzuca tę rodzinę modeli przy eksporcie pod ten akcelerator. Na start trzeba więc "
        "zamknięcia się w zestawie klas COCO, nie w swobodnym „co to jest” dla dowolnego przedmiotu. "
        "To się może zmienić z kolejną wersją oprogramowania Hailo — wart sprawdzenia przy realizacji, "
        "nie zakładania na dziś.",
    ))
    story.append(p(
        "<b>Przykład:</b> węzeł ROS 2 odbiera klatkę z kamery, przepuszcza ją przez YOLOv8 na Hailo-8L, "
        "i publikuje listę wykrytych obiektów z pozycją w kadrze — dokładnie to demonstruje "
        "hailo-rpi5-examples, oficjalny zestaw przykładów Hailo na Raspberry Pi 5.",
        "FootnoteRef",
    ))
    story.append(Spacer(1, 8))

    story.append(p("5. Sekwencer: „idź do pokoju A, zobacz co jest na stole”", "H1"))
    story.append(p(
        "Ostatni element to nie nowy model, tylko kolejność wywołań: (1) Nav2 dojeżdża do zapisanej "
        "pozycji pokoju A, (2) po dojechaniu robot obraca głowę w stronę stołu (mikroserwo już w "
        "planie), (3) węzeł YOLOv8 rozpoznaje klatkę i zwraca listę obiektów. To da się złożyć jako "
        "prosty skrypt Python wywołujący akcje ROS 2 po kolei — nie wymaga własnego frameworku do "
        "planowania zadań na tym etapie."
    ))
    story.append(Spacer(1, 8))

    story.append(p("6. Koszt energetyczny tej ekspansji", "H1"))
    story.append(p(
        "Hailo-8L dolicza 1–1,5 W aktywnego liczenia do budżetu, który już liczy ~50–70 W z samych "
        "serw — zaokrąglenie błędu pomiaru, nie realna zmiana czasu pracy na baterii. Tabela czasu "
        "pracy z dokumentu o napędach (3000 mAh → ~30-36 min, 5000 mAh → ~50-60 min) obowiązuje "
        "bez zmian z tą ekspansją."
    ))
    story.append(Spacer(1, 8))

    story.append(callout(
        "Co ten dokument świadomie pomija",
        "Konkretne parametry RTAB-Map (rozmiar mapy, częstotliwość zamknięć pętli), sposób "
        "etykietowania pokoi w interfejsie użytkownika, i finetuning YOLOv8 pod niestandardowe klasy "
        "(np. konkretne przedmioty domowe poza zbiorem COCO) — to decyzje do podjęcia przy "
        "implementacji, nie teraz. Żadna z czterech warstw nie jest jeszcze wdrożona; to plan, nie stan.",
    ))

    doc.build(story)
    print("written:", path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "docs/ekspansja-wizyjna.pdf")

