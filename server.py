# ...existing code...
import socket
import random
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
DROP_PROB = 0.3  # 30% di probabilità di scartare il messaggio
MAX_DELAY = 5.0  # delay massimo in secondi prima di inviare ACK

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

processed = {}  # seq -> timestamp
CLEANUP_AGE = 300.0  # mantieni gli ultimi 5 minuti
LAST_CLEANUP = time.time()

print(f"Server UDP in ascolto su {UDP_IP}:{UDP_PORT} (drop={int(DROP_PROB*100)}%, max_delay={MAX_DELAY}s)")

while True:
    data, addr = sock.recvfrom(4096)
    now = time.time()
    # pulizia periodica
    if now - LAST_CLEANUP > CLEANUP_AGE:
        cutoff = now - CLEANUP_AGE
        processed = {s: t for s, t in processed.items() if t >= cutoff}
        LAST_CLEANUP = now

    try:
        text = data.decode(errors="replace")
        seq_str, payload = text.split(":", 1)
        seq = int(seq_str)
    except Exception:
        # formato non valido: ignora
        print(f"Formato messaggio non valido da {addr}: {data!r}")
        continue

    # simulazione drop
    if random.random() < DROP_PROB:
        print(f"DROPPED da {addr}: seq={seq} payload={payload!r}")
        continue

    delay = random.uniform(0, MAX_DELAY)
    print(f"Ricevuto da {addr}: seq={seq} payload={payload!r} -> attendo {delay:.2f}s prima di inviare ACK")
    time.sleep(delay)

    if seq in processed:
        # duplicate: non rielaborare, ma invia comunque ACK
        print(f"Duplicate ricevuto (seq={seq}) — invio solo ACK")
    else:
        # prima volta: processa e registra
        processed[seq] = now
        print(f"Elaborato messaggio seq={seq}: {payload!r}")

    response = f"ACK:{seq}"
    sock.sendto(response.encode(), addr)
    print(f"ACK inviato a {addr} per seq={seq}")
# ...existing code...