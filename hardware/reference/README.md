# Geometria producentów — źródła do audytu, nie części do druku

## Nowa referencja społecznościowa MG92B — 23.09.2026

[Orczyk z projektu Dtto i kontrola miejsca przy ogonie](mg92b-horn-2026-09-23/README.md):
znaleziony model FreeCAD, wyodrębnione dwie bryły, pomiary i 72 warunkowe
próby położenia. To uproszczony model autora, **nie dokumentacja producenta**.
Nie zmieniono złożenia kota ani nie zatwierdzono sprzęgnięcia.

## Wcześniejsze źródła producentów

Pobrano 2026-09-21. Oryginalne archiwa zachowane bez zmian; rozpakowane
pliki są ignorowane w Git. Nazwy produktów i pliki należą do ich producentów.

SHA-256 archiwów:

```text
waveshare-bus-servo-adapter-a/source.zip
59f239a112e9efa91d5eb6d353e95b3ce7a4ccf7cd2500eacc8d7c389877e9d2
grove-pca9685/source.zip
ca73ab055bf7f847a4f5efef3a9ca8094eb16b75ce68b70c06fc69ebdc387e2f
```

## Waveshare Bus Servo Adapter (A), SKU 25514

- [Dokumentacja i link do STEP](https://docs.waveshare.com/Bus_Servo_Adapter_A/Resources-And-Documents).
- [Oryginalne archiwum](https://files.waveshare.com/wiki/Bus-Servo-Adapter-(A)/Bus%20Servo%20Adapter%20(A)_3D.zip).
- Lokalnie: `waveshare-bus-servo-adapter-a/source.zip`.
- [Wymiary producenta](https://docs.waveshare.com/Bus_Servo_Adapter_A):
  PCB nominalnie 42 × 33 mm, otwory Ø2,5 mm.
- STEP ma 117 brył; cały import **nie przechodzi `isValid()`**. Nie używać
  bezkrytycznie jako poprawnego modelu BRep. `supplier26.py` zapisuje wynik
  osobno dla każdej bryły. Przy testach przecięć wadliwe bryły zastępuje ich
  konserwatywnymi prostopadłościennymi obwiedniami, nie „naprawia” oryginału.
- STEP nie zawiera wpiętych przewodów i nie potwierdza dostępu narzędzia.

## Seeed Grove — 16-Channel PWM Driver (PCA9685)

- [Dokumentacja i pliki Eagle](https://wiki.seeedstudio.com/Grove-16-Channel_PWM_Driver-PCA9685/).
- [Oryginalne archiwum](https://files.seeedstudio.com/wiki/Grove-16-Channel_PWM_Driver-PCA9685/res/Grove%20-%2016-Channel%20PWM%20Driver%20(PCA9685).zip).
- Lokalnie: `grove-pca9685/source.zip`.
- Katalogowe 60 × 40 × 18 mm nie uwzględnia całego obrysu uszu w Eagle:
  warstwa Dimension szablonu `U2*3N` sięga ±32,1 i ±22,1 mm.
- Szablon na płytce (`U$1`) ma obrót R180. Współrzędne otworów trzeba
  przekształcić; nie wolno automatycznie przyjąć prostokątnego rastra.
- Montaż i obwiednie wtyczek nadal wymagają sprawdzenia z rzeczywistą płytką.

Rozpakowanie w PowerShell (bez nadpisywania istniejących źródeł):

```powershell
Expand-Archive -LiteralPath hardware/reference/waveshare-bus-servo-adapter-a/source.zip -DestinationPath hardware/reference/waveshare-bus-servo-adapter-a
Expand-Archive -LiteralPath hardware/reference/grove-pca9685/source.zip -DestinationPath hardware/reference/grove-pca9685
```

Weryfikacja geometrii: Python dostarczony z FreeCAD 1.1.3,
`tools/freecad/skorupa/probe26.py` i `supplier26.py`. Nie potrzebują ROS ani pixi.
