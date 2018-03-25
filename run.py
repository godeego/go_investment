import sys
from PyQt5.QtWidgets import *
from kiwoom import *
import time

app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()

# 조건식 불러오기
# kiwoom.get_condition_load()

# 조건명 리스트
# list = kiwoom.get_condition_name_list()
# print("list:",list)

# 조건에 해당하는 종목리스트
# kiwoom.send_condition("0101", "주봉기준", "001", 0)
# print("code_list_run:",kiwoom.code_list)
# code_list = kiwoom.code_list

#종목이름얻기
# for code in code_list:
#     print("code:",code)
#     name = kiwoom.get_master_code_name(code)
#     print("name:",name)

# code =  "039490"   #종목코드
date = "20180319"    #기준일자
have_list =["000650","003090","005930","009835","023530","035420","039130","055550","066570","068400","082740","111770","136480","175330"]

print("종목코드 종목이름 시가 고가 저가 종가")
for code in have_list:
    kiwoom.get_data(code)
    name = kiwoom.get_master_code_name(code)
    kiwoom.get_name(name)
    kiwoom.set_input_value("종목코드", code)
    kiwoom.set_input_value("기준일자", date)
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10082_req", "opt10082", 0, "0101")
    time.sleep(1)


#kiwoom.get_master_code_name()
# kiwoom.set_input_value("종목코드", code)
# kiwoom.set_input_value("기준일자", date)
# kiwoom.set_input_value("수정주가구분", 1)
# kiwoom.comm_rq_data("opt10082_req", "opt10082", 0, "0101")

# while kiwoom.remained_data == True:
#     time.sleep(3)
#     kiwoom.set_input_value("종목코드", code)
#     kiwoom.set_input_value("기준일자", date)
#     kiwoom.set_input_value("수정주가구분", 1)
#     kiwoom.comm_rq_data("opt10082_req", "opt10082", 2, "0101")


