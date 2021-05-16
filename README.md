# robinhood-1099

This program takes as input a 1099-B from Robinhood converted from
PDF to text using:

pdftotext -table 1099.pdf 1099.txt

As output it will generate:
1. Proceeds from covered short-term non-wash sale transactions (8949 type A)
2. Cost basis from covered short-term non-wash sale transactions (8949 type A)
3. Proceeds from covered long-term non-wash sale transactions (8949 type D)
4. Cost basis from covered long-term non-wash sale transactions (8949 type D)
5. txf file of covered short-term wash sale transactions (8949 type A)
6. txf file of covered long-term wash sale transactions (8949 type D)

If no wash sales are detected, the txf files will not be generated.

Items 1-4 can be entered as summarized transactions.
Items 5-6 can be imported into tax software accepting txf files.

This does not support any other types of transactions except those
mentioned above and will likely produce erroneous results if used on
a 1099-B containing other types of transactions.
