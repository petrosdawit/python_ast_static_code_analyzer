class T1(object):

    def func(x,y):
        print(x)
        print(y)
        pass

class T2(object):
    
    def __init__(self):
        self.__x = 4
        self.__y = 4
    
    def hi(self,x,y,z):
        pass
    
    def hi(self,x,y,t):
        pass
    
    def hi(self,x):
        pass

def hi(x,y,z):
    pass
    
class T3(object):
    
    def __init__(self):
        self.__y = T5()
        self.__z = T4()
        
t = T()
print(t.__y)