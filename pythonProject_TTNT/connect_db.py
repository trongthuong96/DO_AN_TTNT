import _sqlite3
import sys
from datetime import datetime
import datetime as day

class connect_db:

    # kết nối data
    def connect(self):

        try:
            conn = _sqlite3.connect("venv/database/diemdanh1.db")

        except _sqlite3.Error as e:

            print("Error %s:" % e.args[0])
            sys.exit(1)
        return conn

    # Kiểm Tra SV trong data
    def check(self, mssv):
        conn = self.connect()
        cur = conn.cursor()
        mssv = str(mssv).split(" ")[0]

        cur.execute("select mssv from sinhvien where mssv = " + mssv)
        conn.commit()
        data = '0'
        for row in cur:
            data = row

        conn.close()
        return data[0]

    # chức năng insert thông tin sinh viên vào bảng sinhvien
    def upsinhvien(self, mssv, name, classcode):
        conn = self.connect()
        cur = conn.cursor()

        mssv = str(mssv).split(" ")[0]
        classcode = str(classcode).split(" ")[0]

        data = (mssv, name, classcode)

        try:

            cur.execute("insert into sinhvien(mssv,name,classcode) values(?,?,?)", data)
            conn.commit()

        except _sqlite3.Error as e:
            if str(e.args).split(':')[0] == "('UNIQUE constraint failed":
                print("Đã có mssv này")
        conn.close()

    # chức năng insert sinh viên trong class vào bảng denlop để điểm danh theo ca
    def upclassdiemdanh(self, classcode):
        conn = self.connect()
        cur = conn.cursor()
        # Làm sạch dữ liệu
        classcode = str(classcode).split(" ")[0]
        # mssv = str(mssv).split(" ")[0]

        # Kiểm tra có mã lớp k?
        # Sinh vien cùng lớp
        cur.execute("select mssv from sinhvien where classcode = ? order by mssv", (classcode,))

        # lưu thông tin lớp vào mảng
        data = []
        for rows in cur:
            data.append(rows)

        # Kiểm tra nếu không có mssv thì thoát, nếu có thì thêm vào bảng denlop
        if data == []:
            conn.close()
            return 0, None

        else:
            ca = '6'
            now = datetime.now()
            today = now.strftime("%H%M")

            if today >= '0645' and today <= '0910':
                ca = '1'
            elif today >= '0920' and today <= '1145':
                ca = '2'
            elif today >= '1230' and today <= '1455':
                ca = '3'
            elif today >= '1505' and today <= '1730':
                ca = '4'
            elif today >= '1800' and today <= '2030':
                ca = '5'

            # Lấy ngày hiện tại
            days = day.date.today()

            cur.execute("select time from denlop")
            data2 = []
            for row in cur:
                data2.append(row)

            # So sánh ngày hiện tại và ngày trong table dentop
            temp = True
            for i in range(len(data2)):
                if str(days) == str(data2[i][0]):
                    temp = False

            if temp:
                for i in range(len(data)):
                    cur.execute("INSERT INTO denlop(mssv, time, cahoc) VALUES(?, date('now'), ?)", (data[i][0], ca))
                    conn.commit()

            else:
                # Sinh viên cùng lớp cùng ca trong bảng denlop
                cur.execute("select d.mssv from denlop d, sinhvien s where d.mssv = s.mssv and cahoc = ? and classcode = ? ORDER BY d.mssv", (ca,classcode))
                data1 = []
                for rows in cur:
                    data1.append(rows)

                for i in range(len(data) - len(data1)):
                    print(i+len(data1))
                    cur.execute("INSERT INTO denlop(mssv, time, cahoc) VALUES(?, date('now'), ?)",(data[i+len(data1)][0], ca))
                    conn.commit()

        conn.close()
        return ca, data

    # Điểm danh sinh viên
    def diemdanh_sv(self, mssv, ca):
        conn = self.connect()
        cur = conn.cursor()

        days = day.date.today()

        cur.execute("UPDATE denlop SET comat = ? where mssv = ? and cahoc = ? and time = ?", (1, mssv, ca, str(days)))
        conn.commit()
        conn.close()

    def xuatfile(self, classcode):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("select d.mssv as MSSV, name as [Họ Tên], classcode as [Lớp], cahoc as [Ca học], time as [Thời gian], CASE comat WHEN 0 THEN'Vắng' ELSE'Có Mặt' END as [Điểm Danh] from denlop as d, sinhvien as s WHERE d.mssv = s.mssv AND classcode = ? ORDER by time",(classcode,))

        data = [("MSSV", "Họ Tên", "Lớp", "Ca Học", "Thời Gian", "Điểm Danh")]

        for rows in cur:
            data.append(rows)

        conn.commit()
        conn.close()
        return data
