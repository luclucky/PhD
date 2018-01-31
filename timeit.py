def testtest(xxxx):
 
    ti = time.clock()
    
    for x in range(1111111):
        
        x = x+1
 
    ti = time.clock() - ti
    
    print(ti)
   
if __name__ == '__main__':
    
    import timeit
    import time
    
    for xxxx in range(10):
        
        t = timeit.Timer("testtest(xxxx)", setup="from __main__ import testtest, xxxx")
        
        repeat, number = 3, 1
        r = t.repeat(repeat, number) 
        best, worse = min(r), max(r)
        
        print("{number} loops, best of {repeat}: {best:.3g} seconds per loop, "  "worse of {repeat}: {worse:.3g} seconds per loop".format(**vars()))

        
        