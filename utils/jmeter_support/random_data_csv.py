#! /usr/bin/env python
'''
Created on Jul 27, 2011

@author: jklo
'''
import time
import random
import argparse
import csv
import sys

class RandomDateRangeGenerator():
    def __init__(self, start, end, gran="second"):
        
        if gran == "second":
            self.format = "%Y-%m-%dT%H:%M:%SZ"
        elif gran == "minute":
            self.format = "%Y-%m-%dT%H:%MZ"
        elif gran == "day":
            self.format = "%Y-%m-%d"
            
        self.stime = time.mktime(time.strptime(start, self.format))
        self.etime = time.mktime(time.strptime(end, self.format))
    
        
    def generate(self):
        rand1 = random.random()
        rand2 = random.random()

        t1 = self.stime + rand1 * (self.etime - self.stime)
        t2 = self.stime + rand2 * (self.etime - self.stime)

        def format(t):
            return time.strftime(self.format, time.localtime(t))
    
        if t1 < t2:
            return { "start": format(t1), "end": format(t2) }
        else:
            return { "start": format(t2), "end": format(t1) }
    

def getArgs():
        parser = argparse.ArgumentParser()
        parser.set_defaults(mode="date")

        subparsers = parser.add_subparsers(help="Supported Commands:")
        
        d_parser = subparsers.add_parser("date", help="Random Date Range Generator")
        d_parser.add_argument('start', help="ISO8601 Zulu formated start date")
        d_parser.add_argument('end', help="ISO8601 Zulu formated start date")
        d_parser.add_argument('-n', '--number', help="The number of ranges to generate", type=int, default=10, dest="number")
        d_parser.add_argument('-g', '--granularity', help="ISO8601 Zulu date granularity", choices=["second", "minute", "day"], dest="granularity", default="second")
        d_parser.set_defaults(mode="date")
        
        return parser.parse_args()

if __name__ == '__main__':
    args = getArgs()
    
    if args.mode == "date":
        gen = RandomDateRangeGenerator(args.start, args.end, args.granularity)
        writer = csv.writer(sys.stdout, dialect="excel")
        
        for i in range(0, args.number):
            rng = gen.generate()
            writer.writerow(rng.values())
#
#import random
#import time
#
#def strTimeProp(start, end, format, prop):
#    """Get a time at a proportion of a range of two formatted times.
#
#    start and end should be strings specifying times formated in the
#    given format (strftime-style), giving an interval [start, end].
#    prop specifies how a proportion of the interval to be taken after
#    start.  The returned time will be in the specified format.
#    """
#
#    stime = time.mktime(time.strptime(start, format))
#    etime = time.mktime(time.strptime(end, format))
#
#    ptime = stime + prop * (etime - stime)
#
#    return time.strftime(format, time.localtime(ptime))
#
#
#def randomDate(start, end, prop):
#    return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)
#
#print randomDate("1/1/2008 1:30 PM", "1/1/2009 4:50 AM", random.random())