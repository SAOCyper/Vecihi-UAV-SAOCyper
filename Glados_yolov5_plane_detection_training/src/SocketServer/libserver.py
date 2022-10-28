import sys
import selectors
import json
import io
import struct
from datetime import *



class AppServerStorage:
    def _StoreData(telemetri_veri=[{},{}],kilitlenme_veri=[{},{}],giriş_veri=[{},{}],kamikaze_veri=[{},{}]):
            request_post = {
                "/telemetri_gonder":{"takım1":telemetri_veri[0],"takım2":telemetri_veri[1]},
                "/kilitlenme_bilgisi":{"takım1":kilitlenme_veri[0],"takım2":kilitlenme_veri[1]},
                "/giris":{"takım1":giriş_veri[0],"takım2":giriş_veri[1]},
                "/kamikaze_bilgisi":{"takım1":kamikaze_veri[0],"takım2":kamikaze_veri[1]}
            }
            print(request_post.get("/telemetri_gonder"))
            return request_post 
class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print(f"Sending {self._send_buffer!r} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        action = self.request.get("action")
        request_get = {
            "morpheus": "Follow the white rabbit. \U0001f430",
            "ring": "In the caves beneath the Misty Mountains. \U0001f48d",
            "\U0001f436": "\U0001f43e Playing ball! \U0001f3d0",
            "/sunucusaati":"Saat:{} ,Dakika:{} ,Saniye:{} ,MiliSaniye:{}".format(datetime.now().strftime('%H:'),datetime.now().strftime('%M:'),datetime.now().strftime('%S'),datetime.now().strftime('%f')),
            "/qr_koordinati" : "qrEnlem:42.6543 , qrBoylam:52.1424",
        }
        if action == "get":
            query = self.request.get("value")
            answer = request_get.get(query) or f"No match for '{query}'."
            content = {"result": answer}
        elif action == "post":
            query = self.request.get("value")
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
            answer=AppServerStorage._StoreData(telemetri_veri=telemetry_data,kilitlenme_veri=lock_on_data)
            content = {"result": answer}
        else:
            content = {"result": f"Error: invalid action '{action}'."}
        content_encoding = "utf-8"
        response = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": "text/json",
                "content_encoding": content_encoding,
        }
        return response    

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        AppServerStorage()
        self._write()

    def close(self):
        print(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )

        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f"Missing required header '{reqhdr}'.")

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print(f"Received request {self.request!r} from {self.addr}")
        else:
            # Binary or unkdatetime.now()n content-type
            self.request = data
            print(
                f"Received {self.jsonheader['content-type']} "
                f"request from {self.addr}"
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unkdatetime.now()n content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message