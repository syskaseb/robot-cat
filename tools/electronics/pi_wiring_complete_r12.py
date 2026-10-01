"""OE north fan widened6mm to clear full T18I band, not just copper."""
import pi_wiring_complete_r11 as P
M=P.M
M.OUT=M.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r12'
M.OE_FAN_OFFSET=6
if __name__=='__main__':M.main()
