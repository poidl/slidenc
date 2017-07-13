import matplotlib.pyplot as plt

def mypl(va):
    plt.imshow(va,interpolation='none')
    plt.colorbar()
    plt.show()
