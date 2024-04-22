Prueba de uso Gunicorn y Nginx en subsistema Ubuntu:

josephjosue@DESKTOP-RPP4S87:/mnt/c/Users/Joseph/Documents/UIP/Programacion de Computadoras 4/Flask$ gunicorn -w 4 -b 127.0.0.1:5001 main:my_app
[2024-04-22 14:37:10 -0500] [4507] [INFO] Starting gunicorn 20.1.0
[2024-04-22 14:37:10 -0500] [4507] [INFO] Listening at: http://127.0.0.1:5001 (4507)
[2024-04-22 14:37:10 -0500] [4507] [INFO] Using worker: sync
[2024-04-22 14:37:10 -0500] [4509] [INFO] Booting worker with pid: 4509
[2024-04-22 14:37:10 -0500] [4510] [INFO] Booting worker with pid: 4510
[2024-04-22 14:37:10 -0500] [4511] [INFO] Booting worker with pid: 4511
[2024-04-22 14:37:10 -0500] [4513] [INFO] Booting worker with pid: 4513
[2024-04-22 14:39:17 -0500] [4507] [CRITICAL] WORKER TIMEOUT (pid:4513)
[2024-04-22 14:39:17 -0500] [4513] [INFO] Worker exiting (pid: 4513)
[2024-04-22 14:39:17 -0500] [4999] [INFO] Booting worker with pid: 4999