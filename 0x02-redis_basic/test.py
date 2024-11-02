from functools import wraps

# def my_decorator(func):
#     @wraps(func)  # استخدام wraps لحفظ معلومات الدالة الأصلية
#     def wrapper(*args, **kwargs):
#         print("before")
#         result = func(*args, **kwargs)  # استدعاء الدالة الأصلية
#         print("after")
#         return result
#     return wrapper

# @my_decorator
# def say_hello(name):
#     """ welcome """  # تأكد من عدم تعليقها
#     return f"welcome {name}!"

# print(say_hello("moaz"))
# print(say_hello.__name__)  # ستكون "say_hello" بدلاً من "wrapper"
# print(say_hello.__doc__)   # الآن ستظهر "هذه الدالة تقول مرحبا"



from functools import wraps
from typing import Union, Callable, Optional
from functools import wraps
import redis
import uuid


def call_history(method: Callable) -> Callable:
    """Stores the history of inputs and outputs for a particular function"""
    method_key = method.__qualname__
    inputs, outputs = method_key + ':inputs', method_key + ':outputs'

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(inputs, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(result))
        return result
    return wrapper


def count_calls(method : Callable) -> Callable:
    key = method.__qualname__ 
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper
    
    
def replay(method : callable) -> None:
    redis = method.__self__._redis
    method_key = method.__qualname__
    my_method = redis.get(method_key)
    print(f"{method_key} was {my_method.decode('utf-8')} called times:")
    inputs, outputs = method_key + ':inputs', method_key + ':outputs'
    IOTuple = zip(redis.lrange(inputs, 0, -1), redis.lrange(outputs, 0, -1))
    for inp, outp in list(IOTuple):
        attr, data = inp.decode("utf-8"), outp.decode("utf-8")
        print(f'{method_key}(*{attr}) -> {data}')

class Cache:
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()
        
    @call_history
    @count_calls
    def store(self ,data : Union[str, bytes, int, float] ) -> str:
        key = str(uuid.uuid4)
        self._redis.set(key, data)
        return key
    
    def get(self, key : str, fn : Optional[callable] = None) -> str:
        data = self._redis.get(key)
        return fn(data) if fn is not None else data
    
    def get_str(self, data: str) -> str:
        return data.decode('utf-8')

    def get_int(self, data: str) -> int:
        return int(data)


cache = Cache()
cache.store("foo")
cache.store("bar")
cache.store(42)
replay(cache.store)
