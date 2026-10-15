# Aktualne odbiorniki wiązki korpusu

Jeden zestaw:4 zamienne Frame i7 osobnych CAP. Nie drukować ponownie
historycznych Frame fixed-source-supports ani ich starszych wariantów.
Model:ReceiverSupportsCurrent.FCStd; manifest.json przypina wszystkie
źródła/eksporty. Partial to odzyskiwanie sprzed próby parametrów, nie
drugi wybrany model.

Wynik1054,687s/339 nowych w pełni ograniczonych szkiców, poprawne pojedyncze
bryły/BOP0, CoreBoreRadius1,3→1,4→1,3 i ArmThickness4→4,2→4, przeniesiony
reopen.11STL zamkniętych, po1komponencie, bez non-manifold, mieszczą się
z5mm brim w256³. Bez slicera, wydruku, prób retencji ani zasilania.

Zachowane integralne podpory źródeł;22 grupy odbiorników,10 wcześniejszych
odciążeń feedów i niezależne FL_G/W025. W002 ma odciążenie na CAP D_FL.
G1/G2 należą do osobnej UpperCarrier z upper-fixed-feed-supports.
Nie obciążać lewarów WAGO ani kleju przewodami.

Wkład osprzętu:21T18I,1M2x14,1nakrętkaM2 według przypiętego
receiver-hardware-contribution.json. Feedów:11 blanków802534B po150mm,
1650mm nominalnie, nie wybrany cały stock. Nie dodawać śrub do integralnych
gałęzi. Zachowane śruby Frame/źródeł są we wcześniejszych pakietach i muszą
wejść do całościowego zestawienia.

Kolejność prototypu:

1. Zamontować Frame na zachowanych interfejsach przed prowadzeniem żył.
2. Przygotować i oznaczyć przewody na stole; długości dopiero po przymiarce.
3. Ułożyć izolowane sekcje w grupach, zamknąć właściwe CAP. RR_G ma śrubęM2
   i nakrętkę, nie opaskę wokół grupy.
4. Osobno sznurować krótkie feedy, nie gołe żyły/koszulki lapu/pady/lewary.
5. Przy demontażu podeprzeć przewody i zwolnić ich retencję. D_FL nie
   zdejmować z napiętymW002; głębsza naprawa odwraca montaż, nie hot-swap.

Pełny dostęp narzędzi, wspólny montaż pozostałych źródeł/25interfejsów,
stock i wybórW5 nadalOPEN.36tras i ten CAD nie są fizycznymPASS ani
ukończeniem całej fazy. Rzeczywisty wynik12/20=60%.
