# robot cat — notes for Codex

## Nowe 2 godziny16Nov — lżejszy i niższy CAŁY robot; rzetelny wygląd

Jawna nowa zgoda użytkownika: „Zostańmy na razie z tymi co miałem”, „Ok dawaj. Ale stan wizualny oceniaj rzetelnie”, „Do zobaczenia za2h”. Okno2026-11-16T18:21:26Z–20:21:26Z (19:21–21:21Warszawa); zastępuje pauzę i wcześniejsze22:10/NEXT. Celem jest JEDEN lżejszy, niższy wykonalny CAŁY wariant z prawdziwymi widokami i porównaniem masy/obciążeń. Nie obiecano pełnego zestawuSTL ani fizycznegoPASS.
Zachować12ST3215,3MG, obecną długość nóg, wszystkie wybrane moduły/ochronę/fabryczne końce i funkcje, ogonGÓRA–DÓŁ oraz2osie głowy. MocniejszeSM80BL były tylko rozmową: NIE wybrane/nie kupować. Niewielka zmiana szerokości/długości ramy i rozstawu CAŁYCH bioder dopuszczona, gdy upraszcza całość. Dawne własneP10/P11/P12/pozybanków i druki są zmienne; nie utrwalać wysokiej pudełkowatej zabudowy lokalnymi wspornikami.
Najpierw cały niski układ części, nośności, przestrzeni wspólnych wiązek, portów/chłodzenia i otwartego montażu, potem niezbędne modelowanie. Bez123osi/FEM/serwisu produkcyjnego/globalnychstarychscanów/katalogowegoaudytu. Zwykłe dokończenie własnegojointu w tej samej architekturze nie jest osobną rodziną/HOLD.
Zeno ocenia rzeczywiste opaque przód/bok/3q oraz wnętrze względem ROBOTA Oli: proporcje tułów–głowa–nogi, oczy/pysk, grzbiet i nasadaogona; brakujące osłony i wystające części widoczne. Ma napisać wprost jeśli nadal pudełkowaty/niepodobny/bez poprawy, bez procentu/pobłażliwegoGO. Master również ogląda obrazy. Same uszy/oczy nie dowodzą kociej całości. Nie zastępować CAD obrazkiemimagegen.
Pomiar92a798fc:70aktualnychdruków1400,4cm3/1,779kgPETGpełnego materiału; druki+nogi1,35..1,90kg heurystycznie; całyrobot3,1..4,6kg szerokiszacunek, roboczo4kg; ramię75,12mm. Nowy wynik porównuje TE SAME gęstości/wypełnienia/zakresy części; nie usuwać masy przez ukrycie/zmianęzałożenia. 2,5kg jest kierunkiem do sprawdzenia, NIE nowym niezmiennym limitem. Momentznamionowy10/stall30kgfcm przy12V nie jest odbiorem chodzenia.
JedynyCADBanach; masterjedynyFIRST/runtime/currentassembly; Bohr prywatnyworktree/osobnyGitindex. Recenzenci readonly fixedsource, bez narzędziCAD/edycji. Nie stageowaćMECH podczasaktywnegoBanacha; własne wąskiecommity, bezforeignstagedchanges/blanketclean/reset/add.
Checkpoint18:51:26UTC. Nowe długie native do20:01:26; zapis/koniecownedcompute20:11:26; HARDSTOP20:21:26 bezprzedłużenia. Limit ordinary świeży target4/max10 i przedkosztownym; %guardNULL/resetzakazany. ZachowaćjednąGUI, normalreturn bezSystemExit. Bez zakupów/zasilania/druku/slicera/ROS/push/mail/alertów/nowychagentów. Physicalfit/cut/slack nieudawane. Przy stopzapis/koniecownedcompute/enabledfalse.

## Ogon — potwierdzone wymaganie użytkownika 16.11.2026

Ogon ma poruszać się GÓRA–DÓŁ: obrót wokół osi poprzecznej korpusu (pitch; Y przy X wzdłuż korpusu i Z w pionie). Nie zastępować tego merdaniem na boki wokół Z. Model symulacyjny tail_joint już ma axis="0 1 0"; nie zmieniać go na błędną oś CAD.
Zapisany CAD5e504/99007 ma niewłaściwy kierunek tail_Z. Dawne dowody ruchu/prześwitu ogona dla Z nie kwalifikują ruchu pionowego. Przy następnym wznowieniu poprawić cały interfejs serwo–róg–łożysko–korzeń/przejście osłony i tylko dotknięte sprawdzenia; sama zmiana metadanych osi nie naprawia mechanizmu. Zakres kąta pozostaje do dobrania, bez automatycznego przenoszenia dawnych±20Z. Zachować wybrane części/liczbę napędów i niezależne dowody podstawy.
Potwierdzenie wymagania nie wznawia zamkniętego okna ani nie oznacza poprawionej geometrii.

## Prototype harness fidelity (26.10.2026)

Read the current26.10 section at the top of `hardware/cad/DESIGN_LESSONS.md`
and the `cad-layout-planning` skill. Plan stable module mounts and connected,
accessible bundle regions with local occupancy, lengths/slack, anchors and
assembly. Complete123/246 connection coverage does not require individual
solid sweeps. Before an exact wire model/test, name the local physical hazard,
the design decision, and why a bundle-space model cannot answer it. Keep that
test local. Illustrative flexible free spans are not rigid obstacles; one
immutable wire shape cannot represent every flexed leg pose. Preserve real
module/connector/motion constraints, selected parts and factory lengths.
For prototype acceptance, prove feasible installation and required routine
access. Occasional repair may use documented partial disassembly. Do not add
rapid-service requirements, individual rigid holders for every conductor, or
a production harness drawing. Final hand-laid wire arrangement is an assembly
check; connected bundle capacity, fixed lengths and joint slack remain planned.
This changes model fidelity, not the completion score or physical acceptance.

## Current decision entry point (25.10.2026)

For current mechanical layout work, read ONLY the first Karta decyzji CAD
section in `hardware/HOBBY_COMPLETION_PLAN.md` through the next level-two
heading first. Older cards and NEXT blocks are history, even when they say ON.
Use the named current packet for geometry; do not reload the whole diary.
Local corridor occupancy comes from wires traversing that segment, not all
logical groups assigned to a side. Receive the whole prerequisite gate before
generating dependent geometry. After two same-cause failures record a concrete
change of module/support/topology/assembly order; a new filename is insufficient.
One writer and the existing read-only reviewer; no competing CAD agents.
Fixed N01-N10 score; accepted local evidence is reused without partial points.

Quadruped robot cat: ROS 2 Jazzy + Gazebo Harmonic, running **natively on
macOS / Apple Silicon** through RoboStack (conda packages, driven by `pixi`).

**Read the Runbook section of [README.md](README.md) before running anything.**
It covers bootstrap, startup, how to drive the cat without a keyboard, and how
to verify it actually walked. What follows is only the part most likely to
waste your time.

For CAD, PETG mechanics or actuator sizing, read `hardware/skorupa/STATUS.md`
and `hardware/simulation/README.md` first. The current FreeCAD-derived model
is separate from the historical primitive ROS model; do not reuse its
2.095 kg budget or stall-torque comparison as approval of current hardware.
Keep existing checkpoints and use the user's `syskaseb` remote for mechanical
work; `origin` points to a different owner's repository.

For CAD architecture/refactoring, also read `hardware/MODULAR_DESIGN.md`.
It describes staged migration: the AUX pilot is implemented, not the whole
assembly. Preserve the v35 baseline and inspect pilot evidence before extending it.

Project skills live in `.agents/skills/`: `robot-cat-module` for CAD changes,
`robot-cat-petg` for print design, `robot-cat-assembly-audit` for joints/mounts,
`robot-cat-electronics` for electrical integration, and `robot-cat-release` for
hardware checkpoints. Read the relevant SKILL.md before applying its workflow.
Use `hardware/cad/README.md` for the actual migration scope and validation paths.
Follow `hardware/cad/SESSION_HYGIENE.md`: keep only the active assembly and its
dependencies open; run expensive experiments in disposable worker processes.

## Environment

**Check which platform you are on before running anything.** On macOS the
project runs through pixi, as below. On Windows or Linux `pixi install` refuses
outright — `pixi.toml` pins `osx-arm64` — and the way in is
`run/docker/`, which has its own README. The two paths share every source file,
so a change made in one has to keep working in the other; nothing
platform-specific belongs in `src/`.

There is no system ROS. Every command must go through pixi:

```bash
pixi run bash -c 'source install/setup.bash && <ros2 command>'
```

Plain `ros2 ...` will not be found, and `source install/setup.bash` alone is not
enough — the overlay sits on top of the pixi environment, not instead of it.

## Rules that are easy to get wrong

- **Never `set -u` before `source install/setup.bash`.** colcon's script reads
  unset variables and aborts the whole shell. This looks like the launch failing
  for no reason.
- **Shut down with all three:**
  `pkill -f "gz sim"; pkill -f gait_controller; pkill -f "ros2 launch"`.
  Killing only the launcher orphans its child nodes. Two surviving
  `gait_controller` processes publish to the same command topic at 100 Hz with
  independent gait phases, and the cat skates across the world looking exactly
  like a physics bug. Check `pgrep -fl gait_controller` before diagnosing any
  strange motion.
- **Startup takes ~10 s.** Poll until all four controllers report `active`
  rather than sleeping a fixed amount — see Runbook step 4.
- **A lame-looking cat is dropped `/cmd_vel`, not a broken gait.** Stuttering,
  tens of degrees of veer, or barely moving *while the head and tail still
  respond* means the 0.5 s gait watchdog is firing mid-stride. Check
  `grep "holding stance"` in the sim log. This is why the repo pins
  `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`; Fast DDS's shared memory is broken
  on this machine and drops traffic silently. See
  `config/cyclonedds_localhost.xml`.
- **A backgrounded `ros2 topic pub` outlives `kill -INT $!`.** The pid you
  captured is the `pixi run` wrapper; the publisher itself is a grandchild
  python process and keeps driving `/cmd_vel` at 20 Hz, so the cat walks off
  by itself and later measurements are garbage. Always confirm with
  `pgrep -fl "ros2 topic pub"` and clear with `pkill -9 -f "ros2 topic pub"`.
- **`teleop.sh` publishes `/cmd_vel` at 20 Hz even when idle** (zeros). Do not
  run it while driving `/cmd_vel` from the CLI — the two publishers interleave
  and the cat barely moves.
- **You cannot use the keyboard teleop.** It reads an interactive terminal.
  Publish to `/cmd_vel` instead; it is the same interface the teleop node uses.
- **Verify motion by reading the pose**, not the viewport:
  `gz model -m robot_cat -p`. Standing height is `z ≈ 0.172`. Parse it with
  `tr -d '[]'` — including a space in that set concatenates the coordinates.
- **Yaw wraps at ±π.** A "backwards" turn reading after a long spin is almost
  always a wrap. Measure turn rates in bursts of ~4 s.

## Layout

| package | contents |
|---|---|
| `robot_cat_description` | xacro model, `ros2_control` wiring, controller config |
| `robot_cat_gait` | leg IK, trot generation, the play-bow stretch and the lie-down loaf (all ROS-free, unit tested) + the node, which also owns `/stretch` and `/lie_down` |
| `robot_cat_teleop` | arrow-key body teleop, W/A/S/D head, space-stepped tail, `v` camera views, `m` meow, `x`/`p` requests to the gait node; decoding, head easing, tail sweep and the first-person pose maths are pure functions in `keys.py`, `head.py`, `tail.py`, `camera_view.py` |
| `robot_cat_bringup` | world, launch files, RViz config |

## Changing things

The gait maths is pure and fully unit tested — `pixi run pytest` is 581 tests in
under a second, with no simulator. Run it before launching Gazebo; if it fails,
the simulator will only obscure the cause.

Gait defaults were chosen by measurement, not taste, and the reasoning is
recorded in `gait.py` docstrings. Before "improving" `duty_factor` or
`cycle_time`, read those — a textbook 0.5 trot drifts 12x more in heading.

Link lengths are duplicated by design: `cat.urdf.xacro` and `LegGeometry` in
`leg_ik.py` are not derived from one another. Change one, change the other —
and `gait_controller.py` declares them a third time as ROS parameter defaults,
so that is three files, not two.

The leg is sized for **proportion**, not just reach. Segments are `0.11` and
the cat stands at `0.16`, which puts the withers at 21.7 cm over a 22 cm hip
span — near enough square, which is what reads as feline. The earlier `0.09`
segments at `0.13` gave a ratio of 0.85 and looked like a dachshund. Those two
numbers move **together**: what the gait actually depends on is the knee
staying near 73% of full reach, and raising `stance_height` on its own
straightens it toward a locked leg with no swing clearance.

`stance_width` is not cosmetic. Setting it to 0 puts each paw in the plane of
its own hip, which makes `leg_ik` solve that roll joint to exactly zero for
every pose — four of the twelve motors stop moving entirely and the cat
wallows about 8–11° in roll on the diagonal it is standing on. Every lateral
offset in `GaitGenerator` goes through `_neutral_y()` so that walking,
standing, stretching and lying down widen together and
`stretch_pose(0) == stand()` stays true; if you add another pose, use it
rather than `hip_offset` directly.

All four legs bend the **same** way. An earlier revision mirrored the rear
knees to be anatomically catlike; that was deliberately reverted to match how
real quadruped robots (Spot, Unitree) are actually built, with four identical
legs. `knee_sign` still selects the IK branch, but it is now one value for the
whole robot.

## Known limitation

Gazebo **sensors do not work on macOS** — cameras, lidar and depth sensors crash
because Cocoa requires render-window creation on the main thread
(gazebosim/gz-sim#960). Nothing here needs them. Adding perception means moving
the runtime to Docker or Linux; the ROS packages port over unchanged.
