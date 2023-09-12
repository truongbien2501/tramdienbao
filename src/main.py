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
import pandas as pd

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
        data = pd.DataFrame()
        data['time'] = pd.date_range(bd,kt,freq='T')
        matram = self.chuyenmatram(self.spinner.text)
        
        pth = 'http://113.160.225.84:2018/API_TTB/XEM/solieu.php?matram={}&ten_table={}&sophut=1&tinhtong=0&thoigianbd=%27{}%2000:00:00%27&thoigiankt=%27{}%2023:59:00%27'
        pth = pth.format(matram,'mucnuoc_oday',bd.strftime('%Y-%m-%d'),kt.strftime('%Y-%m-%d'))
        df = pd.read_html(pth)
        df[0].rename(columns={"thoi gian":'time','so lieu':'H'},inplace=True)
        df = df[0].drop('Ma tram',axis=1)
        df['time'] = pd.to_datetime(df['time'])
        data = data.merge(df,how='left',on='time')
        
        pth = 'http://113.160.225.84:2018/API_TTB/XEM/solieu.php?matram={}&ten_table={}&sophut=1&tinhtong=0&thoigianbd=%27{}%2000:00:00%27&thoigiankt=%27{}%2023:59:00%27'
        pth = pth.format(matram,'mua_oday_thuyvan',bd.strftime('%Y-%m-%d'),kt.strftime('%Y-%m-%d'))
        df = pd.read_html(pth)
        df[0].rename(columns={"thoi gian":'time','so lieu':'mua'},inplace=True)
        df = df[0].drop('Ma tram',axis=1)
        df['time'] = pd.to_datetime(df['time'])
        data = data.merge(df,how='left',on='time')
       
        data.set_index('time',inplace=True)
        data['mua_gio'] = data['mua'].rolling(60,min_periods=1).sum()
        data = data.drop('mua',axis=1)
        # data = data[data.index.minute == 0]
        epsilon = 1e-10
        data = data.applymap(lambda x: 0 if abs(x) < epsilon else x)    
        data =data.astype(float)
        return data
    
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
        h1 = h1 *100
        h2 = h2 *100
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
        if now.hour==1 or now.hour==7 or now.hour==13 or now.hour==19:
            rr = '3'
        else:
            rr = '4'
            
        if r ==0:
            rrrr = rr + '0000'
        elif r > 0 and r < 10:
            rrrr = rr + '000' + '{:.0f}'.format(r)
        elif r >= 10 and r < 100:
            rrrr = rr + '00' + '{:.0f}'.format(r)   
        elif r >= 100 :
            rrrr = rr + '0' + '{:.0f}'.format(r)    
        return rrrr
                
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
        batdau = 'ZCZC\n' + 'TVS01 DDDD ' + now.strftime('%d%H00') + '\n' + 'HHXX ' + now.strftime('%d%H1') + '\n' + self.spinner.text
        df = self.TTB_API_mua()
  
        if now.hour==7:
            df19 = df[(df.index > (now-timedelta(hours=18))) & (df.index <= (now-timedelta(hours=12)))]
            df19 = df19[df19.index.minute==0]
            df1 = df[(df.index > (now-timedelta(hours=12))) & (df.index <= (now-timedelta(hours=6)))]
            df1 = df1[df1.index.minute==0]
            df7 = df[(df.index > (now-timedelta(hours=6))) & (df.index <= now)]
            df7 = df7[df7.index.minute==0]
            # print(df1)

            df_h19 = df19.dropna(subset=['H'], how='any')
            h19 = df_h19.iloc[-1]['H']
            
            mua01 = df1['mua_gio'].sum()
     
            df_h1 = df1.dropna(subset=['H'], how='any')
            h1 = df_h1.iloc[-1]['H']
            
            mua07 = df7['mua_gio'].sum()
            df_h7 = df7.dropna(subset=['H'], how='any')
            h7 = df_h7.iloc[-1]['H']
            
            dienbao_h = ' 22 ' + (now - timedelta(hours=6)).strftime('%d%H') + ' ' + self.buc_dien_h(h1,h19) + ' ' +now.strftime('%d%H') + ' ' + self.buc_dien_h(h7,h1)
            dienbao_r = '\n      44 ' + (now - timedelta(hours=6)).strftime('%d%H') + ' ' + self.buc_dien_r(mua01) + ' ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua07)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'

        elif now.hour==13 or now.hour==19 or now.hour==1:
            df7 = df[(df.index > (now-timedelta(hours=12))) & (df.index <= (now-timedelta(hours=6)))]
            df7 = df7[df7.index.minute==0]
            df13 = df[(df.index > (now-timedelta(hours=6))) & (df.index <= now)]
            df13 = df13[df13.index.minute==0]
            # print(df1)
            mua13 = df13['mua_gio'].sum()
            
            df_h7 = df7.dropna(subset=['H'], how='any')
            h7 = df_h7.iloc[-1]['H']
            
            df_h13 = df13.dropna(subset=['H'], how='any')
            h13 = df_h13.iloc[-1]['H']
            dienbao_h = ' 22 ' + now.strftime('%d%H') + ' ' + self.buc_dien_h(h13,h7)
            dienbao_r = '\n\t      44 ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua13)   + '=' 
            dienbao =  batdau + dienbao_h + dienbao_r + '\n\nNNNN'
        elif now.hour==4 or now.hour==10  or now.hour==16 or now.hour==22:
            df1 = df[(df.index > (now-timedelta(hours=6))) & (df.index <= (now-timedelta(hours=3)))]
            df1 = df1[df1.index.minute==0]
            df4= df[(df.index > (now-timedelta(hours=3))) & (df.index <= now)]
            df4 = df4[df4.index.minute==0]
            # print(df1)
            mua4 = df4['mua_gio'].sum()
            
            df_h1 = df1.dropna(subset=['H'], how='any')
            h1 = df_h1.iloc[-1]['H']
            
            df_h4 = df4.dropna(subset=['H'], how='any')
            h4 = df_h4.iloc[-1]['H']
            dienbao_h = ' 22 ' + now.strftime('%d%H') + ' ' + self.buc_dien_h(h4,h1)
            dienbao_r = '\n      44 ' + now.strftime('%d%H') + ' ' + self.buc_dien_r(mua4)   + '=' 
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
