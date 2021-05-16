#!/usr/local/bin/python3

# MIT License
#
# Copyright (c) 2021 Eudean Sun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This program takes as input a 1099-B from Robinhood converted from
# PDF to text using:
#
# pdftotext -table 1099.pdf 1099.txt
#
# As output it will generate:
# 1. Proceeds from covered short-term non-wash sale transactions (8949 type A)
# 2. Cost basis from covered short-term non-wash sale transactions (8949 type A)
# 3. Proceeds from covered long-term non-wash sale transactions (8949 type D)
# 4. Cost basis from covered long-term non-wash sale transactions (8949 type D)
# 5. txf file of covered short-term wash sale transactions (8949 type A)
# 6. txf file of covered long-term wash sale transactions (8949 type D)
#
# If no wash sales are detected, the txf files will not be generated.
#
# Items 1-4 can be entered as summarized transactions.
# Items 5-6 can be imported into tax software accepting txf files.
#
# This does not support any other types of transactions except those
# mentioned above and will likely produce erroneous result if used on
# a 1099-B containing other types of transactions.

import os
import re
import sys

if len(sys.argv) != 2:
    print('Usage: ./process1099.py <filename>')
    sys.exit(1)

input_file = sys.argv[1]
wash = {}
wash['short'] = []
wash['long'] = []
regular_proceeds = {}
regular_proceeds['short'] = 0
regular_proceeds['long'] = 0
regular_cost = {}
regular_cost['short'] = 0
regular_cost['long'] = 0
symbol = None
key = None
with open(input_file) as f:
    for line in f:
        line = line.strip().replace(',', '')
        split = line.split()
        if 'SHORT TERM TRANSACTIONS FOR COVERED TAX LOTS' in line:
            key = 'short'
        elif 'LONG TERM TRANSACTIONS FOR COVERED TAX LOTS' in line:
            key = 'long'
        elif 'Symbol:' in line:
            assert key
            symbol = split[0]
        elif re.match('[0-9]{2}/[0-9]{2}/[0-9]{2}', line):
            assert symbol
            if re.search('[0-9]+\.[0-9]+ +W', line):
                wash[key].append([symbol] + split)
            else:
                regular_proceeds[key] += float(split[2])
                regular_cost[key] += float(split[4])
        elif ('Detail for Dividends and Distributions' in line or
              'Fees and Expenses' in line):
            break

print('Short-term non-wash proceeds: {:.2f}'.format(regular_proceeds['short']))
print('Short-term non-wash cost basis: {:.2f}'.format(regular_cost['short']))
print('Long-term non-wash proceeds: {:.2f}'.format(regular_proceeds['long']))
print('Long-term non-wash cost basis: {:.2f}'.format(regular_cost['long']))

code = {}
code['short'] = 'N321'
code['long'] = 'N323'
for key in wash:
    if wash[key]:
        with open(os.path.splitext(input_file)[0] + '_' + key + '_wash.txf', 'w') as f:
            print('V042', file=f)
            print('^', file=f)
            for sale in wash[key]:
                print('TD', file=f)
                print(code[key], file=f)
                print('C1', file=f)
                print('L1', file=f)
                (symbol, date_sold, quantity, proceeds, date_acquired, cost, wash_amount ) = sale[:7]
                quantity = float(quantity)
                if quantity.is_integer():
                    quantity = '{:.0f}'.format(quantity)
                else:
                    quantity = '{:.02f}'.format(quantity)
                print('P{} {}'.format(quantity, symbol), file=f)
                print('D{}'.format(date_acquired), file=f)
                print('D{}'.format(date_sold), file=f)
                print('$' + cost, file=f)
                print('$' + proceeds, file=f)
                print('$' + wash_amount, file=f)
                print('^', file=f)
