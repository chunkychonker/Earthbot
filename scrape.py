import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.hset("environment_news", 999, "hello")
x = r.hget("environment_news", 999)
print(x)