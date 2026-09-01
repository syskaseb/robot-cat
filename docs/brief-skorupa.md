# Brief: skorupa robota-kota

Zadanie: zaprojektować **kosmetyczną powłokę** czworonożnego robota-kota tak,
żeby wyglądała jak żywy kot, a nie jak bochenek na patykach — i żeby dała się
wydrukować na FDM i złożyć.

To jest brief do przekazania komukolwiek, kto ma to zrobić. Zawiera wszystkie
liczby, których **nie wolno zmienić**, i wszystko, co jest wolne.

---

## 1. Dlaczego dotychczasowe podejście zawiodło

Skorupa jest zbudowana z **otoczek wypukłych kul** (`hull()` w OpenSCAD).
Daje to szczelne bryły i szybkie renderowanie, ale otoczka wypukła **nie
potrafi zrobić wklęsłości**. Suma brył wypukłych daje garby, nigdy wgłębienia.

Kot to w dużej mierze wklęsłości: wcięcie w talii za klatką piersiową,
zagłębienie przed łopatką, dołek u nasady szyi, policzek pod okiem. Żadnej z
nich tą metodą zrobić się nie da — i to jest przyczyna, dla której sylwetka
czyta się jak owad.

**Sugerowane rozwiązanie:** powłoka jako **loft przez przekroje** wzdłuż
kręgosłupa. Każdy przekrój to superelipsa z własną szerokością, wysokością i
wykładnikiem kształtu; wykładnik pozwala przechodzić od okrągłego do
prostokątnego, a ujemna krzywizna obwiedni daje talię. Siatkę można
wygenerować skryptem i wczytać do OpenSCAD-a przez `import()`, albo zrobić
całość w Blenderze. Powiązanie z symulacją musi zostać — patrz §2.

---

## 2. Liczby, których NIE WOLNO zmienić

Na nich policzono momenty na serwach i na nich zmierzono chód. Zmiana
którejkolwiek unieważnia cały dobór napędu.

| wielkość | wartość | skąd |
|---|---|---|
| pudełko tułowia | **300 × 111 × 141 mm** | `cat.urdf.xacro`, `body_length/width/height` |
| osie bioder | **x = ±110, y = ±55, z = 0** | `leg.xacro`, `mount_x`/`mount_y` |
| biodro → udo, w bok | **25 mm** | `hip_offset` w `leg_ik.py` |
| udo, oś–oś | **110 mm** | `thigh_length` |
| goleń, oś–łapa | **110 mm** | `calf_length` |
| promień łapy | **12 mm**, kula | `foot_radius`, kontakt w symulacji |
| wysokość postawy | 160 mm | `stance_height` |

Skorupa **musi się zmieścić w pudełku 300 × 111 × 141** i nie może zmienić
położenia żadnej osi.

## 3. Co jest wolne

Wszystko inne. Kształt przekroju, obwiednia, linie podziału, proporcje głowy,
pysk, uszy, ogon, osłony kończyn, obudowy stawów, faktura.

## 4. Zapas do nóg — zmierzony, nie założony

`hardware/cad/measure/envelope.py` przepuszcza przez prawdziwy kod chodu
każdą pozę, jaką robot potrafi zakomendować (marsz 0,10 m/s, pełny skręt,
stanie, przeciąganie, leżenie) i liczy, jak blisko osi symetrii zachodzi
kolano albo łapa:

- najbliżej: **|y| = 84,6 mm**
- połowa szerokości korpusu: **55,5 mm**
- **zapas: 29,1 mm**

Wniosek: noga **nigdy nie wchodzi pod korpus**, więc skorupa może być pełną,
gładką bryłą. Przebijają ją tylko cztery biodra. Po każdej zmianie parametrów
chodu uruchomić ten skrypt ponownie.

## 5. Serwo — wymiary zmierzone z oficjalnego CAD-u

Źródło: `TheRobotStudio/SO-ARM100`, plik `STEP/SO100/STS3215_03a.step`.
STEP trzyma otwory jako encje `CIRCLE`, więc to są liczby z pliku, nie pomiar
na oko. Metoda i surowe dane: `hardware/cad/measure/README.md`.

| wielkość | wartość |
|---|---|
| obudowa | 45,40 × 24,80 × **35,40** mm |
| całość z czopami | 39,60 mm |
| oś wyjściowa | **10,2 mm od bliższego czoła**, nie w środku |
| rozstaw śrub orczyka | **4 × Ø2,5 na okręgu Ø14,00**, co 90°, pod 45° |
| ten sam wzór od spodu | tak — serwo jest **dwuwałowe** |
| śruby obudowy | y = ±10,25; x = +4,2 / −16,5 / −20,3 |
| kołnierz wokół osi | Ø22,0, wystaje 1,8 mm |

**Dwuwałowość jest kluczowa.** Część ruchoma powinna być widelcem
obejmującym serwo: przykręconym do orczyka na jednym czole **i do czopu
jałowego na drugim**. Wtedy staw jest podparty obustronnie i nic nie wisi na
samym wale. Płaska płytka na czole orczyka **nigdy się nie zmieści** — bliższa
śruba obudowy leży 8,3 mm od osi, a część ruchoma potrzebuje minimum 10 mm
promienia na sam okrąg Ø14.

## 6. Pułapki, w które już wpadliśmy

1. **Stacje profilu to środki kul, nie punkty obrysu.** Stacja o promieniu *r*
   w *x* wystawia skorupę do *x ± r*. Rozstawienie ich jak punktów obrysu dało
   korpus 356 mm zamiast 300.
2. **Kołnierz robiony jako różnica dwóch otoczek wychodzi niemanifoldowy.**
   Element mocujący ma być **prymitywem przyciętym do korpusu** — jedno
   działanie logiczne z prostą bryłą.
3. **Wycinanie okienek w płaszczyźnie ścinania** psuje siatkę wzdłuż każdej
   krawędzi okienka. Zakładki dokładać *po* ścięciu, nie przed.
4. **Rama musi zmieścić się w skorupie.** Obecny `trunk_frame` ma 126 mm przy
   skorupie 109 — 1208 z 1640 wierzchołków leży na zewnątrz. **To jest nadal
   niedomknięte** i trzeba to naprawić przewężając szyny.
5. **Osłona biegnąca od stawu do stawu zlepia nogę w jedną masę.** Segmenty
   mają być krótsze niż rozstaw stawów, z widoczną przerwą — to rozdzielenie
   segmentów jest najsilniejszym efektem wizualnym.
6. **Oko z równikiem w otworze wystaje o cały promień.** Kulkę trzeba przyciąć
   powierzchnią czaszki odsuniętą o zadaną wypukłość.

## 7. Masa — to jest realne ograniczenie, nie kosmetyka

Skorupa waży dziś **425 g**, przy 412 g konstrukcji. Moment na najgorszym
serwie rośnie z 1,87 do 2,27 N·m, a zapas ST3215 przy wyczerpanej baterii
spada z 37% do **13%**.

Każdy dodany gram trzeba uzasadnić. Gramy na **machającej nodze** są
najdroższe — dokładają i do momentu podporowego, i do bezwładności wymachu.
Przelicza to `hardware/cad/measure/mass_check.py`.

## 8. Czego oczekujemy

- części **osobno**, każda jako własny plik, gotowa do slicera
- każda część: **jedna spójna, szczelna bryła** (`verify.py` to sprawdza)
- **bez podpór**, albo z jawnie podaną orientacją na stole
- połączenia **zdefiniowane** — śruba w konkretnym miejscu, wkładka, zatrzask.
  Nie „przykręć gdziekolwiek wypadnie"
- **długości śrub oznaczone jako do zmierzenia**, nie zgadnięte: zależą od
  tego, jak głęboko wchodzą oryginalne wkręty obudowy serwa

## 9. Punkt odniesienia dla wyglądu

Zdjęcie kota z projektu wstępnego. Co się na nim liczy, w kolejności:

1. **rozdzielone segmenty** — każdy człon to osobna zaokrąglona bryła, między
   nimi wyraźne, beczkowate obudowy stawów
2. **masywne kończyny** — wizualnie równie ważne co tułów
3. **pysk jako osobna bryła** ze stopniem względem policzków, brew nad nim
4. **duże wypukłe oczy** osadzone w oczodołach
5. **linie podziału** na tułowiu, łamiące masę
