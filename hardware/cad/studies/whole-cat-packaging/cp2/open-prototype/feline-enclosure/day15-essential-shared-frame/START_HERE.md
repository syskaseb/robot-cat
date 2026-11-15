# START — wspólna rama, etap CAD do przymiarki

**HOLD — NIE ZWALNIAĆ RAMY DO DRUKU:** tylny prawy pełny łeb M3x10 ma validcommon2,918676287mm³ z MAIN_Pololu4853/gap0. Potrzebna inna kompletna realizacja tego połączenia przy zachowanej płytce, nie skrócenie łba. Reszta po tej pierwszej przyczynie jest NIEODEBRANA. Region audio przyjęty wyłącznie lokalnie.

**Bieżący dokument:** `shared-frame.FCStd`. `frame-result.json` rozstrzyga odbiór nowych interfejsów; jeśli ma HOLD, tych STL nie traktować jako zwolnionego zestawu. Zamrożona podstawa `day14-fasttrack-first-fit/fit-kit-ready` pozostaje bez zmian, zaczyna się od P00/8 rzeczywistych osi. Nie ma fizycznego testu gwintu/masy/ruchu.

## Zamknięty lokalny problem audio

Nie utrwalono własnegoR14. Z górnego dojściaZ131, zakresu chłodzenia/ramki, rzeczywistych odsunięć7profili i minimalnychRcore6,4/8,4 wynika wspólny przedziałRosi10,45..17mm. WybranoR12; coreRmin9,3. Odcinek przyAMP jest przed górnym łukiem, a jego początek119mm jest5mm nad rozgałęzieniem114mm. Całeprofile+0,4 mają84/84 dodatnie relacje do wybranych sąsiadów, minimum2,38mm; kanałpełnejpojemności7 ma1,30mm, a21/21nominalnychodstępów co najmniej0,2mm. Zasada1,25 zachowana. To lokalne przyjęcie tego konkretnego pola, nie całego gotowego harnessu/leadstock.

Przez feed idą rzeczywiście2speakerBTL, z góry5PiI2S/zasilanie/masa. AniBTL nie jest masą. AMPpady/header/kierunki, PiGPIOwyjście i terminale/długość głośnika są jawnym nominalnym założeniemFIT. Lokalne długości nie są długością całychkabli/cięciem. USB_AUDIO osobny, bez drugiego kredytu500DelockBUS. Cztery niezależne220/obaMTA/FHAC>=84,5/K1474/pełnekońce iE1solder zachowane.

## Realne części i śruby

- P10/P11: przedni/tylnyportal ze wspólnymi górnymi szczękami czterech zachowanych zacisków. P16:2przednie dolne szczęki (dokładnyflip0/0). P17/P18: po1różnej tylnej dolnej szczęce; nie zastępować jednej drugą — lustrzana różnica15,5/30,725mm³. Nie ma fuzji z kupnym WAVEGO ani wiercenia jego ramy.
- P12: wspólny środek z półką głośnika, standoffamiPi i strefami podparcia logiki. Przednie skrzydło tacki i jeden standoff należą doP10; ich pozycja/kształt zachowane. To rzeczywisty podział, nie luźny odcięty fragment.
- Cztery złącza środkaportal: integralne półzakładki, pełna śruba/nakrętka/dwiepodkładki. DwaM3x12 i dwaM3x10. Przedni ujemny interfejs ma wydłużony wspólny język do obszaru pozaBNO; rawC0BNOcommon1,6539166 zachowany. Nie zmieniono BNO ani otworówPi.
- P13: zdejmowany mostekBUS na dwóch pełnych M3x16 do integralnych uszuP12. Jego31mm separacji odPi nie zamieniono w nowe pasowanie fizyczne.
- P14: stała prawa belkaTTP223. P15: osobna lewa belka+podparcieReSpeaker. DwieparyM3x12 na rzeczywistych dolnych zakładkach do poprzeczek portalów. Żadnej drukowanej części nie sfuzowano z drugą; rzeczywiste wspólne objętości części wynoszą0.

Komplet nowych standardowych zestawów:10śrub/10nakrętek/20podkładek. Zachowane czteryzaciski dodają4śruby/4nakrętki/4podkładki — nie dublować ich przy zamówieniu/listowaniu. Modele mają pełny trzon/czubek/łeb i całą nakrętkę; wymiary nominalne wCSV/JSON. Zapas i rzeczywisty gwint niepotwierdzone, nic nie kupiono. Osobna retencja PCB i bezpieczne chwytaki audio są NEXT, nie ukryte w etapie ramy.

## Dwie osoby, otwarte układanie

1. P00 i rzeczywista8-osiowa rama: FIT1 rewizja/gwint/masa/ruch. A trzyma ramę, B składa dolne szczęki i portale na zachowanych kompletnych zestawach. Banki/WAGO i krótkie połączone końce układać otwarcie, bez wirtualnego rozpinania lutów.
2. Połączyć P12 z portalami na stole bezPCB. Pełny dostęp boczny do śrub PRZED MAIN/AUX/Pi/pionowąlogiką; późniejsza rzadka naprawa może wymagać zdjęcia płytki. Nie prowadzić narzędzia przez zamontowany MAIN.
3. Ułożyć parę głośnika przez otwarty kanał, potem pięć przewodów od góry przyAMP. Dużych fabrycznych obudów nie przeciągać przez zamknięty otwór. PCB/końce/E1 lutowane zachowane; dociski krawędziowe dopiero po układaniu i potwierdzeniu rzeczywistych keepout.
4. P14/TTP223 przykręcić jako stałą prawąbelkę. Jego przewód doE1 zostaje w stałej bocznej strefie, pozycja złączy nie zmienia się przy baterii — nie założono nowej odpinki ani zapasu do parkowania. Ułożyć ten przewód przed dociskami i sprawdzić rzeczywistą długośćFIT2.
5. P13/BUS i P15/mikrofon zamykać na końcu. Przy baterii: odłączyć istniejący rzeczywistyUSB_AUDIO, zdjąć dwa leweM3 i P15/ReSpeaker; odłączyć istniejąceUSB/zasilanieBUS, odkręcić dwaM3mostka i wyjąćP13; odłączoną baterię przesunąć do lewego otwartego miejsca i podnieść. P14 i dotyk pozostają. To wiarygodna kolejność otwartych części; pełne fizyczne końce, długości i próba wyjęcia należą doFIT2, nie szybki serwis ani wykonana czynność sprzętowa.

## Druk i dalszy zakres

Eksporty obejmują WYŁĄCZNIE nasze rzeczywiste części P10..P18. Własny lokalnyXYZ zZ0, każdy wymiar<256mm; zamknięcie siatki i dodatniaobjętość wmesh-check. Współrzędne złożenia wFCStd/partingJSON. Portale mają żebra/zakładki, P12 podwieszenia półki: ocenić podpory przy rzeczywistym slicerpreview w przyszłości, nie nazywać całego zestawu płaskim bez tej próby. Nie uruchamiano slicera/druku.

Nie dociskać niewidocznych elementówAMP/Pi ani membrany głośnika/mikrofonu. Strefy chwytu i otwory akustyczne są nazwanym fizycznym FIT/coupon; bez komory akustycznej ani bramki rozpoznawania mowy. Po odebranej ramie potrzebne: proste bezpieczne edgekeepers/izolujące dystanse, retencja banków/baterii i rzeczywisty stock/ends. FIT3obrysOli/głowa/ogon/otworyosłony pozostaje. Cały robot nie jest przyjęty ani zasilony; actualcut/installedfit/slackNULL. StareHOLDy nie zostały skasowane.

Aktualny milestone:9typów STL/10drukowanych sztuk,9zamkniętych dodatnich siatek<256;6głównych druków rozłączneobjętościowo/15par0,4górneszczęki zachowane0missing. C0BNO1,6539166 zachowany; C1MAIN2,9186763 kończy tę realizację połączenia, nie całą architekturę. Użyteczne pliki są zapisem inżynierskim HOLD, nie alternatywą instrukcji podstawy.
