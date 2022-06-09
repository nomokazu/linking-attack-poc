import matplotlib.pyplot as plt
import pickle


plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams["font.size"] = 30

experimentNumber = int(input("Experiment Number : "))
number = int(input("Pickle Number : "))
filename = open('./' + str(experimentNumber) +  '/myPickle/'+str(number)+'.pickle', 'rb')
fig = pickle.load(filename)

plt.show()