from ftplib import FTP
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from io import BytesIO
from datetime import datetime,timedelta
from kivy.uix.spinner import Spinner
import numpy as np
import requests
# kivy.require('2.0.0')
class FTPApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.text_box = TextInput(multiline=True)
        layout.add_widget(self.text_box)
        
        # Tạo một Spinner
        self.spinner = Spinner(text='Chọn trạm điện báo', values=('71539', '71542'))
        
        # spinner.bind(text=on_spinner_select)

        layout.add_widget(self.spinner)
        
        # Tạo một text để hiển thị nội dung
        # self.my_text = Label(text='')
        button_layout = BoxLayout(orientation='horizontal')
        # Tạo một button
        button1 = Button(text='Soandien!')
        button1.bind(on_press=self.soandien_button_click)  # Khi button được nhấn, gọi hàm on_button_click
        
        # Tạo một button
        button2 = Button(text='Chuyển điện')
        button2.bind(on_press=self.send_button_click)  # Khi button được nhấn, gọi hàm on_button_click
        button_layout.add_widget(button1)
        button_layout.add_widget(button2)

        # Thêm button và text vào layout
        # layout.add_widget(self.my_text)
        layout.add_widget(button_layout)

        return layout
    
    def chuyenmatram(self,matram):
        tram = ['71539','71542']
        ma_api = ['551900','552100']
        idx = tram.index(matram)
        return ma_api[idx]
    
    def chuyenmatram_txt_lu(self,matram):
        tram = ['71539','71542']
        ma_api = ['53992','54292']
        idx = tram.index(matram)
        return ma_api[idx]
    
    def chuyenmatram_txt_can(self,matram):
        tram = ['71539','71542']
        ma_api = ['53990','54290']
        idx = tram.index(matram)
        return ma_api[idx]
        
    def TTB_API_mua(self):
        now = datetime.now()
        kt = datetime(now.year,now.month,now.day,now.hour)
        bd = kt - timedelta(days=1)
        # data = pd.DataFrame()
        # data['time'] = pd.date_range(bd,kt,freq='T')
        matram = self.chuyenmatram(self.spinner.text)
        # muc nuoc
        pth = 'http://113.160.225.84:2018/API_TTB/JSON/solieu.php?matram={}&ten_table={}&sophut=1&tinhtong=0&thoigianbd=%27{}%2000:00:00%27&thoigiankt=%27{}%2023:59:00%27'
        pth = pth.format(matram,'mucnuoc_oday',bd.strftime('%Y-%m-%d'),kt.strftime('%Y-%m-%d'))
        response = requests.get(pth)
        mucnuoc = np.array(response.json())
        # mua
        pth = 'http://113.160.225.84:2018/API_TTB/JSON/solieu.php?matram={}&ten_table={}&sophut=1&tinhtong=0&thoigianbd=%27{}%2000:00:00%27&thoigiankt=%27{}%2023:59:00%27'
        pth = pth.format(matram,'mua_oday_thuyvan',bd.strftime('%Y-%m-%d'),kt.strftime('%Y-%m-%d'))
        response = requests.get(pth)
        mua = np.array(response.json())
        return mucnuoc,mua
    
    def ftp_sever(self,tram):
        # Thông tin máy chủ FTP và đường dẫn đến file
        ftp_host = '113.160.225.111'
        ftp_user = 'kttvttbdb'
        ftp_password = '618778'
        file_path = 'Dulieu-Bantinkttvttb/5-Quang Ngai/PHAN MEM/DIENBAO'
        # Kết nối đến máy chủ FTP
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)
        ftp.cwd(file_path)
        contents = None

        try:
            with BytesIO() as file:
                ftp.retrbinary('RETR ' + tram, file.write)
                contents = file.getvalue().decode('utf-8')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
                
        ftp.quit()
        return contents
    def write_ftp_sever(self,tram,noidung):
        now = datetime.now()
        # Thông tin máy chủ FTP và đường dẫn đến file
        ftp_host = '113.160.225.111'
        ftp_user = 'kttvttbdb'
        ftp_password = '618778'
        if now.month >=9:
            file_path = 'Dulieu-Bantinkttvttb/5-Quang Ngai/PHAN MEM/DIENBAO'
        else:
            file_path = 'datattb'
        # Kết nối đến máy chủ FTP
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)
        ftp.cwd(file_path)
        # file = open(r'C:\Users\Administrator\Desktop\tap huan FES\chep so.xls','rb')
        ftp.storbinary('STOR ' + tram, noidung)
        # file.close()                                   
        ftp.quit()
    def buc_dien_h(self,h1,h2):
        h1 = float(h1) *100
        h2 = float(h2) *100
        if h1 > h2:
            xuthe ='2'
        elif h1 < h2:
            xuthe= '1'
        else:
            xuthe = '0'
        # 22893..
        if h1 > -100 and h1 < -10:
            hhhh = xuthe + "50" + '{:.0f}'.format(h1)
        elif h1 > -10 and h1 < 0:
            hhhh = xuthe + "500" + '{:.0f}'.format(h1)
        elif h1 > 0 and h1 < 10:
            hhhh = xuthe + "000" + '{:.0f}'.format(h1)
        elif h1 > 10 and h1 < 100:
            hhhh = xuthe + "00" + '{:.0f}'.format(h1)
        elif h1 > 100 and h1 <1000:
            hhhh = xuthe + "0" + '{:.0f}'.format(h1)    
        elif h1 > 1000:
            hhhh = xuthe + '{:.0f}'.format(h1)
        return hhhh
            
    def buc_dien_r(self,r):
        now = datetime.now()
        if (now.hour==1 or now.hour==7 or now.hour==13 or now.hour==19 ) and now.month >=9 :
            rr = '3'
        elif now.hour== 4 or now.hour==10 or now.hour==16 or now.hour==22:
            rr = '4'
        if (now.hour==1 or now.hour==7 or now.hour==13 or now.hour==19 ) and now.month < 9 :
            rr = '4'    
        else:
            rr = '3'
            
        if r ==0:
            rrrr = rr + '0000'
        elif r > 0 and r < 10:
            rrrr = rr + '000' + '{:.0f}'.format(r)
        elif r >= 10 and r < 100:
            rrrr = rr + '00' + '{:.0f}'.format(r)   
        elif r >= 100 :
            rrrr = rr + '0' + '{:.0f}'.format(r)    
        return rrrr
            
       
    def get_h(self,data,gioget):
        for a in range(data.shape[0]-1,1,-1):
            if gioget.strftime('%Y-%m-%d %H:%M:%S') == data[a]['Thoigian_SL']:
                break
        return data[a]['Solieu']        
         
    def tinhmua(self,data,bd,kt):
        tonngmua = 0
        for a in range(data.shape[0]-1,1,-1):
            date_object = datetime.strptime(data[a]['Thoigian_SL'], "%Y-%m-%d %H:%M:%S")
            if date_object > bd and date_object <=kt:
                tonngmua+= float(data[a]['Solieu'])
        return tonngmua
    
    def soandien_button_click(self, instance):
        if self.spinner.text =='Chọn trạm điện báo':
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text='Vui lòng chọn trạm!'))
            # Thêm nút tắt thông báo
            dismiss_button = Button(text='Đóng')
            content.add_widget(dismiss_button)
            # Tạo popup với nội dung và nút tắt thông báo
            popup = Popup(title='Thông báo', content=content, size_hint=(None, None), size=(400, 300))
            # Thiết lập hàm callback khi nút tắt được nhấn
            dismiss_button.bind(on_release=popup.dismiss)
            # Hiển thị thông báo
            popup.open()
            return
        now = datetime.now()
        now = datetime(now.year,now.month,now.day,now.hour)
        batdau = 'ZCZC\n' + 'TVS01 DDDD ' + now.strftime('%d%H00') + '\n' + 'HHXX ' + now.strftime('%d%H1') + '\n' + self.spinner.text
        
        
        mucnuoc,mua = self.TTB_API_mua()

        if now.hour==7:
            gio19 = now-timedelta(hours=12)
            gio01 = now-timedelta(hours=6)
            gio7 = now

            h19 = self.get_h(mucnuoc,gio19)
            h1 = self.get_h(mucnuoc,gio01)
            h7 = mucnuoc[-1]['Solieu']

            mua01 = self.tinhmua(mua,gio19,gio01)
            mua07 = self.tinhmua(mua,gio01,gio7)
            # print(h19)
            dienbao_h = ' 22 ' +gio01.strftime('%d%H') + ' ' + self.buc_dien_h(h1,h19) + ' ' +now.strftime('%d%H') + ' ' + self.buc_dien_h(h7,h1)
            dienbao_r = '\n      44 ' + gio01.strftime('%d%H') + ' ' + self.buc_dien_r(mua01) + ' ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua07)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'

        elif now.hour==13 or now.hour==19 or now.hour==1:
            gio01 = now-timedelta(hours=6)
            gio7 = now
            
            h1 = self.get_h(mucnuoc,gio01)
            h7 = mucnuoc[-1]['Solieu']
            mua07 = self.tinhmua(mua,gio01,gio7)
            
            dienbao_h = ' 22 ' + now.strftime('%d%H') + ' ' + self.buc_dien_h(h7,h1)
            dienbao_r = '\n      44 ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua07)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'
        elif now.hour==4 or now.hour==10  or now.hour==16 or now.hour==22:
            gio01 = now-timedelta(hours=3)
            gio7 = now
            
            h1 = self.get_h(mucnuoc,gio01)
            h7 = mucnuoc[-1]['Solieu']
            mua07 = self.tinhmua(mua,gio01,gio7)
            
            dienbao_h = ' 22 ' + now.strftime('%d%H') + ' ' + self.buc_dien_h(h7,h1)
            dienbao_r = '\n      44 ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua07)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'
        else:
            gio01 = now-timedelta(hours=6)
            gio7 = now
            
            h1 = self.get_h(mucnuoc,gio01)
            h7 = mucnuoc[-1]['Solieu']
            mua07 = self.tinhmua(mua,gio01,gio7)
            
            dienbao_h = ' 22 ' + now.strftime('%d%H') + ' ' + self.buc_dien_h(h7,h1)
            dienbao_r = '\n      44 ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua07)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'
            
        self.text_box.text = dienbao

    def send_button_click(self, instance):
        now = datetime.now()
        noidung = self.text_box.text.encode('utf-8')  # Chuyển chuỗi thành dữ liệu bytes
        noidung_file = BytesIO(noidung)
        if now.month >=9:
            tram_txt = 'DATA' + self.chuyenmatram_txt_lu(self.spinner.text) + '.txt'
        else:
            tram_txt = 'DATA' + self.chuyenmatram_txt_can(self.spinner.text) + '.txt'
            
        self.write_ftp_sever(tram_txt,noidung_file)
        # Tạo một thông báo
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Dữ liệu đã được chuyển đi!'))
        
        # Thêm nút tắt thông báo
        dismiss_button = Button(text='Đóng')
        content.add_widget(dismiss_button)
        
        # Tạo popup với nội dung và nút tắt thông báo
        popup = Popup(title='Thông báo', content=content, size_hint=(None, None), size=(400, 300))
        
        # Thiết lập hàm callback khi nút tắt được nhấn
        dismiss_button.bind(on_release=popup.dismiss)
        
        # Hiển thị thông báo
        popup.open()
        
if __name__ == '__main__':
    FTPApp().run()
