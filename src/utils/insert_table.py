import pymysql
import datetime


def create_mysql_conn():
    db = pymysql.connect(host="192.168.1.2",
                         port=33717,
                         user="root",
                         passwd="transwarp@123",
                         database="dataset",
                         charset="utf8")
    return db

def insert_data_mysql(tableName, data):
    db = create_mysql_conn()
    try:
        # f格式化字符串（f-string），sql变量里只有data的长度的占位符（values (%s,%s)），没有实际data值
        sql = f"insert into{tableName} values(" + ",".join(["%s"] * len(data[0])) + ")"
        print(sql)

        # 使用cursor（）方法创建一个游标对象cursor
        cursor = db.cursor()
        # 运行sql语句
        # cursor.execute(sql)
        cursor.executemany(sql, data)
        # 提交事务
        db.commit()
        # 关闭游标，释放资源
        cursor.close()
        # 关闭数据链接，释放资源
        db.close()
        # 打印成功
        print("success!")
    # 捕获所有异常
    except Exception as e:
        # 打印异常信息
        print(e)
        # 打印异常出错的表名和数据
        print(tableName, data)
        # 回滚事务，撤销所有未提交的更改，保持数据一致性
        db.rollback()