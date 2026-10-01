"""One bundle restraint below AUX crossing, five board-end restraints."""
import pi_gpio_integrated_checks_r1 as G
G.OUT=G.ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r5'
G.ROUTES=G.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r9'
G.AXES=[(10,45),(22,53),(26,57),(14,51),(18,53)]
G.ENDS=[(91.54,28,151.5),(104.24,2,151.5),(91.54,-16,149),(-57.095,-7,149),(-57.095,18,151.5)]
G.GROUP_UPSTREAM=True;G.GROUP_TIE_Z=129;G.GROUP_MAX_Y=58.5
if __name__=='__main__':G.main()
