def testtest(xxxx):
 
    print('run ' + str(xxxx))
   
if __name__ == '__main__':
    
    import timeit
    
    for xxxx in range(10):
        
        t = timeit.Timer("testtest(xxxx)", setup="from __main__ import testtest, xxxx")
        
        repeat, number = 3, 1
        r = t.repeat(repeat, number) 
        best, worse = min(r), max(r)
        
        print("{number} loops, best of {repeat}: {best:.3g} seconds per loop, "  "worse of {repeat}: {worse:.3g} seconds per loop".format(**vars()))

        
        