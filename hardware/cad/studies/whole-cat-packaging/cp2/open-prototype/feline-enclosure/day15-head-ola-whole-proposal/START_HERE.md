# Głowa i sylwetka Oli — jedna propozycja całości

**PROPOSED_NOT_PRINTSKIN. Brak odbioru korzenia głowy i carriera. Nie drukować tych obwiedni.**

Zacznij od `whole-opaque-side.png` i `whole-opaque-front-three-quarter.png`. To rzeczywiste widoki tego samego modelu; stopy, ogon i twarz są w kadrze. Nie schowano wystających kupnych części dla urody. Zamrożony model widoków: `opaque-proposal-snapshot.FCStd`, piny i kamery w `snapshot-source-pins.json`. Bieżący model: `head-ola-proposal.FCStd`.

Zmiany: krótki blend barki–tył głowy, wspólna maska policzków z otwartymi pełnymi nominalnymi polami Camera3/ToF, łagodniejszy dół boków. Grzbiet i długość ogona zachowane. Osobne otwarcie tylnej obwiedni zostawia strefę S0; nie jest odbiorem rzeczywistej obsługi klucza. Wszystkie kupne moduły/końce i ich pozy pozostają. 6 aktualnych par kosmetyka–pełny nominalny sensor ma validcommon0; pełne stożki optyczne nadal nieodebrane. Źródło podaje Camera3 102×67°/120° diagonalnie; okno pudełkowe tego nie dowodzi.

## Rzeczywista konstrukcja przed maską

`head-root-actual-context.png` pokazuje jawnie przerwy, a `head-root-and-assembly-map.json` zawiera datums. Cylindry BRep potwierdzają yaw608: ośZ przez(-126,0), pierścienie120..127 i134..141, OD22/ID8. Pitch688: ośY przez(-155,14,141), Y14..19, OD16/ID8. Nie wyprowadzono tych osi z nazwy pudełka. W obecnym projekcie Neck_shared_root ma **2mm do P10 i32,48mm do dolnego608**; to nie jest gotowy loadpath.

Jedna następna zasada: wspólny otwarty most oparty o rzeczywiste ledges P10 (dolnyX[-113,-98]/Y±16/Z63..65,5 oraz górnyX[-104,-98]/Y±15/Z132,5..138) -> dwa stałe gniazda608 -> ruchomy yawtrunnion/pitchcarrier ->688 -> wspólna sensorplate. Maska nie niesie serw/czujników. Do związania pozostają rzeczywisty orczyk/spline/taby MG92B, utrzymanie trunniona w8mm otworach, cały zestaw śrub mostu i otwory sensorplate. Niczego nie sklejono pozornie z kupnym serwem/łożyskiem i nie wydano rootSTL.

Dwie osoby: A podtrzymuje otwartą bramę i most; B weryfikuje bearing/horn-coupon i pełne mocowanie przed elektroniką. Potem yaw/pitch i wspólna sensorplate, rzeczywiste fabryczne końce CSI/czujników układane otwarcie, na końcu maska. E1 pozostaje lutowane. CSI ma tylko diagram miejsca z jawnym UNKNOWN złącza/wybranej pełnej taśmy/długości/R i rzeczywistych granic obu osi; nie przyznano zapasu ani motionPASS. Fizyczny FIT3 wiąże orczyk, łożysko, plate i optykę; nie katalogowy audyt całego robota.

## Krótka porcja tylnego mocowania — zakończona bez drugiej rodziny

Stare pełne M3x25 w S0: common60,309861mm³ zachowane. Nowy odczyt P11 wROI X80..115/Y-50..-20/Z50..85 daje **validcommon0 materiału**. W tej strefie nie istnieje deklarowane oparcie; BBox P11 i nazwa receivingpad nie były dowodem. Carrier pozostaje OPEN, bez nowego przesunięcia łba/nakrętki i bez nowego STL. Następna korekta musi doprowadzić rzeczywisty loadroute do istniejącej nogi P11. Całe battery/MTA/fourfeet/stock/straps/Pi pozostały w modelu.

Brak nowych STL kosmetyki/korzenia/carriera. Wszystkie starsze HOLD pozostają, Pi4 i prowadzenia tylko w odebranym niezmienionym zakresie. Actualfit/cut/slack=NULL; brak fizycznego druku, zasilania, strengthPASS, gotowej skorupy lub całego kota. Obwiednie są pełnymi bryłami do oceny wyglądu, **nie masą ani drukiem**. 57+extras,4DATA/5plus/7G,4niezależne220/MTA,USB/krótkieFHAC i ochrona zachowane. Następny ruch: związać rzeczywisty horn/8mm trunnion i most na P10; kosmetyczne detale po tej decyzji. S0key/motion/FOV i pozostałe praktyczne FIT nadal jawnie otwarte.
