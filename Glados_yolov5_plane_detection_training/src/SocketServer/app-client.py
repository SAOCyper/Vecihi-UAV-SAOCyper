
import sys
import socket
import selectors
import traceback

import libclient

sel = selectors.DefaultSelector()

telemetry_data=[{
                            "takim_numarasi": 1,
                            "IHA_enlem": 43.576546,
                            "IHA_boylam": 22.385421,
                            "IHA_irtifa": 100,
                            "IHA_dikilme": 5,
                            "IHA_yonelme": 256,
                            "IHA_yatis": 0,
                            "IHA_hiz": 223,
                            "IHA_batarya": 20,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 315,
                            "Hedef_merkez_Y": 220,
                            "Hedef_genislik": 12,
                            "Hedef_yukseklik": 46,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 1,
                            "saniye": 23,
                            "milisaniye": 507
                            }
                            },
                            {
                            "takim_numarasi": 1,
                            "IHA_enlem": 43.654352,
                            "IHA_boylam": 22.31245421,
                            "IHA_irtifa": 105,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            }]
lock_on_data = [{"kilitlenmeBaslangicZamani": {
                                "saat": 19,
                                "dakika": 1,
                                "saniye": 23,
                                "milisaniye": 507
                                },
                                "kilitlenmeBitisZamani": {
                                "saat": 19,
                                "dakika": 1,
                                "saniye": 45,
                                "milisaniye": 236
                                },
                                "otonom_kilitlenme": 0},
                                {"kilitlenmeBaslangicZamani": {
                                "saat": 19,
                                "dakika": 2,
                                "saniye": 35,
                                "milisaniye": 234
                                },
                                "kilitlenmeBitisZamani": {
                                "saat": 19,
                                "dakika": 3,
                                "saniye": 10,
                                "milisaniye": 236
                                },
                                "otonom_kilitlenme": 1}]
login = {
    "kadi" : "Hüma Vecihi",
    "sifre": "Vecihi123"
}
kamikaze_list = {
    "kamikazeBaslangicZamani": {
    "saat": 19,
    "dakika": 1,
    "saniye": 23,
    "milisaniye": 507
    },
    "kamikazeBitisZamani": {
    "saat": 19,
    "dakika": 1,
    "saniye": 28,
    "milisaniye": 236
    },
    "qrMetni ": "teknofest2022",
}

def create_post_value(value):
    request_post = {
    "/api/telemetri_gonder":telemetry_data,
    "/api/kilitlenme_bilgisi":lock_on_data,
    "/api/giris":login,
    "/api/kamikaze_bilgisi":kamikaze_list,
    }
    sent = request_post[value]
    return  sent
def create_request(action, value):
    if action == 'post':
        sent = create_post_value(value=value)
    else:
        sent = "Nothing sent"
    if action == "get" or action == "post":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value ,sent = sent ),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value + sent, encoding="utf-8"),
        )


def start_connection(host, port,action, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    
    events =  selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if len(sys.argv) != 5:
    print(f"Usage: {sys.argv[0]} <host> <port> <action> <value>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
action, value = sys.argv[3], sys.argv[4]
request = create_request(action, value)
start_connection(host, port,action,request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    f"Main: Error: Exception for {message.addr}:\n"
                    f"{traceback.format_exc()}"
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()