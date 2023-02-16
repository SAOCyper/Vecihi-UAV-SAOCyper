from datetime import datetime
lock_on_started = False
lock_on_finished = False
class TelemetryCreate():
            
    def __init__(self):
        self.iha_bilgiler = {"IHA_enlem":0 ,
                            "IHA_boylam":0,
                            "IHA_irtifa": 0,
                            "IHA_dikilme": 0,
                            "IHA_yonelme": 0,
                            "IHA_yatis": 0,
                            "IHA_hiz": 0,
                            "IHA_batarya": 0,
                            "IHA_otonom": 0,
                            "IHA_kilitlenme": 0,
                            "Hedef_merkez_X": 0,
                            "Hedef_merkez_Y": 0,
                            "Hedef_genislik": 0,
                            "Hedef_yukseklik": 0}
        
    def _GPS_Saati(self):
        time_format = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        splitted = time_format.split(":")
        splitted1 = splitted[2].split('.')
        self.gps_saat = {"saat":splitted[0],"dakika":splitted[1],"saniye":splitted1[0],"milisaniye":splitted1[1]}
        return self.gps_saat
    def Kilitlenme_başlangıç(self):
        time = self._GPS_Saati()
        self.lock_on_start = {"kilitlenmeBaslangicZamani":{"saat:{},dakika:{},saniye:{},milisaniye:{}".format(time["saat"],time["dakika"],time["saniye"],time["milisaniye"])}}
        return self.lock_on_start
    def Kilitlenme_bitiş(self):
        time = self._GPS_Saati()
        self.lock_on_finish = {"kilitlenmeBitisZamani":{"saat:{},dakika:{},saniye:{},milisaniye:{}".format(time["saat"],time["dakika"],time["saniye"],time["milisaniye"])}}
        return self.lock_on_finish
    def Iha_telemetri_bilgi(self,takım_numarası:int,iha_bilgiler:list):
        time = self._GPS_Saati()
        takım_numarası = {"takim_numarasi": takım_numarası}
        self.takım_numarasi = takım_numarası
        i = 0
        for key , value in self.iha_bilgiler.items() :
            self.iha_bilgiler[key] = iha_bilgiler[i]
            i=i+1
        self.telemetry_data = self.takım_numarasi | self.iha_bilgiler | self.gps_saat    
        print(self.telemetry_data)
    def Iha_kilitlenme_bilgi(self,process:bool):
        global lock_on_started , lock_on_finished , locked_on
        if locked_on== True and lock_on_started == True :
            self.Kilitlenme_başlangıç()
            process = True
            return process
        elif locked_on == True and lock_on_finished == True:
            locked_on = {"otonom_kilitlenme": 1}
            self.Kilitlenme_bitiş()
            self.kilitlenme_bilgisi = self.lock_on_start | self.lock_on_finish | locked_on
            return self.kilitlenme_bilgisi
        elif locked_on == False or lock_on_started == False or lock_on_finished == False:
            process = False
            return process
#Creates complete dictionary of telemetry data
bilgiler = [43.654352,22.31245421,105,6,252,2,245,19,1,1,421,240,143,57]
telemetry=TelemetryCreate()
telemetry.Iha_telemetri_bilgi(1,bilgiler)
process = False
#Creates complete dictionary of lock_on_data
while True : 

    result=telemetry.Iha_kilitlenme_bilgi(process)
    if result == True or result == False :
        print(result)
        process = True
        continue
    else :
        print(result)
        process=False
        continue