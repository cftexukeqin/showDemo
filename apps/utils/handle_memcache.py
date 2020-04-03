import memcache
mc = memcache.Client(['127.0.0.1:11211'],debug=True)


def get_value(key):
    return mc.get(key)

def set_key(key,value):
    mc.set(key,value,time=60*60*24)


def delete_key(key):
    mc.delete(key)