import matplotlib.pyplot as plt
 
name_list = ['0.2', '0.4','0.6','0.8','1.0']
# R
# num_list = [0, 0, 0, 45, 9, 0, 0, 1, 0, 0, 2, 0, 3, 11, 2, 10, 7, 6, 0, 5, 2, 5, 3, 1, 2, 0, 0, 0] # 0.2
# num_list1 = [0, 0, 0, 34, 19, 1, 0, 1, 0, 0, 2, 0, 3, 8, 3, 8, 8, 3, 2, 8, 3, 5, 3, 2, 1, 0, 0, 0] # 0.4
# num_list2 = [0, 0, 0, 24, 15, 4, 9, 3, 0, 0, 2, 0, 3, 7, 6, 6, 6, 5, 2, 8, 2, 5, 4, 2, 1, 0, 0, 0] # 0.6
# num_list3 = [0, 0, 0, 15, 14, 8, 2, 3, 6, 4, 4, 1, 2, 6, 6, 8, 6, 3, 4, 5, 6, 4, 4, 2, 1, 0, 0, 0] # 0.8
# num_list4 = [0, 0, 0, 10, 13, 7, 6, 1, 1, 3, 1, 5, 5, 8, 9, 9, 5, 5, 4, 4, 7, 4, 3, 2, 2, 0, 0, 0] # 1.0
# G
# num_list = [0, 0, 0, 44, 10, 0, 0, 1, 0, 0, 2, 0, 3, 8, 3, 8, 9, 4, 0, 6, 6, 3, 4, 2, 1, 0, 0, 0] # 0.2
# num_list1 = [0, 0, 0, 19, 25, 10, 0, 1, 0, 0, 2, 0, 1, 10, 4, 7, 9, 1, 4, 7, 3, 4, 4, 2, 1, 0, 0, 0] # 0.4
# num_list2 = [0, 0, 0, 11, 6, 14, 14, 9, 1, 0, 2, 0, 3, 7, 4, 8, 7, 3, 3, 6, 5, 4, 4, 2, 1, 0, 0, 0] # 0.6
# num_list3 = [0, 0, 0, 3, 9, 2, 7, 6, 11, 7, 5, 7, 2, 8, 4, 7, 5, 7, 2, 5, 5, 5, 4, 2, 1, 0, 0, 0] # 0.8
# num_list4 = [0, 0, 0, 1, 7, 4, 2, 3, 5, 2, 5, 5, 10, 9, 9, 8, 11, 8, 3, 3, 6, 6, 4, 2, 1, 0, 0, 0] # 1.0
# B
num_list = [0, 0, 0, 47, 7, 0, 0, 1, 0, 0, 2, 0, 1, 11, 2, 9, 6, 4, 3, 5, 4, 5, 4, 2, 1, 0, 0, 0] # 0.2
num_list1 = [0, 0, 0, 41, 10, 3, 0, 0, 1, 0, 1, 1, 3, 5, 6, 8, 9, 2, 2, 7, 3, 6, 3, 2, 1, 0, 0, 0] # 0.4
num_list2 = [0, 0, 0, 14, 30, 7, 2, 1, 1, 0, 0, 1, 4, 5, 4, 10, 8, 2, 3, 5, 5, 5, 4, 2, 1, 0, 0, 0] # 0.6
num_list3 = [0, 0, 0, 5, 18, 20, 7, 3, 1, 1, 0, 1, 6, 3, 9, 10, 5, 2, 6, 4, 6, 4, 2, 0, 1, 0, 0, 0] # 0.8
num_list4 = [0, 0, 0, 1, 11, 7, 11, 10, 8, 3, 2, 5, 4, 6, 11, 6, 3, 9, 3, 4, 7, 1, 1, 1, 0, 0, 0, 0] # 1.0
x = [112.5, 117.5, 122.5, 127.5, 132.5, 137.5, 142.5, 147.5, 152.5, 157.5, 162.5, 167.5, 172.5, 177.5, 182.5, 187.5, 192.5, 197.5, 202.5, 207.5, 212.5, 217.5, 222.5, 227.5, 232.5, 237.5, 242.5, 247.5]



total_width, n = 3, 5
width = total_width / n
 
# plt.bar(x, num_list, width=width, label='0.2',color=(0.2,0,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list1, width=width, label='0.4',color=(0.4,0,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list2, width=width, label='0.6',color=(0.6,0,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list3, width=width, label='0.8',color=(0.8,0,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list4, width=width, label='1.0',color=(1.0,0,0))

# plt.bar(x, num_list, width=width, label='0.2',color=(0,0.2,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list1, width=width, label='0.4',color=(0,0.4,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list2, width=width, label='0.6',color=(0,0.6,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list3, width=width, label='0.8',color=(0,0.8,0))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list4, width=width, label='1.0',color=(0,1.0,0))

plt.bar(x, num_list, width=width, label='0.2',color=(0,0,0.2))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list1, width=width, label='0.4',color=(0,0,0.4))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list2, width=width, label='0.6',color=(0,0,0.6))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list3, width=width, label='0.8',color=(0,0,0.8))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list4, width=width, label='1.0',color=(0,0,1.0))

plt.legend()
plt.show()

