# Skrypty do skorupy kota (v17)

Model `hardware/skorupa/Kot_v17_WNETRZE.FCStd` powstał przez edycję archiwum
`.FCStd` poza FreeCADem, z użyciem `cadquery-ocp` (te same wiązania OpenCascade,
co w FreeCADzie). Powód: FreeCAD potrafi wisieć minutami na booleanach w pętli,
a przez tunel MCP kończy się to timeoutem.

    pip install cadquery-ocp matplotlib numpy --break-system-packages

Kolejność:

1. rozpakuj `.FCStd` do `src/`
2. `build17.py` - przebudowuje obwiednie i robi wycięcia (kratka głośnika,
   otwory złączy, kieszenie serw, wydrążenia), nadpisuje pliki `*.brp` w `src/`
3. `patchxml.py` - zeruje `Placement` ruszanych obiektów w `Document.xml`
   i poprawia etykiety
4. spakuj z powrotem **zachowując oryginalną kolejność wpisów w archiwum**
   (inaczej FreeCAD wczyta dokument z pustymi kształtami)
5. `render17.py` - podgląd bez FreeCADa (tesselacja + matplotlib), także
   przekrój "ghost" ze skorupą przezroczystą

`fc.py` to warstwa wspólna: wczytywanie `.brp`, tesselacja, obwiednie
i klasyfikator punkt-w-kawernie (rzucanie promieni po siatce trójkątów,
bez booleanów - jest o rzędy wielkości szybszy przy skanowaniu wolnej przestrzeni).

Pułapki układu współrzędnych opisane są w `hardware/skorupa/README.md`.
