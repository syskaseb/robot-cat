# Wyłącznik baterii bez klucza

Zmiana do pakietu WAVEGO 25. Bezpiecznik główny F0 30 A zostaje tuż za XT60. Wyłącznik rozłącza dodatnią żyłę przed rozdziałem zasilania. Klapka baterii zachowuje swoją funkcję, a XT60 służy do odłączania baterii na czas montażu i wyjmowania.

**BAT+ → XT60 → F0 30 A → POST_F0 → S0 → P_SYS.** Ujemny tor baterii pozostaje według mapy pakietu. S1 zachowuje rolę odłącznika napędów. [Mapa połączeń pakietu 25](../source/POLACZENIA.csv)

| Zmiana | Część lub połączenie |
|---|---|
| S0 | Carling BA1-A0-03-650-511-C, jednobiegunowy wyłącznik dźwigniowy ON/OFF 50 A w wersji DC Switch Only. Napięcie pakietu dochodzi do 12,6 V i mieści się w zakresie karty serii dla tej wersji. Mocowanie 6-32, zaciski 10-32. Dostępność egzemplarza pozostaje do potwierdzenia. |
| Zaciski S0 | 2 × TE 8-35109-0, oczka pod śrubę #10 do istniejącego przewodu HELU 23802 4 mm². Każdy gotowy zacisk osłonić, także głowę śruby i odsłoniętą część oczka. Oparcie całej powierzchni oczka i pełny docisk sprawdzić na rzeczywistym zacisku. |
| W076/custom | POST_F0.2 → S0 LINE. Fabryczny odcinek F0 → POST_F0.1 zostaje w całości. |
| W066 | S0 LOAD → P_SYS.1. |

Stare długości 389 i 260 mm oraz oczka M10 dotyczą układu z kluczykiem. Długości W076/custom i W066 ustalić po przymiarce wyłącznika, obu osłoniętych zacisków i trasy pod zamkniętą klapką. Zachować podparcie na izolacji przewodów.

### Pierwsza przymiarka

1. Przy odłączonej baterii i USB przymierzyć wyłącznik z obiema śrubami mocowania, dwoma zaciśniętymi i osłoniętymi oczkami oraz klapką. Dźwignia ma być dostępna palcem w obu pozycjach. Sprawdzić, czy złożone zaciski mają dostęp dla wkrętaka i niczego nie dotykają.
2. Sprawdzić, czy można rozpiąć XT60 i wyjąć cały pakiet bez napinania obu żył i bez kontaktu z zaciskami. Dopiero wtedy ustalić długości do cięcia.
3. Przed podłączeniem baterii sprawdzić miernikiem ciągłość toru w pozycji ON i rozłączenie w pozycji OFF oraz brak zwarcia do masy. Przy pierwszym uruchomieniu zostawić S1 w pozycji OFF i zmierzyć prąd załączenia. Przy normalnym wyłączaniu zatrzymać napędy, przestawić S1 na OFF, zamknąć system Raspberry Pi i wyłączyć S0. XT60 rozpiąć po wyłączeniu S0.

[Wyłącznik Carling](https://www.carlingtech.com/eParts-catalog/b-series-hydraulic-magnetic-circuit-breakers/BA1-A0-03-650-511-C) · [Karta serii B](https://www.carlingtech.com/sites/default/files/documents/b-series_datasheet.pdf) · [Oczko TE](https://www.te.com/en/product-8-35109-0.html)
