import time
t66=time.monotonic();c66=time.process_time()
tail66=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat44-S0-full-bench-approach-and-terminal-access.py').read_text(encoding='utf-8')
tail66=tail66[tail66.index('inverse65='):]
tail66=tail66.replace('inverse65=A.Matrix(place57);inverse65.invert()','inverse65=place57.inverse().toMatrix()')
tail66=tail66.replace('time.monotonic()-t65>22','time.monotonic()-t66>15')
tail66=tail66.replace('operation_seconds=time.monotonic()-t65,process_cpu_seconds=time.process_time()-c65','operation_seconds=None,interrupted_total_elapsed_wall_seconds=time.monotonic()-t65,resumed_terminal_operation_seconds=time.monotonic()-t66,resumed_terminal_process_cpu_seconds=time.process_time()-c66,process_cpu_seconds=time.process_time()-c65,error_recovery_receipt=err65.name,error_recovery_sha256=hashlib.sha256(err65.read_bytes()).hexdigest(),case_phase_not_replayed=True')
exec(compile(tail66,'S0-terminal-resume-same-data-after-type-error','exec'))
