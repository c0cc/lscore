# coding:utf-8
import sys
sys.path.append("../")
from lscore.libs.thread import multi_threading
import random
import time

@multi_threading(20)
def test_func(x):
    time.sleep(random.randint(1,10))
    print x

for x in range(20):
    test_func(x)

test_func.wait(debug=True)
