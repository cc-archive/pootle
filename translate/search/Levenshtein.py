# -*- coding: utf-8 -*-
# 
# Copyright 2006 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""A class implementing to calculate a similarity based on the Levenshtein 
distance. See http://en.wikipedia.org/wiki/Levenshtein_distance."""

from translate.search import segment
import math

DEBUG = 0

class LevenshteinComparer:
    def __init__(self, max_len=200):
        self.MAX_LEN = max_len

    def similarity(self, a, b, stoppercentage=40):
        similarity = self.similarity_real(a, b, stoppercentage)
        measurements = 1
        if DEBUG:print similarity

        chr_a = segment.characters(a)
        chr_b = segment.characters(b)
        if abs(len(chr_a) - len(a)) + abs(len(chr_b) - len(b)):
            similarity += self.similarity_real(chr_a, chr_b, stoppercentage)
            measurements += 1
            if DEBUG:print self.similarity_real(chr_a, chr_b, stoppercentage)
        else:
            similarity *= 2
            measurements += 1
            
        wrd_a = segment.words(a)
        wrd_b = segment.words(b)
        if len(wrd_a) + len(wrd_b) > 2:
            similarity += self.similarity_real(wrd_a, wrd_b, 0)
            measurements += 1
            if DEBUG:print self.similarity_real(wrd_a, wrd_b, 0)
        return similarity / measurements

    def similarity_real(self, a, b, stoppercentage=40):
        """Returns the similarity between a and b based on Levenshtein distance. It
    can stop prematurely as soon as it sees that a and b will be no simmilar than
    the percentage specified in stoppercentage.

    The Levenshtein distance is calculated, but the following should be noted:
        * Only the first MAX_LEN characters are considered. Long strings differing
          at the end will therefore seem to match better than they should. See the
          use of the variable penalty to lessen the effect of this.
        * Strings with widely different lengths give the opportunity for shortcut.
          This is by definition of the Levenshtein distance: the distance will be 
          at least as much as the difference in string length.
        * Calculation is stopped as soon as a similarity of stoppercentage becomes
          unattainable. See the use of the variable stopvalue.
        * Implementation uses memory O(min(len(a), len(b))
        * Excecution time is O(len(a)*len(b))
    """
        #TODO: consider case sensitivity
        #TODO: consider word spacing, stripping \n, \r, \t
        #TODO: consider working by words instead of / in addition to characters
        #TODO: consider whitespace on edges
        l1, l2 = len(a), len(b)
        #Let's make l1 the smallest
        if l1 > l2:
            l1,l2 = l2,l1
            a, b = b, a
            
        #maxsimilarity is the maximum similarity that can be attained as constrained
        #by the difference in string length
        assert 0 <= stoppercentage <= 100
        maxsimilarity = 100 - 100.0*abs(l1 - l2)/l2
        if maxsimilarity < stoppercentage:
            return maxsimilarity * 1.0

        #Let's penalise the score in cases where we shorten strings
        penalty = 0
        if l2 > self.MAX_LEN:
            b = b[:self.MAX_LEN]
            l2 = len(b)
            penalty += 7
            if l1 > self.MAX_LEN:
                a = a[:self.MAX_LEN]
                l1 = len(a)
                penalty += 7
        
        #The actual value in the array that would represent a giveup situation:
        stopvalue = math.ceil((100.0 - stoppercentage)/100 * l2)
        dist = self.distance(a, b, stopvalue)
        if dist > stopvalue:
            return stoppercentage - 1.0
        
        #If MAX_LEN came into play, we consider the calculated distance to be 
        #representative of the distance between the whole, untrimmed strings
        if dist != 0:
            penalty = 0
        return 100 - (dist*1.0/l2)*100 - penalty

    def distance(self, a, b, stopvalue=0):
        """Calculates the distance for use in similarity calculation."""
        l1 = len(a)
        l2 = len(b)
        assert stopvalue <= l2
        if stopvalue == 0:
            stopvalue = l2
        current = range(l1+1)
        for i in range(1,l2+1):
            previous, current = current, [i]+[0]*l1
            for j in range(1, l1 + 1):
                change = previous[j-1]
                if a[j-1] != b[i-1]:
                    change = change + 1
                insert = previous[j] + 1
                delete = current[j-1] + 1
                current[j] = min(insert, delete, change)
            #The smallest value in the current array is the best (lowest) value
            #that can be attained in the end if the strings are identical further
            least = min(current)
            if least > stopvalue:
                return least
        
        return current[l1]

if __name__=="__main__":
    from sys import argv
    DEBUG = 1
    comparer = LevenshteinComparer()
    print "Similarity:\n%s" % comparer.similarity(argv[1],argv[2], 50)

