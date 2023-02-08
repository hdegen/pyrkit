from __future__ import print_function
import pandas as pd
import sys


usage = '''\
USAGE:
    python xlsx_reader.py input.xlsx output_file_prefix [-h]
Positional Arguments:
    [1]       Type [File]: Input XLSX filename to convert to TSV. Note: XLSX files with multiple worksheets are separated into multiple TSV files. 
    [2]       Type [String]: Prefix of output filename. Note: An additional suffix containing the worksheet name will also be appended.   
Example: Note 'huPlasma_36-plex.xlsx' contains two worksheets: Results and QC
    $ python xlsx_reader.py huPlasma_36-plex.xlsx test
    
    # Returns TSV file for each worksheet
    > test_Results.txt
    > test_QC.txt
Requirements:
   pandas
'''


def write(inputfile, outprefix):
        '''Takes input XLSX filename and output file prefix to create multiple TSV files for each worksheet in the XSLX file.'''
        sheet2df = pd.read_excel(inputfile, sheet_name=None, header=None)

        print('Found Worksheets:')
        for sheet, data in sheet2df.items():
                print(" - {}".format(sheet))
                outfile =  sheet2df[sheet]
                outfile.to_csv("{}_{}.txt".format(outprefix, sheet.replace(' ','-')),sep='\t',encoding='utf-8', header=None, index=False)


def main():

        # Parse args
        if '-h' in sys.argv or '--help' in sys.argv:
                print(usage)
                sys.exit()
        try:    
                filename = sys.argv[1]  # Input xlsx file
                ofn = sys.argv[2]       # Output filename prefix 
        except IndexError:
                print(usage)
                sys.exit()

        write(filename, ofn)

if __name__ == '__main__':
        main()
