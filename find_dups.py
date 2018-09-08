from __future__ import print_function
import os, sys

if sys.version_info[0] != 3 or sys.version_info[1] < 0:
    print('Your Python version is too old! Please use Python 3.0 or higher.')
    sys.exit(1)

import hashlib
import fnmatch
import configparser
import argparse
import platform

os.chdir(os.path.dirname(os.path.abspath(__file__)))

warnings = []
BULLET = '*     o  '
DEFAULT_FILTERMODE = 'NONE'
DEFAULT_FILTERFILE = ''
DEFAULT_SUBDIRS = 'TRUE'
DEFAULT_MAXFILESIZE = 0
DEFAULT_INCLUDEEMPTYFILES = 'FALSE'
DEFAULT_BLOCKSIZE = 65536
DEFAULT_HASHALGORITHM = 1
DEFAULT_CSV_FOLDER = os.getcwd()
DEFAULT_CSV = ''
MIN_BLOCKSIZE = 65536


def findDup(parentFolder, filters, scanOptions):
    # This does a quick scan to identify files of exactly the same size without having to read every files contents
    # This shorter 'preliminary list' is then passed for file hashing which is much slower. In this way, only likely candidates for duplicates are read

    sizeDups = {}
    hashDups = {}
    filterMode = scanOptions['FilterMode']
    numFiles = 0

    try:
        maxcol = os.get_terminal_size().columns - 2
    # piped output to file or other process
    except OSError:
        maxcol = sys.maxsize - 2

    for dirName, subdirs, fileList in os.walk(parentFolder):
        newDirName = True
        for fileName in fileList:
            numFiles = numFiles + 1

            if ((scanOptions['SubDirs'].upper()=='FALSE') and (dirName == parentFolder)) or (scanOptions['SubDirs'].upper()!='FALSE'):
                # Get the path to the file
                filterFound = False
                # Calculate size
                path = os.path.join(dirName, fileName)
                for filter_fn in filters:
                    if fnmatch.fnmatch(path, filter_fn):
                        filterFound=True
                if (not filterFound and filterMode.upper() == 'EXCLUDE') or (filterFound and filterMode.upper() == 'INCLUDE') or (filterMode.upper()=='NONE'):
                    if newDirName:
                        print(' ' * maxcol, end='\r')
                        print('Scanning ' + shortenName(dirName, maxcol - 9), end='\r')
                        newDirName = False
                    try:
                        fileSize = int(os.path.getsize(path))
                    except:
                        fileSize = -1
                else:
                    fileSize = -1
                # Add or append the file path
                if (fileSize != -1):
                    if ((fileSize == 0 and scanOptions['MaxFileSize'] == 0 and scanOptions['IncludeEmptyFiles'].upper() == 'TRUE')
                        or (fileSize == 0 and scanOptions['MaxFileSize'] > 0 and scanOptions['IncludeEmptyFiles'].upper() == 'TRUE')
                        or (fileSize > 0 and scanOptions['MaxFileSize'] == 0) 
                        or (fileSize > 0 and scanOptions['MaxFileSize'] > 0 and scanOptions['MaxFileSize'] >= fileSize)):
                    
                        if fileSize in sizeDups:
                            sizeDups[fileSize].append(path)
                        else:
                            sizeDups[fileSize] = [path]
    print (numFiles, 'file(s) in',parentFolder, 'scanned.')
    print ('Now checking potential duplicates...')
    hashDups = findDupsInDict(sizeDups, scanOptions['HashAlgorithm'], scanOptions['Blocksize'])
    return hashDups

def findDupsInDict(fileDict, hashAlgorithmVal, blocksize):
    dups = {}
    hashAlgorithms = {}
    hashAlgorithms = getHashAlgorithms(hashAlgorithmVal)
    results = list(filter(lambda x: len(x) > 1, fileDict.values()))

    if len(results) > 0:
        currResult = 0
        percentComplete = 0
        numResults = len(results)
        for result in results:
            currResult = currResult + 1
            for subresult in result:
                fileHash = hashfile(subresult, blocksize, hashAlgorithms)
                if fileHash in dups and fileHash != 0:
                    dups[fileHash].append(subresult)
                elif not(fileHash in dups) and fileHash != 0:
                    dups[fileHash] = [subresult]
            print(' ' * 100, end='\r')
            print ('Checking potential duplicate set', currResult, 'of', numResults, end='\r')
            percentComplete = int(round(currResult / numResults,0))
    print('')
    return dups

# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
 
def getHashAlgorithms(algorithm_val):
    hashAlgorithms = {}
    valSHA512 = 32
    valSHA384 = 16
    valSHA256 = 8
    valSHA224 = 4
    valSHA1 = 2
    valMD5 = 1
    if not str(algorithm_val).isnumeric():
        algorithm_val = valMD5

    hashAlgorithms['useSHA512'] = False
    hashAlgorithms['useSHA384'] = False
    hashAlgorithms['useSHA256'] = False
    hashAlgorithms['useSHA224'] = False
    hashAlgorithms['useSHA1'] = False
    hashAlgorithms['useMD5'] = False

    if (algorithm_val <= 0) or (algorithm_val >= 64):
        algorithm_val = 1
    if algorithm_val >= valSHA512:
        hashAlgorithms['useSHA512'] = True
        algorithm_val = algorithm_val - valSHA512
    if algorithm_val >= valSHA384:
        hashAlgorithms['useSHA384'] = True
        algorithm_val = algorithm_val - valSHA384
    if algorithm_val >= valSHA256:
        hashAlgorithms['useSHA256'] = True
        algorithm_val = algorithm_val - valSHA256
    if algorithm_val >= valSHA224:
        hashAlgorithms['useSHA224'] = True
        algorithm_val = algorithm_val - valSHA224
    if algorithm_val >= valSHA1:
        hashAlgorithms['useSHA1'] = True
        algorithm_val = algorithm_val - valSHA1
    if algorithm_val >= valMD5:
        hashAlgorithms['useMD5'] = True
    return hashAlgorithms
 
def hashfile(path, blocksize, hashAlgorithms):
    compositeHash = ''

    if int(blocksize) <= MIN_BLOCKSIZE:
        blocksize = DEFAULT_BLOCKSIZE
    try:
        afile = open(path, 'rb')
        if hashAlgorithms['useMD5']: hasherMD5 = hashlib.md5()
        if hashAlgorithms['useSHA1']: hasherSHA1 = hashlib.sha1()
        if hashAlgorithms['useSHA224']: hasherSHA224 = hashlib.sha224()
        if hashAlgorithms['useSHA256']: hasherSHA256 = hashlib.sha256()
        if hashAlgorithms['useSHA384']: hasherSHA384 = hashlib.sha384()
        if hashAlgorithms['useSHA512']: hasherSHA512 = hashlib.sha512()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            if hashAlgorithms['useMD5']: hasherMD5.update(buf)
            if hashAlgorithms['useSHA1']: hasherSHA1.update(buf)
            if hashAlgorithms['useSHA224']: hasherSHA224.update(buf)
            if hashAlgorithms['useSHA256']: hasherSHA256.update(buf)
            if hashAlgorithms['useSHA384']: hasherSHA384.update(buf)
            if hashAlgorithms['useSHA512']: hasherSHA512.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        if hashAlgorithms['useMD5']: compositeHash = compositeHash + hasherMD5.hexdigest()
        if hashAlgorithms['useSHA1']: compositeHash = compositeHash + hasherSHA1.hexdigest()
        if hashAlgorithms['useSHA224']: compositeHash = compositeHash + hasherSHA224.hexdigest()
        if hashAlgorithms['useSHA256']: compositeHash = compositeHash + hasherSHA256.hexdigest()
        if hashAlgorithms['useSHA384']: compositeHash = compositeHash + hasherSHA384.hexdigest()
        if hashAlgorithms['useSHA512']: compositeHash = compositeHash + hasherSHA512.hexdigest()
        return compositeHash
    except:
        warnings.append('WARNING: Could not calculate the hash of ' + path)
        return 0
 
 
def printResults(dict1, csvOutput):
    if (not os.path.exists(os.path.dirname(csvOutput)) and csvOutput != ''):
        if os.path.dirname(csvOutput) == '':
            newCsvOutput = os.path.join(DEFAULT_CSV_FOLDER, csvOutput)
        else:
            newCsvOutput = csvOutput.replace(os.path.dirname(csvOutput), DEFAULT_CSV_FOLDER)
            warnings.append('WARNING: The folder name "' + os.path.dirname(csvOutput)
                    + '" for the CSV output file does not exist. '
                    + 'Results will be saved in ' + newCsvOutput + ' instead.')
        csvOutput = newCsvOutput
        
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    print('')
    print('************************************************************')
    if len(results) > 0:
        if csvOutput !='': f = open(csvOutput, 'w+')
        print('*  RESULTS: DUPLICATES FOUND:')
        if csvOutput !='': f.write('DUPLICATES FOUND:\nFile Name,File Size (bytes)')
        print('*  ---------------------------------------------------------')
        for result in results:
            if csvOutput !='': f.write('\n')
            for subresult in result:
                print('*  \t' + subresult)
                if csvOutput !='': f.write(subresult + ',' + str(os.path.getsize(subresult)) + '\n')
            print('*  ---------------------------------------------------------\n*')
        if csvOutput !='': f.close()
 
    else:
        print('*  RESULTS: NO DUPLICATE FILES FOUND')
    print('************************************************************')

def loadDefaultScanOptions():
    #These values will be used if they are not set through config file or command line parameters
    scanOptions = {}
    scanOptions['FilterMode'] = DEFAULT_FILTERMODE
    scanOptions['FilterFile'] = DEFAULT_FILTERFILE
    scanOptions['SubDirs'] = DEFAULT_SUBDIRS
    scanOptions['MaxFileSize'] = DEFAULT_MAXFILESIZE
    scanOptions['IncludeEmptyFiles'] = DEFAULT_INCLUDEEMPTYFILES
    scanOptions['Blocksize'] = DEFAULT_BLOCKSIZE
    scanOptions['HashAlgorithm'] = DEFAULT_HASHALGORITHM
    scanOptions['CSVOutput'] = DEFAULT_CSV
    return scanOptions

def loadConfigFileScanOptions(configFile):
    #These values will override the defaults if they are set
    scanOptions = {}
    scanOptions = loadDefaultScanOptions()
    if os.path.exists(configFile):
        config = configparser.ConfigParser()
        with open(configFile) as cf:
                config.read_file(cf)
        if config.has_option('General', 'FilterMode') and (config.get('General', 'FilterMode').upper() == 'NONE' or config.get('General', 'FilterMode').upper() == 'INCLUDE') or config.get('General', 'filterMode').upper() == 'EXCLUDE':
            scanOptions['FilterMode'] = config.get('General', 'FilterMode').upper()
        if (scanOptions['FilterMode'].upper() != 'NONE') and (os.path.exists(config.get('General', 'FilterFile'))):
            scanOptions['FilterFile'] = config.get('General', 'FilterFile')
        if config.has_option('Scan Options', 'SubDirs') and (config.get('Scan Options', 'SubDirs').upper() == 'TRUE' or config.get('Scan Options', 'SubDirs').upper() == 'FALSE'):
            scanOptions['SubDirs'] = config.get('Scan Options', 'SubDirs').upper()
        if config.has_option('Scan Options', 'MaxFileSize') and (config.get('Scan Options', 'MaxFileSize').isnumeric()):
            scanOptions['MaxFileSize'] = int(config.get('Scan Options', 'MaxFileSize'))
        if config.has_option('Scan Options', 'IncludeEmptyFiles') and (config.get('Scan Options', 'IncludeEmptyFiles').upper() == 'TRUE' or config.get('Scan Options', 'IncludeEmptyFiles').upper == 'FALSE'):
            scanOptions['IncludeEmptyFiles'] = config.get('Scan Options', 'IncludeEmptyFiles').upper()
        if config.has_option('Advanced', 'Blocksize') and (config.get('Advanced', 'Blocksize').isnumeric()):
            scanOptions['Blocksize'] = abs(int(config.get('Advanced', 'Blocksize')))
            if scanOptions['Blocksize'] <= MIN_BLOCKSIZE: scanOptions['Blocksize'] = MIN_BLOCKSIZE
        if config.has_option('Advanced', 'HashAlgorithm') and (config.get('Advanced', 'HashAlgorithm').isnumeric()):
            scanOptions['HashAlgorithm'] = int(config.get('Advanced', 'HashAlgorithm'))
        if config.has_option('Scan Options', 'CSVOutput'):
            scanOptions['CSVOutput'] = str(config.get('Scan Options', 'CSVOutput'))
    return scanOptions

def loadFilters(filterFile):
    if os.path.exists(filterFile):    
        with open(filterFile) as f:
            filters = f.read().splitlines()
    else:
        filters = []
    return filters

def printHashAlgorithms(hashAlgorithms):
    print('*  USING ALGORITHMS:')
    print('*  -----------------')
    if hashAlgorithms['useMD5']: print(BULLET + 'MD5')
    if hashAlgorithms['useSHA1']: print(BULLET + 'SHA1')
    if hashAlgorithms['useSHA224']: print(BULLET + 'SHA224')
    if hashAlgorithms['useSHA256']: print(BULLET + 'SHA256')
    if hashAlgorithms['useSHA384']: print(BULLET + 'SHA384')
    if hashAlgorithms['useSHA512']: print(BULLET + 'SHA512')
 
def loadCommandLineScanOptions(args, scanOptions):
    if args['filterMode'] != None and (args['filterMode'].upper()=='INCLUDE' or args['filterMode'].upper()=='EXCLUDE' or args['filterMode'].upper()=='NONE'):
        scanOptions['FilterMode'] = args['filterMode'].upper()
    if args['filterFile'] != None:
        if os.path.exists(args['filterFile']):
            scanOptions['FilterFile'] = args['filterFile']
    if args['subDirs'] != None and (args['subDirs'].upper()=='TRUE' or args['subDirs'].upper()=='FALSE'):
        scanOptions['SubDirs'] = args['subDirs'].upper()
    if args['maxFileSize'] != None:
        scanOptions['MaxFileSize'] = int(abs(args['maxFileSize']))
    if (args['includeEmptyFiles'] != None) and ((args['includeEmptyFiles'].upper()=='TRUE') or args['includeEmptyFiles'].upper()=='FALSE'):
        scanOptions['IncludeEmptyFiles'] = args['includeEmptyFiles'].upper()
    if args['blocksize'] != None and abs(args['blocksize']) >= MIN_BLOCKSIZE:
        scanOptions['Blocksize'] = int(abs(args['blocksize']))
    if args['hashAlgorithm'] != None:
        scanOptions['HashAlgorithm'] = int(args['hashAlgorithm'])
    if args['csvOutput'] != None:
        scanOptions['CSVOutput'] = args['csvOutput']
    return scanOptions

def shortenName(stringToShorten, lengthToShorten):
    if stringToShorten == None: return ''
    if lengthToShorten == None: return stringToShorten
    if lengthToShorten < 5: lengthToShorten = 5
 
    if len(stringToShorten) <= lengthToShorten:
        shortenedString = stringToShorten
    else:
        splitSize = int(round((lengthToShorten-3) / 2,0))
        shortenedString = stringToShorten[:splitSize] + '...' + stringToShorten[-splitSize:]

    return shortenedString

def padSpaces(stringToPad, lengthToPad):
    stringToPad = str(stringToPad)
    while len(stringToPad) < lengthToPad:
        stringToPad = stringToPad + ' '
    return stringToPad

def printSettings(folders, scanOptions, filters):
    print('')
    print('************************************************************')
    printHashAlgorithms(getHashAlgorithms(scanOptions['HashAlgorithm']))
    print('*  \n*  FOLDER(S) TO SCAN:')
    print('*  ------------------')
    for x in folders: print(BULLET + str(x)) 
    print('*  \n*  SCAN OPTIONS USED:')
    print('*  ------------------')
    for x in scanOptions: print(BULLET + padSpaces(str(x),20) + ': ' + str(scanOptions[x]))
    if len(filters) > 0:
        print('*  FILTERS: ')
        print('*  --------')
        for x in filters: print(BULLET + str(x)) 
    print('*\n************************************************************')
    print ('')

def printWarnings(warnings):
    if len(warnings) > 0:
        print('')
        print('************************************************************')
        print('*  WARNINGS:')
        for x in range(len(warnings)): print (BULLET + ' ' + warnings[x])
        print('************************************************************')
        print('')

def getConfigurations(cmdArgs):
    #First load the default scan options
    scanOptions = {}
    scanOptions = loadDefaultScanOptions()

    #Then over-write these default scan options with any values supplied in a configuration file
    config = configparser.ConfigParser()
    scanOptions['ConfigFile']=''
    if cmdArgs['configFile'] != None: scanOptions['ConfigFile'] = cmdArgs['configFile']
    configFile = scanOptions['ConfigFile']
    if os.path.exists(configFile): scanOptions = loadConfigFileScanOptions(configFile)

    #Finally over-write these scan options with any explicitly supplied in the command line itself
    loadCommandLineScanOptions(cmdArgs, scanOptions)
    return scanOptions

def getFilters(filterFile, cmdFilters):
    #If a filter has been set in the commandline, use that. Otherwise try to get it from the config file
    if filterFile != None and filterFile != '' and cmdFilters != None:
        warnings.append('INFO: Supplied --filters command line parameter will take precedence over supplied --filterMode parameter or config file settings')
    if cmdFilters != None and cmdFilters != '':
        filters = cmdFilters
    elif filterFile != None and filterFile != '':
        filters = loadFilters(filterFile)
    else:
        filters = []
    return filters

def getDupsInFolders(folders):
    #Iterate through each supplied folder name and start scanning for duplicates
    for i in folders:
        if i[-1] == ':' and platform.system() == 'Windows': i = i + '\\'
        if os.path.exists(i):
            # Find the duplicated files and append them to the dups
            joinDicts(dups, findDup(i, filters, scanOptions))
        else:
            warnings.append('WARNING: ' + str(i) + ' is not a valid path, please verify')    
    return dups

if __name__ == '__main__':
    dups = {}

    #Read the command line parameters
    parser = argparse.ArgumentParser(description='Search for duplicate files in one or more folders')
    parser.add_argument('-cfg', '--configFile', help='Configuration File for script', required=False)
    parser.add_argument('-fm', '--filterMode', help='Filter Mode', choices=['INCLUDE', 'EXCLUDE', 'NONE'], required=False)
    parser.add_argument('-ff', '--filterFile', help='File containing list of filters to be applied if Filter Mode is not NONE', required=False)
    parser.add_argument('-f', '--filters', nargs='+', help = 'List of filters', required=False)
    parser.add_argument('-s', '--subDirs', help='Scan subdirectories of selected folders?', choices=['TRUE', 'FALSE'], required=False)
    parser.add_argument('-ms', '--maxFileSize', type=int, help='Maximum size of files to be scanned', required=False)
    parser.add_argument('-emp', '--includeEmptyFiles', help='Include files with no content in results?', choices=['TRUE', 'FALSE'], required=False)
    parser.add_argument('-bs', '--blocksize', type=int, help='Blocksize for file reads', required=False)
    parser.add_argument('-ha', '--hashAlgorithm', type=int, help='Algorithm(s) to be used for file hashing', required=False)
    parser.add_argument('-csv', '--csvOutput', help='Path to output results in CSV format', required=False)
    parser.add_argument('-dirs', '--directories', nargs='+', help = 'List of directories to scan', required=True)
    args = vars(parser.parse_args())

    #Construct the set of scan options from command line parameters (1st precedence), configuration file settings (2nd precedence), and default values (fallback)
    scanOptions = getConfigurations(args)

    #Get the filter list to be used, if any
    filters = getFilters(scanOptions['FilterFile'], args['filters'])
    
    #Get list of directories to be scanned (currently can only be a command line parameter)
    folders = args['directories']
    
    #Print the list of settings to the console
    printSettings(folders, scanOptions, filters)

    #Find all the duplicates
    dups = getDupsInFolders(folders)

    #Print the results to the console and any output file specified
    printResults(dups, scanOptions['CSVOutput'])

    #Print any errors / warnings and the duplicates found to the consoles
    printWarnings(warnings)
