import sys
import selectors
import json
import io
import struct
from datetime import *
from geopy.geocoders import Nominatim
import geocoder,pickle
import urllib
import simplejson

i = 0

def get_data():
        global i
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
                                    "IHA_enlem": 39.854833,
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
        #data_string = pickle.dumps([0,0])
        data_string = None
        if i < 6:
            #data_string = pickle.dumps([telemetry_list[i],telemetry_list[i+1]])
            data_string = [telemetry_list[i],telemetry_list[i+1]]
            i = i + 1
        elif i==6:
            #data_string = [telemetry_list[i],telemetry_list[i]]
            i=0
        return data_string

class AppServerStorage:
    def _StoreData(telemetri_veri=[{},{}],kilitlenme_veri=[{},{}],giriş_veri=[{},{}],kamikaze_veri=[{},{}]):
            request_post = {
                "/telemetri_gonder":{"takim1":telemetri_veri[0],"takim2":telemetri_veri[1]},
                "/kilitlenme_bilgisi":{"takim1":kilitlenme_veri[0],"takim2":kilitlenme_veri[1]},
                "/giris":{"takım1":giriş_veri[0],"takim2":giriş_veri[1]},
                "/kamikaze_bilgisi":{"takim1":kamikaze_veri[0],"takim2":kamikaze_veri[1]}
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
            #print(f"Sending {self._send_buffer!r} to {self.addr}")
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
            "/api/telemetri_gonder": get_data(),
            "\U0001f436": "\U0001f43e Playing ball! \U0001f3d0",
            "/sunucusaati":"Saat:{} ,Dakika:{} ,Saniye:{} ,MiliSaniye:{}".format(datetime.now().strftime('%H:'),datetime.now().strftime('%M:'),datetime.now().strftime('%S'),datetime.now().strftime('%f')),
            
        }
        if action == "get":
            query = self.request.get("value")
            #if query == "/api/telemetri_gonder":
            #    i = i + 1
            answer = request_get.get(query) or f"No match for '{query}'."
            content = {"result": answer}
        elif action == "post":
            sent = self.request.get("sent")
            value = self.request.get("value")
            if value == '/api/telemetri_gonder':
                answer=AppServerStorage._StoreData(telemetri_veri=sent)
            elif value == '/api/kilitlenme_bilgisi':
                answer=AppServerStorage._StoreData(kilitlenme_veri=sent)
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
            #print(f"Received request {self.request!r} from {self.addr}")
            print(f"Received request from {self.addr}")
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

