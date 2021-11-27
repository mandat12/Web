from redis import StrictRedis as Redis
import csv

connection = Redis()
CACHE_SIZE = 20
POP_SIZE = 0
CACHE_KEYS = "lru-keys"
CACHE_STORE = "lru-store"
connection.flushall()

def add_item(key,value):
    if not connection.hexists(CACHE_STORE, key):
        reorganize()
        connection.hset(CACHE_STORE, key, value['name'])

        for k, v in value.items():
            if k!='name':
                connection.hset(key, k, v)
        connection.lpush(CACHE_KEYS, key)

def update_item(key,value):
    if connection.hexists(CACHE_STORE, key):
        connection.hset(CACHE_STORE, key, value['name'])
        connection.delete(key)

        for k, v in value.iteritems():
            if k!='name':
                connection.hset(key, k, v)

def reorganize():
    if connection.llen(CACHE_KEYS) >= CACHE_SIZE:
        to_pop = connection.rpop(CACHE_KEYS)
        connection.hdel(CACHE_STORE, to_pop)
        connection.delete(to_pop)

def get_item(key):
    result = None
    exist = connection.hget(CACHE_STORE, key)
    if exist: # Cache hit
        connection.lrem(CACHE_KEYS,1,key)
        connection.lpush(CACHE_KEYS,key)
        result=connection.hgetall(key)
    return result


def get_all():
    return connection.hgetall(CACHE_STORE)

def get_cache():
    return connection.lrange(CACHE_KEYS,0,-1)

def get_name(_id):
    return connection.hget(CACHE_STORE,_id)

def delete_item(_id):
    connection.lrem(CACHE_KEYS,1,_id)
    connection.hdel(CACHE_STORE, _id)
    connection.delete(_id)

def get_cache_size():
    return connection.llen(CACHE_KEYS)

def init():
    #test()
    student_data = data_from_csv('student.csv')
    i=0
    student={}
    for _list in student_data:
        if i>0 :
            student[_list[0]]={}
            student[_list[0]]['name']=_list[1]
        i+=1

    marks_data = data_from_csv('marks.csv')
    i=0
    for _marks in marks_data:
        if i>0 :
            if _marks[0] in student:
                student[_marks[0]][_marks[1]]=_marks[2]
        i+=1

    for key, value in student.items():
        add_item(key,value)

def data_from_csv(name):
    csv_data = []
    f = open(name, 'r')
    csv_file = csv.reader(f)
    for row in csv_file:
        csv_data.append(row)
    f.close()
    return csv_data

def on_exit_restore():
    data=[]
    marks=[]

    marks.append(['Id','Subject','Mark'])
    data.append(['Id','Name'])

    students=connection.hgetall(CACHE_STORE)

    for _id, student in students.items():
        data.append([_id,student])
        mark=connection.hgetall(_id)
        for s, m in mark.items():
            marks.append([_id,s,m])

    data_to_csv('student.csv',data)
    data_to_csv('marks.csv',marks)

def data_to_csv(name,data):
    with open(name, 'w+') as fp:
        a = csv.writer(fp, delimiter=',',lineterminator='\n')
        a.writerows(data)

