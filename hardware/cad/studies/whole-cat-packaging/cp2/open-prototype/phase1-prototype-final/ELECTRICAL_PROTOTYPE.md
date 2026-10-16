# E3: nominalny dobór prototypu, nie odbiór elektryczny

PakietGEA223S30X6GT to zwykłyLiPo3S2200mAh30C:11,1V nominalne/12,6V pełne,
nie4S/LiHV.30C nie jest ograniczeniem zwarcia. Zachowany alarm cel nie odcina
baterii; brakBMS/GUARD i konieczność operatora są jawne.

WaveshareST3215 to wariant12V:0,2A bez obciążenia/0,9A znamionowo/2,7A stall.
To punkty katalogowe, nie pomiar chodu. Adafruit0,85A MG92B przy4,8V to
oszacowanie. Skalowanie0,85×6/4,8=1,0625A służy tylko wrażliwości, nie jest
gwarancją przy6V. Trzy takie wartości3,1875A przekraczają budżetAUX3A.
Analogiczne kableArmDojo5264 opisano jako26AWG/silikon; nie jest to dowód
przekroju/obciążalności naszych Waveshare. Model3D również tego nie dowodzi.

MAIN4853=D30V33MAL: nastawa projektowa5,10V, Pi/USBłącznie3A.
AUX4092=D36V50F6: osobne6V, łączny budżet3A. Nie łączyć wyjść równolegle.
80%sprawności/VIN9V/10mAdodatku są założeniami obliczeń wejść, nie gwarancją
ani progiem rozładowania. Zachowane kryteria poszczególnych cel obowiązują.

Zachowane23wkładki: F030A,4grupoweMiniVAL10A,12serw4A,F_PI3A,F_AUX4A,
3małe serwa1A,F_PWM0,1A. Wartości/oprawki/przewody/CAD bez zmian.
Pełne role, numery, rachunki i ograniczenia: assessment.json.
20A całego robota to budżet, NIE limiter. Same12zablokowanychST3215=32,4A.
4Afuse nie musi wyłączyć serwa stall2,7A;30AF0 też nie chroni przed każdym
przeciążeniem. Nie dopuszczamy allstall ani testów przez blokowanie wałów.

F0 ma32VDC/1000A, ale granica zwarcia pakietu nie jest potwierdzona.
Hipotetyczne Rcałego toru10/20/40mΩ dają12,6V/R=1260/630/315A; pierwszy
przekracza1000A. To scenariusze, nie pomiar ani zatwierdzony zakres baterii.
Nie wykonywać zwarćLiPo. Krótki odcinek przed wkładką nie jest automatycznie
termicznie chroniony; większa wkładka nie jest naprawą przepalania starej.

S821:30A/30VDC rezystancyjne, nie ratingACmotor ani modelS821D. Pololu
deklaruje softstart/ochrony modułów, nie pełną ochronę każdej żyły ani
zdolność pochłaniania dowolnej energii wstecznej.

## Obowiązkowe bramki fazy2 przed próbami zLiPo

1. **Źródło:** obronna granica zwarcia kompletnego toru zgodna z dokładną
   wkładką/oprawkąF0. Jeśli przekroczona lub nieustalona, nie podłączaćLiPo;
   potrzebna kwalifikacja/rewizja, nie30C lub pojedynczy odczytIR z ładowarki.
2. **Żyły/styki:** ustalić dostarczone przekroje, izolację i styki15serw oraz
   cienkich końców. Sprawdzić polaryzację/izolację/odciążenia, rzeczywiste
   limity i temperatury. Brak danych wymaga kompetentnej kwalifikacji na
   kontrolowanym źródle, nie zgadywania na surowym pakiecie.
3. **Koordynacja:** czasy/energia wyłączenia zgodne z limitami każdej żyły,
   także przedF_PI/F_AUX/F_PWM; sprawdzić rozruch i przepalanie wkładek.
   Nie zwiększać amperażu bez ponownego doboru. Pełna selektywność10A/4A
   nie jest dodatkowym celem hobbystycznego prototypu.
4. **DC/termika:** sprawdzić rozruch/zatrzymanie, skoki napięć, energię
   wsteczną i działanieS821. Projektowy budżet20A i MAIN/AUX3A nie mogą
   być przekroczone w dopuszczonych próbach; temperatury poniżej niższych
   rzeczywistych limitów części/izolacji/PETG z zapasem. Przekroczenie lub
   nieznany limit oznaczaSTOP i rewizję, nie zgodę na dalszy chód.

Pierwsze kontrole na odłączonym układzie. Dalsze próby wymagają osobnej zgody
i kontrolowanego zasilania/warunków dobranych przez osobę kompetentną.
Żadnej z tych bramek tu nie wykonano. Dokumentacja fazy1 może być kompletna,
choć kwalifikacja elektryczna i fizyczne bramki nadal sąOPEN.

## Źródła, różna siła dowodu

- Pakiet: https://gensace.de/products/gens-ace-g-tech-soaring-2200mah-11-1v-30c-3s1p-lipo-battery-pack-with-xt60-plug
- ST3215, nie wersja7,4V: https://docs.waveshare.com/ST3215_Servo
- SzacunekMG92B: https://forums.adafruit.com/viewtopic.php?t=104598
- MG92B: https://towerpro.com.tw/product/mg92b/
- Analogiczne kable, nie nasz certyfikat: https://armdojo.com/products/feetech-servo-cable-set-3-pin-5264
- MAIN: https://www.pololu.com/product/4853
- AUX: https://www.pololu.com/product/4092
- S821: https://www.nkkswitches.com/pdf/stoggleshighcap.pdf
- Przypięte karty wkładek: hardware/electronics/full-cat/protection-selection-r2/sources.json
