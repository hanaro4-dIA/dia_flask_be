import mysql.connector

def get_keywords_from_db():
    #MySql 연결
    connection = mysql.connector.connect(
        host='seochodb.cnisi2wyicv7.ap-northeast-2.rds.amazonaws.com',
        port='3306',
        user='dia',
        password='dia1234',
        database='dIAdb'
    )
    
    cursor = connection.cursor()

    #쿼리
    query = "SELECT id, title, content FROM keyword"
    cursor.execute(query)
    db_results = cursor.fetchall()
    results = [
        {"id": row[0], "title": row[1], "content": row[2]}
        for row in db_results
    ]
    cursor.close()
    connection.close()
    
    # {"id": ..., "title": ...} 형태로 반환
    return results
