import pymysql
conn=pymysql.connect(host="192.168.3.127",user="cp_user",password="your-strong-password",database="cyberpatriot_runbook")
print("Connected!")
conn.close()
