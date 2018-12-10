import matplotlib.pyplot as plt
 
name_list = ['0.2', '0.4','0.6','0.8','1.0']
# R
num_list = [0, 0, 0, 46, 54, 54, 54, 55, 55, 56, 57, 57, 60, 71, 73, 82, 89, 96, 96, 101, 105, 108, 111, 114, 114, 114, 114, 114] # 0.2
num_list1 = [0, 0, 0, 33, 52, 54, 54, 55, 55, 56, 57, 57, 60, 70, 73, 82, 91, 96, 96, 100, 104, 109, 111, 113, 114, 114, 114, 114] # 0.4
num_list2 = [0, 0, 0, 26, 41, 45, 53, 55, 55, 56, 57, 57, 60, 71, 73, 82, 90, 96, 96, 101, 103, 109, 111, 112, 114, 114, 114, 114] # 0.6
num_list3 = [0, 0, 0, 18, 32, 37, 42, 45, 47, 54, 56, 57, 60, 69, 74, 82, 89, 96, 96, 100, 102, 108, 112, 113, 114, 114, 114, 114] # 0.8
num_list4 = [0, 0, 0, 11, 23, 31, 36, 39, 40, 42, 46, 49, 52, 59, 69, 79, 88, 95, 96, 100, 102, 108, 111, 113, 114, 114, 114, 114] # 1.0
# G
# num_list = [0, 0, 0, 45, 54, 54, 54, 55, 55, 56, 57, 57, 62, 70, 73, 82, 91, 95, 96, 100, 102, 110, 111, 113, 114, 114, 114, 114] # 0.2
# num_list1 = [0, 0, 0, 18, 48, 54, 54, 55, 55, 55, 57, 57, 61, 69, 73, 82, 89, 95, 96, 101, 103, 107, 111, 113, 114, 114, 114, 114] # 0.4
# num_list2 = [0, 0, 0, 11, 19, 33, 48, 54, 55, 55, 57, 57, 59, 71, 73, 81, 89, 96, 96, 100, 103, 108, 111, 113, 114, 114, 114, 114] # 0.6
# num_list3 = [0, 0, 0, 5, 11, 15, 23, 29, 39, 45, 50, 56, 59, 70, 73, 81, 88, 96, 96, 100, 102, 108, 110, 113, 114, 114, 114, 114] # 0.8
# num_list4 = [0, 0, 0, 0, 10, 11, 15, 18, 23, 25, 31, 36, 43, 55, 64, 74, 84, 95, 96, 98, 101, 106, 111, 112, 114, 114, 114, 114] # 1.0
# B
# num_list = [0, 0, 0, 47, 53, 54, 54, 55, 55, 56, 57, 57, 61, 70, 74, 83, 91, 95, 96, 101, 103, 108, 111, 113, 114, 114, 114, 114] # 0.2
# num_list1 = [0, 0, 0, 45, 50, 54, 54, 55, 55, 56, 57, 58, 65, 72, 81, 88, 96, 96, 100, 103, 109, 111, 113, 114, 114, 114, 114, 114] # 0.4
# num_list2 = [0, 0, 0, 22, 47, 51, 54, 54, 55, 55, 56, 58, 64, 71, 79, 88, 95, 96, 100, 101, 108, 111, 113, 114, 114, 114, 114, 114] # 0.6
# num_list3 = [0, 0, 0, 6, 25, 41, 49, 52, 54, 55, 55, 59, 64, 68, 75, 86, 94, 96, 98, 101, 109, 111, 113, 113, 114, 114, 114, 114] # 0.8
# num_list4 = [0, 0, 0, 1, 12, 20, 30, 41, 48, 51, 53, 58, 64, 71, 79, 92, 94, 98, 100, 106, 110, 113, 113, 114, 114, 114, 114, 114] # 1.0

x = [112.5, 117.5, 122.5, 127.5, 132.5, 137.5, 142.5, 147.5, 152.5, 157.5, 162.5, 167.5, 172.5, 177.5, 182.5, 187.5, 192.5, 197.5, 202.5, 207.5, 212.5, 217.5, 222.5, 227.5, 232.5, 237.5, 242.5, 247.5]



total_width, n = 3, 5
width = total_width / n
 
plt.bar(x, num_list, width=width, label='0.2',color=(0.2,0,0))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list1, width=width, label='0.4',color=(0.4,0,0))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list2, width=width, label='0.6',color=(0.6,0,0))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list3, width=width, label='0.8',color=(0.8,0,0))
for i in range(len(x)):
    x[i] = x[i] + width
plt.bar(x, num_list4, width=width, label='1.0',color=(1.0,0,0))

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

# plt.bar(x, num_list, width=width, label='0.2',color=(0,0,0.2))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list1, width=width, label='0.4',color=(0,0,0.4))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list2, width=width, label='0.6',color=(0,0,0.6))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list3, width=width, label='0.8',color=(0,0,0.8))
# for i in range(len(x)):
#     x[i] = x[i] + width
# plt.bar(x, num_list4, width=width, label='1.0',color=(0,0,1.0))

plt.legend()
plt.show()

