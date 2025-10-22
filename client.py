# ...existing code...
import socket
import time

UDP_IP = "127.0.0.1"  # IP del server
UDP_PORT = 5005

NUM_MESSAGES = 10
MAX_RETRIES = 5
SEND_INTERVAL = 0.1  # secondi tra messaggi
RETRANSMIT_INTERVAL = 2.5  # client ritrasmette ogni 2.5 secondi

# Creazione socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(RETRANSMIT_INTERVAL)  # attendi fino a 2.5s per ogni tentativo

acked = set()

for i in range(1, NUM_MESSAGES + 1):
    seq = i
    payload = f"Ciao server! #{i}"
    packet = f"{seq}:{payload}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # invia (retrasmissioni consentite fino ad ACK)
            sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
            data, server = sock.recvfrom(4096)
            resp = data.decode(errors="replace")

            if not resp.startswith("ACK:"):
                print(f"Risposta non-ACK (messaggio {i}, tentativo {attempt}): {resp}")
                continue

            # parse ACK
            try:
                ack_seq = int(resp.split(":", 1)[1])
            except Exception:
                print(f"ACK malformato ricevuto: {resp!r}")
                continue

            if ack_seq != seq:
                # ACK per un altro messaggio (probabile ritardo): ignora
                print(f"ACK per sequenza diversa ({ack_seq}) ignorato (atteso {seq})")
                continue

            # ACK per il messaggio corrente
            if seq in acked:
                print(f"ACK duplicato per seq={seq} ignorato")
            else:
                acked.add(seq)
                print(f"Invio messaggio {i}/{NUM_MESSAGES}: {payload} -> ACK ricevuto")
            break

        except socket.timeout:
            print(f"Timeout (messaggio {i}, tentativo {attempt}/{MAX_RETRIES}) — ritento tra {RETRANSMIT_INTERVAL}s...")

    else:
        print(f"Nessuna ACK per il messaggio {i} dopo {MAX_RETRIES} tentativi.")
    time.sleep(SEND_INTERVAL)
# ...existing code...