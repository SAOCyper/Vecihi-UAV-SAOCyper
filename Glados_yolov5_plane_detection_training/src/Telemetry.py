from pydantic import BaseModel
from fastapi import FastAPI
import datetime,time
from typing import Optional

app = FastAPI()

class Telemetri():
    class GPSSaatiSubClass():
        saat: int
        dakika: int
        saniye: int
        milisaniye: int
    takim_numarasi: int
    IHA_enlem: float
    IHA_boyla: float
    IHA_irtifa: float
    IHA_dikilme: int
    IHA_yonelme: int
    IHA_yatis: int
    IHA_hiz: int
    IHA_batarya: int
    IHA_otonom: bool
    IHA_kilitlenme: bool
    Hedef_merkez_X: int
    Hedef_merkez_Y: int
    Hedef_genislik: int
    Hedef_yukseklik: int
    GPSSaati: Optional[GPSSaatiSubClass] = None

class Kilitlenme():
    class BaslangicSubClass():
        saat: int
        dakika: int
        saniye: int
        milisaniye: int

    class BitisSubClass():
        saat: int
        dakika: int
        saniye: int
        milisaniye: int

    kilitlenmeBaslangicZamani: Optional[BaslangicSubClass] = None
    kilitlenmeBitisZamani: Optional[BitisSubClass] = None
    otonom_kilitlenme: bool

def saatAl():
    time_format = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    splitted = time_format.split(":")
    splitted1 = splitted[2].split('.')
    return {"saat":splitted[0],"dakika":splitted[1],"saniye":splitted1[0],"milisaniye":splitted1[1]}

#@app.get("/api/sunucusaati")
def sunucusaati():
    return saatAl()

#@app.post("/api/telemetri_gonder")
def telemetri_gonder(item: Telemetri):
    print({"sistemSaati":saatAl(),
            "konumBilgileri":[
                {
                    "takim_numarasi":1,
                    "iha_enlem":500,
                    "iha_boylam":500,
                    "iha_irtifa":500,
                    "iha_dikilme":5,
                    "iha_yonelme":256,
                    "iha_yatis":0,
                    "zaman_farki":93 #dinamik hale getir
                    },
                ]})
    return {"sistemSaati":saatAl(),
            "konumBilgileri":[
                {
                    "takim_numarasi":1,
                    "iha_enlem":500,
                    "iha_boylam":500,
                    "iha_irtifa":500,
                    "iha_dikilme":5,
                    "iha_yonelme":256,
                    "iha_yatis":0,
                    "zaman_farki":93 #dinamik hale getir
                    },
                ]}

#@app.post("/api/kilitlenme_bilgisi")
def kilitlenme_bilgisi(item: Kilitlenme):
    saat = saatAl()
    Kilitlenme.BaslangicSubClass.saat = saat["saat"]
    Kilitlenme.BaslangicSubClass.dakika = saat["dakika"]
    Kilitlenme.BaslangicSubClass.saniye = saat["saniye"]
    Kilitlenme.BaslangicSubClass.milisaniye = saat["milisaniye"]
    time.sleep(1)
    saat = saatAl()
    Kilitlenme.BitisSubClass.saat = saat["saat"]
    Kilitlenme.BitisSubClass.dakika = saat["dakika"]
    Kilitlenme.BitisSubClass.saniye = saat["saniye"]
    Kilitlenme.BitisSubClass.milisaniye = saat["milisaniye"]
    Kilitlenme.otonom_kilitlenme = 1 


kilitlenme_bilgisi(Kilitlenme)