class T:
    def test_while_if(self, x,y,z):
        if x < y:
            return 2
    def test_while_if_2(self, w,x,y,z):
        while x < y and z < y:
            return 2
    def test_while_if_3(self, w,x,y,z):
        if x:
            return 2   
    def test_return(self, x,y,z):
        return x
    def test_return_1(self,x,y,z):
        return x+y
    def test_for_1(self,x,y,z):
        for i in range(x):
            print(i)
    def test_for_2(self,x,y,z):
        for i in x:
            print(i)
    def test_value_1(self,x,y,z):
        x = 2
        y = 2
    def test_value_2(self,x,y,z):
        x = z[y]
    def test_value_3(self,x,y,z):
        t = x[y:z]
    def test_function_1(self,x,y,z):
        return test_while_if(x,y,z)
        