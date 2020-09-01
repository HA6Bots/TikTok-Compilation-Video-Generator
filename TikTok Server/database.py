import mysql.connector
from mysql.connector import pooling
from datetime import date
import pickle
import settings
current_date = date.today()
connection_pool = None

def startDatabase():
    beginDatabaseConnection()
    initDatabase()

def initDatabase():
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("SET sql_notes = 0; ")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS `tiktokdb` ;")
    cursor.execute("USE tiktokdb;")
    cursor.execute("SET sql_notes = 0;")
    cursor.execute("set global max_allowed_packet=67108864;")
    cursor.execute("create table IF NOT EXISTS clip_bin (clip_num int NOT NULL AUTO_INCREMENT, PRIMARY KEY (clip_num), clip_id varchar(100), date varchar(40), status varchar(100),  clipwrapper BLOB, filter_name varchar(70));")

    cursor.execute("create table IF NOT EXISTS filters (num int NOT NULL AUTO_INCREMENT, PRIMARY KEY (num), name varchar(70), filterwrapper BLOB);")
    cursor.execute("SET sql_notes = 1; ")

def beginDatabaseConnection():
    global connection_pool
    connection_pool = pooling.MySQLConnectionPool(
    pool_size=32,
        pool_reset_session=True,
      host=settings.databasehost,
      user=settings.databaseuser,
      passwd=settings.databasepassword,
    )
    print("Started database connection")
    

def addFoundClip(tiktokclip, filterName):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")

    id = tiktokclip.id
    clipblob = pickle.dumps(tiktokclip)
    query = "INSERT INTO clip_bin(clip_id, date, filter_name, status, clipwrapper) VALUES(%s, %s, %s, 'FOUND', %s);"
    args = (id, current_date, filterName, clipblob)

    cursor.execute(query, args)

    connection_object.commit()
    cursor.close()
    connection_object.close()

def getFoundClips(filter, limit):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")

    query = "select * FROM clip_bin WHERE filter_name = %s and status = 'FOUND' LIMIT %s;"
    args = (filter,limit)

    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[4]))
    connection_object.commit()
    cursor.close()
    connection_object.close()
    return results


def addFilter(filter_name, filterobject):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = f"INSERT INTO filters(`name`, `filterwrapper`) VALUES(%s, %s);"
    filterobjectdumped = pickle.dumps(filterobject)
    args = (filter_name, filterobjectdumped)
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()
    
def getAllSavedFilters():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT name, filterwrapper FROM filters;"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append([res[0], pickle.loads(res[1])])
    cursor.close()
    connection_object.close()
    return results

def getSavedFilterByName(filterName):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT filterwrapper FROM filters WHERE name = %s;"
    args = (filterName,)
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = pickle.loads(result[0][0])
    cursor.close()
    connection_object.close()
    return results

def getFilterNames():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT name FROM filters;"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res[0])
    cursor.close()
    connection_object.close()
    return results

def getFilterClipCount(filter):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT COUNT(*) FROM clip_bin WHERE filter_name = %s"
    args = (filter,)
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)
    cursor.close()
    connection_object.close()
    return results

def getFilterClipCountByStatus(filter,status):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT COUNT(*) FROM clip_bin WHERE filter_name = %s and status = %s"
    args = (filter,status)
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)
    cursor.close()
    connection_object.close()
    return results

def getFilterClipsByStatusLimit(filterName, status, limit):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT * FROM clip_bin WHERE filter_name = %s and status = %s LIMIT %s;"
    args = (filterName,status, limit)
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[4]))
    cursor.close()
    connection_object.close()
    return results


def geClipsByStatusWithoutIds(filterName, status, limit, idlist):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    format_strings = ','.join(["%s"] * len(idlist))

    query = f"SELECT * FROM clip_bin WHERE filter_name = '{filterName}' and status = '{status}'" \
            f" and clip_id not in ({format_strings})" \
            f" LIMIT {int(limit)};"

    cursor.execute(query, tuple(idlist))
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[4]))
    cursor.close()
    connection_object.close()
    return results


def getClipById(id):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT clipwrapper FROM clip_bin WHERE clip_id = %s;"
    args = (id, )
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[0]))
    cursor.close()
    connection_object.close()
    return results[0]

def getClipsByStatus(status):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT clipwrapper FROM clip_bin WHERE status = %s;"
    args = (status, )
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[0]))
    cursor.close()
    connection_object.close()
    return results

def getFilterClipsByStatus(filterName, status):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT clipwrapper FROM clip_bin WHERE status = %s and filter_name=%s;"
    args = (status, filterName)
    cursor.execute(query, args)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(pickle.loads(res[0]))
    cursor.close()
    connection_object.close()
    return results


def getAllSavedClipIDs():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "SELECT clip_id FROM clip_bin;"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)
    cursor.close()
    connection_object.close()
    return results

def updateStatus(clip_id, status):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "UPDATE clip_bin SET status = %s WHERE clip_id = %s;"
    args = (status, clip_id)
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def updateStatusWithClip(clip_id, status, clip):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE tiktokdb;")
    query = "UPDATE clip_bin SET status = %s, clipwrapper = %s WHERE clip_id = %s;"
    tiktokclip = pickle.dumps(clip)
    args = (status, tiktokclip, clip_id)
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

