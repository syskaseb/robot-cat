# ReSpeaker Lite — model źródłowy i pomiary, 22.09.2026

**Materiał referencyjny, nie integracja do kota ani zgoda do druku.**
Złożenie v32, jego jointy, masy oraz 17 prób Gazebo pozostają bez zmian.

Pobrano [oryginalny STEP Seeed](https://files.seeedstudio.com/wiki/respeakerv3/ReSpeakerLitev1.1.step),
bez skalowania i przeróbek, przez odnośnik „ReSpeaker Lite 3D file”
z [oficjalnego wiki](https://wiki.seeedstudio.com/reSpeaker_usb_v3/#resource).
Plik: [ReSpeakerLitev1.1.step](ReSpeakerLitev1.1.step), podpis
[source.sha256](source.sha256). Pobrano22.09.2026 około06:38 Europe/Warsaw.
STEP oznacza rewizję **v1.1** i ma jednostkę milimetr.

## Co rzeczywiście wynika z modelu

484 poprawne bryły. Największa to laminat:

| Obiekt | Obwiednia źródłowa XYZ, mm |
|---|---|
| PCB | około 82,024 × 34,007 × 1,51 |
| Cały STEP ze złączami | około 83,602 × 34,007 × 10,93 |
| Wysokość względem spodu laminatu | Z=−2,585 do+8,345 |
| Stara obwiednia w kocie | 35 ×86 ×12 |

**Wiki podaje 35×86 mm, co nie zgadza się dokładnie z tym STEP-em.**
Nie rozstrzygnięto, czy to zaokrąglona specyfikacja, inna rewizja, czy błąd
modelu. Nie skalować pliku i nie obiecywać zgodności zakupionego modułu.
Przed zatwierdzeniem uchwytu sprawdzić zdjęcie rewizji i wymiar fizyczny.

Dwa pełne otwory Ø2,2 mm przechodzą przez laminat 1,51 mm. W oryginalnym
układzie źródła ich środki na Z=0 to:

- [100,44; −105,295; 0] mm;
- [42,73; −76,375; 0] mm.

To mocowanie po przekątnej, **nie wzór czterech narożnych śrub**.
Zaokrąglenia krawędzi oraz małe pola lutownicze nie są otworami montażowymi.
[Widok od góry](step-top.png) i [od spodu](step-bottom.png) pochodzą
z importu tego STEP przez MCP FreeCAD, nie z wygenerowanej ilustracji.
Zielony laminat i szare elementy są kolorami podglądu, nie BOM-em materiałów.

## Próby położenia i dalsza praca

[measurements.json](measurements.json) mierzy dwa ustawienia ±90° wokół Z,
z długą krawędzią w poprzek głowy. Środek PCB jest w [−142,5;0;139,6] mm.
Sprawdzana jest **konserwatywna obwiednia całego STEP względem rzeczywistych
brył v32**, nie pełne przecięcia wszystkich 484 drobnych elementów.
Pierwszą próbę bezpośrednich szczegółowych przecięć przerwano z powodu
kosztu obliczeń. Zastąpiono ją dwuetapowym sprawdzeniem: zerowe przecięcia
obwiedni wykluczają kontakt, a dodatnie wymagają analizy dokładnej.

Obwiednia nie przecina obu połówek głowy, ale wchodzi w dolne rejony
uszu i wkładek. [Drugi, dokładny etap](detailed-contacts.json) zbadał
wszystkie osiem takich wskazań w dwóch pozycjach: **43 pary brył, zero
rzeczywistych przecięć materiału**. W tych miejscach pudełko zawierało
pustą przestrzeń pomiędzy elementami płytki. To nominalna kontrola dwóch
statycznych ustawień bez kabli, nie gwarancja luzów montażowych ani ruchu.

Weryfikacja nie obejmuje wetkniętych kabli USB/audio, dodatkowego XIAO,
akustycznych kanałów w skorupie, rzeczywistych dystansów/śrub, wiązek
przy ruchomej głowie ani dostępu do przycisków. Nie nadano nowego
fizycznego znaczenia `Fix_Microphones`, który w v32 pozostaje TEMP.
Nie przeliczano gęstości całego STEP jako PETG ani nie zastąpiono zapasu masy.

Odtworzenie: `tools/freecad/skorupa/measure_head_electronics.py`, następnie
`check_respeaker_contacts.py` z tego samego katalogu, w Pythonie FreeCAD
po odtworzeniu `cache32.py`. Skrypty sprawdzają SHA źródła i kota; zapisują
wyłącznie raporty referencyjne. Nie zapisują dokumentu kota.
