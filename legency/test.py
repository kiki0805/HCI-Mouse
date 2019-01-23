x = 20


def func():
    global x
    x = 100
    print(str(x))  # 打印这个外部变量


if __name__ == '__main__':
    func()