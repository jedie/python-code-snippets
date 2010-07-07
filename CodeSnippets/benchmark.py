#!/usr/bin/env python
# coding: utf-8

"""
small system Benchmark by jensdiemer.de

used fak_test by Dookie alias Fritz Cizmarov

http://www.python-forum.de/viewtopic.php?t=3355
"""

__version__ = "0.0.1"

### History
# v0.0.1
#   - erste Version

import time
start_time = time.time()

import os, random, sys, operator


if sys.version_info[:2] < (2,2):
    raise SystemError("need at least Version 2.2 of Python")




rnd_mem_size    = 10000
rnd_mem_count   = 100

rnd_disk_size   = 1000
rnd_disk_count  = 1000

norm_disk_MBsize= 30
norm_disk_count = 1000

fak_num     = 100000





class benchmark:
    def __init__( self ):
        self.rnd_mem_test()

        self.rnd_disk_test()

        self.fak_test()

        print "="*80
        print "complete test duration:"
        print "%.2fsec" % (time.time() - start_time)
        print "="*80



    def print_process( self, i, total ):
        "allg. Fortschrittanzeige"
        i += 1
        tresh = total / 10
        if tresh == 0:
            tresh = 1
        if i % tresh == 0:
            duration = time.time() - start_time
            print "%3.i%% %4.i/%i  %.2fsec" % ( round(float(i)/total*100), i, total, duration)



    def rnd_mem_test( self ):
        print "Random-MEM Test"
        print "-"*80
        print "Creating %i random-Blocks with a Size of %iBytes" % ( rnd_mem_count, rnd_mem_size )

        for i in range( rnd_mem_count ):
            trash = [ chr( random.randint(0,255) ) for r in range(rnd_mem_size) ]
            self.print_process(i, rnd_mem_count)



    def rnd_disk_test( self ):
        print
        print "Random-DISK Test"

        try:
            testfile = file( "benchtest.tmp", "w" )
        except Exception, e:
            print "Can't create Testfile:",e
            sys.exit(1)

        print "-"*80
        KBsize = rnd_disk_count * rnd_disk_size / 1024
        print "Write %i random-Blocks à %iBytes (total %iKB)" % ( rnd_disk_count, rnd_disk_size, KBsize )

        for i in range( rnd_disk_count ):
            testfile.write(
                    "".join( [ chr( random.randint(0,255) ) for r in range(rnd_disk_size) ] )
                )
            self.print_process(i, rnd_disk_count)

        testfile.close()
        testfile = file( "benchtest.tmp", "w" )

        print "-"*80
        print "Test Disk writing speed"
        blockMBsize = norm_disk_MBsize * 1024
        MBytes = blockMBsize * norm_disk_count / 1024 / 1024
        print "Writes %iMBytes (NULL-Bytes)" % ( MBytes )
        NULLblock = " " * blockMBsize

        disk_start_time = time.time()
        for i in xrange( norm_disk_count ):
            testfile.write( NULLblock )
            self.print_process( i, norm_disk_count )
        disk_end_time = time.time()

        testfile.close()

        print "-"*80
        print "%iMB/sec" % ( MBytes / ( disk_end_time-disk_start_time ) )

        try:
            # lösche Inhalt des Tempfile
            testfile = file( "benchtest.tmp", "w" )
            testfile.close()
        except:
            pass

        try:
            # Lösche Datei selber
            os.remove( "benchtest.tmp" )
        except Exception, e:
            print "Can't delete Testfile:",e
            sys.exit(1)



    def fak_test( self ):
        print
        print "fak Test"
        print "-"*80

        def fak_recursive(n):
            if n > 2:
                return n * fak_recursive(n-1)
            else:
                return n

        def fak_iter_while(n):
            res = n
            while n > 2:
                n -= 1   # entspricht n = n - 1
                res *= n # ginge auch als res = res * n
            return res

        def fak_iter_for(n):
            res = n
            for n in xrange(2,n):
                res *= n
            return res

        fak_lambda = lambda n: reduce(operator.mul, xrange(2,n),n)

        def test(funktion_name, f):
            print "%16s: %d Berechnungen..." % (funktion_name, fak_num),
            values = range(1,101)*(fak_num/100)
            t_start = time.time()
            for val in values:
                tmp = f(val)
            print "%.2fsec" % (time.time() - start_time)


        test("fak_recursive", fak_recursive)

        test("fak_iter_while", fak_iter_while)

        test("fak_iter_for", fak_iter_for)

        test("fak_lambda", fak_lambda)


if __name__ == "__main__":
    benchmark()