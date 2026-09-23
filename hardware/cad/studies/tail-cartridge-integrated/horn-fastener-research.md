# MG92B — dalsze źródła mocowania orczyka

Sprawdzono 23.09.2026. Informacje poniżej **nie zostały użyte do wygenerowania
niezweryfikowanego wieloklinu ani śruby w CAD**. Nie jest to nowy dobór zakupowy.

- [Adafruit 2307](https://www.adafruit.com/product/2307), aktualna karta
  sprzedawanego MG92B: 20 zębów wieloklinu. Nie podaje wymiarów śruby
  orczyka, jej łba, długości zazębienia ani geometrii zębów. Liczba zębów
  nie wystarcza do zaprojektowania pasującego gniazda.
- [Odpowiedź wsparcia Adafruit z 16.01.2017](https://forums.adafruit.com/viewtopic.php?t=109955)
  opisuje wałek Ø4,8 z 20 zębami. Treść była dostępna w indeksie wyszukiwarki;
  bezpośrednie pobranie strony zwróciło 403. Historyczna wskazówka dla produktu
  Adafruit, nie rysunek tolerowany ani potwierdzenie aktualnej partii Botland.
- [BOM autora SmallpTsai](https://github.com/SmallpTsai/hexapod-v2-7697/blob/master/mechanism/BOM.md)
  dla hexapod-v2-7697 używającego 18 MG92B przypisuje M2×6 do ramienia serwa
  (po jednej na serwo). **Kandydat do weryfikacji**, nie dokumentacja fabrycznej
  śruby: nie określa gniazda, średnicy/wysokości łba, fazy ani głębokości otworu
  wałka. Nie wiadomo z tego wpisu, czy chodzi o dostarczoną śrubę, czy zamiennik.
  Nie pobrano i nie włączono geometrii ani kodu tego projektu (GPL-3.0).

Wniosek projektowy: zachować demontowalny fabryczny orczyk, osiowy dostęp do
jego śruby i możliwość jej wcześniejszego założenia. Nie zatwierdzać śruby
M2×6 tylko z BOM-u innej konstrukcji i nie kopiować na nią wymiarów nominalnych
M2×10, którymi skręcamy nasz adapter. To dwa różne połączenia.
