import os
import math

def calc(a,b,op):
    if op=="add":
        return a+b
    elif op=="sub":
        return a-b
    elif op=="mul":
        return a*b
    elif op=="div":
        return a/b
    else:
        return "wrong"

def getUserData():
    users = []
    for i in range(0,5):
        name=input("Enter name")
        age=input("Enter age")
        users.append({"name":name,"age":age})
    return users

def process():
    data = getUserData()

    total = 0

    for i in range(len(data)):
        total += int(data[i]["age"])

    avg = total/len(data)

    if avg>50:
        print("old users")
    else:
        print("young users")

    unused = math.pi

process()