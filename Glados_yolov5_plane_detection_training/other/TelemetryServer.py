import socket,time,threading
import json
import pickle
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def get_data(i):
        telemetry_data=[{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.854831,
                                    "IHA_boylam": 32.781294,
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
                                    "takim_numarasi": 2,
                                    "IHA_enlem": 39.855294,
                                    "IHA_boylam": 32.782847,
                                    "IHA_irtifa": 90,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.855888,
                                    "IHA_boylam": 32.781808,
                                    "IHA_irtifa": 185,
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
                                    }
                                    ,{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.853896,
                                    "IHA_boylam": 32.780913,
                                    "IHA_irtifa": 115,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.855172,
                                    "IHA_boylam": 32.778907,
                                    "IHA_irtifa": 120,
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
        a = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.855002,
                                    "IHA_boylam": 32.781967,
                                    "IHA_irtifa": 102,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem": 39.855628,
                                    "IHA_boylam": 32.782197,
                                    "IHA_irtifa": 96,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.855565,
                                    "IHA_boylam": 32.782162,
                                    "IHA_irtifa": 187,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.854489,
                                    "IHA_boylam": 32.781257,
                                    "IHA_irtifa": 113,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.855082,
                                    "IHA_boylam": 32.780001,
                                    "IHA_irtifa": 111,
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
        b = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.854831,
                                    "IHA_boylam":  32.782506,
                                    "IHA_irtifa": 104,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem":  39.855519, 
                                    "IHA_boylam": 32.781460,
                                    "IHA_irtifa": 106,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.855160,
                                    "IHA_boylam": 32.782190,
                                    "IHA_irtifa": 189,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.855057,
                                    "IHA_boylam": 32.780699,
                                    "IHA_irtifa": 109,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.855032,
                                    "IHA_boylam": 32.781321,
                                    "IHA_irtifa": 107,
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
        c = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.854454, 
                                    "IHA_boylam": 32.782664,
                                    "IHA_irtifa": 107,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem":  39.855263, 
                                    "IHA_boylam": 32.780787,
                                    "IHA_irtifa": 87,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.855207, 
                                    "IHA_boylam": 32.780150,
                                    "IHA_irtifa": 182,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.855065, 
                                    "IHA_boylam": 32.779679,
                                    "IHA_irtifa": 107,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.854752,
                                    "IHA_boylam": 32.781847,
                                    "IHA_irtifa": 104,
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
        d = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.854094, 
                                    "IHA_boylam": 32.782445,
                                    "IHA_irtifa": 110,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem":  39.855725, 
                                    "IHA_boylam": 32.781399,
                                    "IHA_irtifa": 83,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.854686,
                                    "IHA_boylam": 32.781922,
                                    "IHA_irtifa": 192,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.854736, 
                                    "IHA_boylam": 32.778542,
                                    "IHA_irtifa": 104,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.854291,
                                    "IHA_boylam": 32.781975,
                                    "IHA_irtifa": 108,
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

        e = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.853838, 
                                    "IHA_boylam": 32.781898,
                                    "IHA_irtifa": 115,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem":  39.855544, 
                                    "IHA_boylam": 32.782193,
                                    "IHA_irtifa": 80,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.854250,
                                    "IHA_boylam": 32.782126,
                                    "IHA_irtifa": 196,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.855214, 
                                    "IHA_boylam": 32.777984,
                                    "IHA_irtifa": 108,
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
                                    },{
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.854125,
                                    "IHA_boylam": 32.781941,
                                    "IHA_irtifa": 112,
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
        f = [{
                                    "takim_numarasi": 1,
                                    "IHA_enlem": 39.853719, 
                                    "IHA_boylam": 32.780939,
                                    "IHA_irtifa": 115,
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
                                    },{
                                    "takim_numarasi": 2,
                                    "IHA_enlem":  39.855237,  
                                    "IHA_boylam": 32.782620,
                                    "IHA_irtifa": 80,
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
                                    },
                                    {
                                    "takim_numarasi": 3,
                                    "IHA_enlem": 39.853662, 
                                    "IHA_boylam": 32.782033,
                                    "IHA_irtifa": 196,
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
                                    },{
                                    "takim_numarasi": 4,
                                    "IHA_enlem": 39.855880,
                                    "IHA_boylam": 32.777920,
                                    "IHA_irtifa": 108,
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
                                    },{ 
                                    "takim_numarasi": 5,
                                    "IHA_enlem": 39.853729,
                                    "IHA_boylam": 32.781366,
                                    "IHA_irtifa": 112,
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
        telemetry_list = [telemetry_data,a,b,c,d,e,f]
        data_string = pickle.dumps([0,0])
        if i < 6:
            data_string = pickle.dumps([telemetry_list[i],telemetry_list[i+1]])
        return data_string

condition = True    
i = 0

def serve_client(addr,client_socket):
    global condition
    global i
    if client_socket:
        print(f"Connected by {addr}")
        while condition:
            #data = client_socket.recv(1024)
            #print(data.decode)
            """ if not data:
                print("Break happened")
                break """
            telemetry_list= get_data(i)
            i = i + 1
            """ if i > 6:
                condition = False
                i= 0
                break """
            time.sleep(0.98)
            
            client_socket.sendall(telemetry_list)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on {(HOST, PORT)}")
    #s.setblocking(True)
    #s.setblocking(False)
    client_socket, addr = s.accept()
    serve_client(addr=addr,client_socket=client_socket)
    #thread = threading.Thread(target=serve_client,args=(addr,client_socket))
    #thread.start()