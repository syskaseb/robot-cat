# Przekroje i warstwy elektroniki

Otwórz [WAVEGO_electronics_sections.FCStd](WAVEGO_electronics_sections.FCStd).
To osobny, statyczny plik podglądowy: nie zmienia modelu konstrukcyjnego,
nie zawiera nowej mechaniki napędów i nie jest źródłem części do druku.

Uruchom [WAVEGO_Sections.FCMacro](../../../tools/freecad/WAVEGO_Sections.FCMacro),
aby wyświetlić panel z sześcioma widokami:

- [Przekrój boczny](section-side.png): odjęta połowa obudowy dla Y<0,
  elektronika zachowana w całości, bliższe nogi ukryte.
- [Dół](section-lower.png): LiPo, Pololu, druga przetwornica i IMU nad nią.
- [Środek](section-middle.png): komputer z rezerwą na HAT/chłodzenie,
  głośnik, listwa i rozłączenia przewodów.
- [Góra](section-upper.png): PCA9685, ReSpeaker, adapter magistrali, audio,
  dotyk i opcjonalny kondensator; niższe moduły ukryte.
- [Zasilanie](section-power.png): cztery oprawki nad listwą oraz rozłączenia,
  bez zasłaniających je wyższych modułów.
- [Głowa](section-head.png): kamera 23, IR 24, ToF 25 oraz rezerwy serw 21/22.

Przycisk **Caly kot / model konstrukcyjny** wraca do całego, nieprzeciętego
modelu. Przełączanie jest tylko zmianą widoku i aktywnego dokumentu.
W FreeCADzie: **Macro → Macros… → wybierz WAVEGO_Sections.FCMacro → Execute**.
Jeśli makra nie ma na liście, ustaw katalog makr na `tools/freecad` w tym repo.

Widoki z góry to rzuty wybranych warstw, nie przekroje jedną płaszczyzną Z.
Nakładanie się obrysów w rzucie nie dowodzi kolizji brył na różnych wysokościach.
Wszystkie pozycje pochodzą z modelu mechanicznego; niczego nie rozsuwano,
żeby pozornie uzyskać dopasowanie. Kolory opisują kategorie rezerw miejsca,
a nie materiały kupnych produktów. Identyfikatory odpowiadają
[components.json](components.json). Znane kolizje pozostają w
[validation.json](validation.json).

## Ogon: brak do uzupełnienia, nie ukończony napęd

Na tym etapie `CAT_Tail` jest przykręcony do nieruchomego `CAT_Tail_Mount`.
Fioletowe pole 26 jest tylko rezerwą serwa, bez połączenia z orczykiem.
Nie należy utożsamiać możliwości odkręcenia ogona z gotowym modułem napędowym.

Zamówiona poprawka ma obejmować odłączany moduł z serwem, uchwytem,
adapterem orczyka, nasadą ogona oraz rozłącznym przewodem, a także właściwe
połączenie obrotowe w modelu. Nie wykonano jeszcze tej poprawki.
Źródło aktualnego planu zakupowego (`docs/report/make_plan.py`, lista PARTS)
podaje tylko „3 × mikroserwo + Grove PCA9685” — dwie osie głowy i ogon.
Dokładny model serwa, geometria orczyka i osi wyjściowej nie są określone.
Potrzebne jest oznaczenie/link od użytkownika albo osobna decyzja o doborze
serwa; nie wolno dopasowywać uchwytu do zgadywanego gabarytu rezerwy 36×22×40 mm.
