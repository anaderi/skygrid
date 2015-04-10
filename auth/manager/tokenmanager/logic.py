import random
import string


KEYLEN = 90

def generate_token():
    token = ""
    for _ in xrange(KEYLEN):
        token += random.choice(string.ascii_letters + string.digits)

    redis_lock_key = "token:" + token + ":lock"

    return token, redis_lock_key


def add_token(r, user, urls):
    token, redis_lock_key = generate_token()
    l = r.lock(redis_lock_key, blocking_timeout=0)

    while not l.acquire():
        token, redis_lock_key = generate_token()
        l = r.lock(redis_lock_key)

    r.sadd("token:" + token, *urls)
    r.set("owner:" + token, user)

    r.sadd("tokens:" + user, token)

    l.release()

    return token


def delete_token(r, token, user):
    if r.get("owner:" + token) != user:
        return False

    r.delete(
        "token:" + token,
        "owner:" + token
    )
    r.srem("tokens:" + user, token)
    return True
