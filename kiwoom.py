from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slot()
        self.code_list =[]
        self.data=0
        self.name = ""

    def get_data(self, data):
        self.data =data

    def get_name(self, data):
        self.name =data


    # 문자열을 분리후 리스트로 리턴
    def get_code_list(self, data):
        code_list = data.split(';')
        self.code_list = code_list[:-1]

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slot(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

        # 서버로부터 조건식 불러오기
        self.OnReceiveConditionVer.connect(self._receive_condition_ver)
        # 조건명에 해당하는 종목리스트 얻어오기
        self.OnReceiveTrCondition.connect(self._receive_tr_condition)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.login_loop.exec_()

    def _event_connect(self, err):
        if err == 0:
            print("로그인 성공")
        else:
            print("로그인 실패")

        self.login_loop.exit()


    # 시장구분에 따른 종목코드를 반환
    # sMarket – 0:장내, 3:ELW, 4:뮤추얼펀드, 5:신주인수권, 6:리츠,
    # 8:ETF, 9:하이일드펀드, 10:코스닥, 30:K-OTC, 50:코넥스(KONEX)
    def get_code_list_by_market(self, market):
        ret = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = ret.split(';')
        return code_list[:-1]


    # 종목코드의 한글명을 반환
    # 장내외, 지수선옵, 주식선옵 검색 가능
    def get_master_code_name(self, code):
        ret = self.dynamicCall("GetMasterCodeName(QString)", code)
        return ret


    # 종목코드의 상장일을 반환
    # 상장일 포멧 – xxxxxxxx[8]
    def get_master_listed_stock_date(self, code):
        ret = self.dynamicCall("GetMasterListedStockDate(QString)", code)
        return ret

    # 종목코드의 감리구분을 반환
    # 감리구분 – 정상, 투자주의, 투자경고, 투자위험, 투자주의환기종목
    def get_master_construction(self, code):
        ret = self.dynamicCall("GetMasterConstruction(QString)", code)
        return ret

    # Tran 입력 값을 서버통신 전에 입력
    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)



    # Tran을 서버로 송신
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         rqname, trcode, next, screen_no);
        self.tr_loop = QEventLoop()
        self.tr_loop.exec_()

    #조회 정보 요청 : GetCommData()
    def get_comm_data(self, trcode, rqname, index, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                               trcode, rqname, index, item_name)
        return ret.strip()

    def _receive_tr_data(self, screen_no, rqname, trcode, recode_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10001_req":
            self.pbr = self.get_comm_data(trcode, rqname, 0, "PBR")
            self.per = self.get_comm_data(trcode, rqname, 0, "PER")
        elif rqname == "opt10081_req":
            self._opt10081(rqname, trcode)
        elif rqname == "opt10082_req":
            self._opt10082(rqname, trcode)
        elif rqname == "opt10083_req":
            self._opt10083(rqname, trcode)

        try:
            self.tr_loop.exit()
        except:
            pass

    # 주식 주문을 서버로 전송
    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_type, order_no):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                         [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_type, order_no])
        # self.order_loop = QEventLoop()
        # self.order_loop.exec_()

    # 로그인한 사용자 정보를 반환
    def get_login_info(self, tag):
        return self.dynamicCall("GetLoginInfo(QString)", tag)

    # 체결잔고 데이터를 반환
    def get_chejan_data(self, fid):
        ret = self.dynamicCall("GetChejanData(int)", fid)
        return ret

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(self.get_chejan_data(900))
        try:
            self.order_loop.exit()
        except:
            pass


   #레코드 반복 횟수를 반환
    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    # 일봉 데이터 얻기
    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self.get_comm_data(trcode, rqname, i, "일자")
            open = self.get_comm_data(trcode, rqname, i, "시가")
            high = self.get_comm_data(trcode, rqname, i, "고가")
            low = self.get_comm_data(trcode, rqname, i, "저가")
            close = self.get_comm_data(trcode, rqname, i, "현재가")
            volume = self.get_comm_data(trcode, rqname, i, "거래량")

            print(date, open, high, low, close, volume)

    # 주봉 데이터 얻기
    def _opt10082(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        # print("trcode:",trcode)
        # print("rqname:", rqname)
        # print("data_cnt:", data_cnt)


        for i in range(data_cnt):
            # print("i:", i)
            date = self.get_comm_data(trcode, rqname, i, "일자")
            # print("date:",date)
            if date == "20180319":
                open = self.get_comm_data(trcode, rqname, i, "시가")
                high = self.get_comm_data(trcode, rqname, i, "고가")
                low = self.get_comm_data(trcode, rqname, i, "저가")
                close = self.get_comm_data(trcode, rqname, i, "현재가")
                volume = self.get_comm_data(trcode, rqname, i, "거래량")
                name = self.name
                print(self.data, name.zfill(6), open, high, low, close)

    # 월봉 데이터 얻기
    def _opt10083(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self.get_comm_data(trcode, rqname, i, "일자")
            open = self.get_comm_data(trcode, rqname, i, "시가")
            high = self.get_comm_data(trcode, rqname, i, "고가")
            low = self.get_comm_data(trcode, rqname, i, "저가")
            close = self.get_comm_data(trcode, rqname, i, "현재가")
            volume = self.get_comm_data(trcode, rqname, i, "거래량")

            print(date, open, high, low, close, volume)


    # 서버로부터 조건식 불러오기
    # 서버에 저장된 사용자 조건식을 조회해서 임시로 파일에 저장
    def get_condition_load(self):
        self.dynamicCall("GetConditionLoad()")
        self.condition_load_loop = QEventLoop()
        self.condition_load_loop.exec_()

    def _receive_condition_ver(self, ret, msg):
        if ret == 1:
            print("조건식 저장 성공")
        else:
            print("조건식 저장 실패")

        self.condition_load_loop.exit()

    # 조건명 리스트 불러오기
    def get_condition_name_list(self):
        ret =  self.dynamicCall("GetConditionNameList()")
        print(ret)
        return ret

    # 조건에 해당하는 종목리스트 얻어오기
    def send_condition(self, screen_no, condition_name, index, search):
        self.dynamicCall("SendCondition(QString, QString, int, int)",
                         screen_no, condition_name, index, search)
        self.condition_tr_loop = QEventLoop()
        self.condition_tr_loop.exec_()

    def _receive_tr_condition(self, screen_no, code_list, condition_name, index, next ):
        print("condition_name:",condition_name)
        print("code_list1:",code_list)
        # self.code_list = code_list
        self.get_code_list(code_list)
        self.condition_tr_loop.exit()

