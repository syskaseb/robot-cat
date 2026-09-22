# Próbki pasowania PETG — nie komplet wydruków robota

Edytowalny `PETGFit34.FCStd` i sześć osobnych STL w milimetrach:

| Plik | Wymiar sprawdzany |
|---|---|
| Seat220.stl | otwór Ø22,0 mm |
| Seat221.stl | otwór Ø22,1 mm |
| Seat222.stl | otwór Ø22,2 mm — obecny nominalny projekt |
| Journal78.stl | czop Ø7,8 mm |
| Journal79.stl | czop Ø7,9 mm — obecny nominalny projekt |
| Journal80.stl | czop Ø8,0 mm |

Pierścienie: Øzew28×7 mm. Czopy: kołnierz Ø11×3, występ10 mm,
otwór osiowy Ø3,4. Każdy STL jest pojedynczą bryłą; po imporcie do slicera
ustaw na stole. Osie pionowo jak w CAD; bez skalowania, na tym samym
profilu PETG, dyszy i ustawieniach co właściwy wydruk. Etykiety są
w nazwach, nie w geometrii — oznacz próbki po zdjęciu ze stołu.

Łącznie około8,7 g z pełnej objętości CAD przy1,27 g/cm³, bez brim/support;
rzeczywistą ilość pokaże slicer. Nie są to elementy do montażu w robocie.

Sprawdź prawdziwym 608ZZ i suwmiarką po ostygnięciu. Gniazdo ma utrzymać
zewnętrzny pierścień, a czop przejść przez wewnętrzny bez młotka. Zapisz
luz oraz możliwość obracania/wyjęcia. Nie wciskaj przez kulki, nie grzej
i nie uderzaj w łożysko; w razie zakleszczania wybierz luźniejszą próbkę.
Test nie kwalifikuje pełzania PETG, nośności, docisku bieżni ani trwałości.

Zmiana wymiaru po próbce wymaga edycji mastera i ponowienia kontroli
złożenia, nie jedynie przeskalowania STL. Szersze gniazdo może wymagać
innego sposobu ustalenia zewnętrznego pierścienia; wynik próby nie jest
sam w sobie zatwierdzeniem całego mechanizmu.
