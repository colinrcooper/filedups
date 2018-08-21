import os, sys
import hashlib
import fnmatch
import configparser
import argparse
 
def findDup(parentFolder, filterMode, filters, scanOptions):
    # Dups in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        newDirName = True
        for fileName in fileList:
            path = os.path.join(dirName, fileName)
            if scanOptions['MaxFileSize'] > 0 or scanOptions['IncludeEmptyFiles']=='FALSE':
                try:
                    fileSize = int(os.path.getsize(path))
                except:
                    fileSize = 0
            else:
                fileSize = 0
            if ((scanOptions['SubDirs'].upper()=='FALSE') and (dirName == parentFolder)) or (scanOptions['SubDirs'].upper()!='FALSE'):
                # Get the path to the file
                filterFound = False
                for filter_fn in filters:
                    if fnmatch.fnmatch(path, filter_fn):
                        filterFound=True
                if (not filterFound and filterMode.upper() == 'EXCLUDE') or (filterFound and filterMode.upper() == 'INCLUDE'):
                    if newDirName:
                        #print('Scanning %s' % dirName)
                        newDirName = False
                    if scanOptions['MaxFileSize'] > fileSize or scanOptions['MaxFileSize'] == 0:
                        # Calculate hash
                        fileHash = hashfile(path, scanOptions['Blocksize'], scanOptions['HashAlgorithm'])
                    else:
                        fileHash = 0
                else:
                    fileHash = 0
                # Add or append the file path
                if (fileHash != 0):
                    if ((fileSize == 0 and scanOptions['MaxFileSize'] == 0 and scanOptions['IncludeEmptyFiles'].upper() == 'TRUE')
                        or (fileSize > 0 and scanOptions['MaxFileSize'] == 0) 
                        or (fileSize > 0 and scanOptions['MaxFileSize'] > 0 and scanOptions['MaxFileSize'] >= fileSize)):
                    
                        if fileHash in dups:
                            dups[fileHash].append(path)
                        else:
                            dups[fileHash] = [path]
    return dups
 
 
# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
 
 
def hashfile(path, blocksize, algorithm):
    valSHA512 = 32
    valSHA384 = 16
    valSHA256 = 8
    valSHA224 = 4
    valSHA1 = 2
    valMD5 = 1
    useSHA512 = False
    useSHA384 = False
    useSHA256 = False
    useSHA224 = False
    useSHA1 = False
    useMD5 = False
    compositeHash = ''

    if algorithm >= valSHA512:
        useSHA512 = True
        algorithm = algorithm - valSHA512
    if algorithm >= valSHA384:
        useSHA384 = True
        algorithm = algorithm - valSHA384
    if algorithm >= valSHA256:
        useSHA256 = True
        algorithm = algorithm - valSHA256
    if algorithm >= valSHA224:
        useSHA224 = True
        algorithm = algorithm - valSHA224
    if algorithm >= valSHA1:
        useSHA1 = True
        algorithm = algorithm - valSHA1
    if algorithm >= valMD5:
        useMD5 = True
        algorithm = algorithm - valMD5

    try:
        afile = open(path, 'rb')
        if useMD5: hasherMD5 = hashlib.md5()
        if useSHA1: hasherSHA1 = hashlib.sha1()
        if useSHA224: hasherSHA224 = hashlib.sha224()
        if useSHA256: hasherSHA256 = hashlib.sha256()
        if useSHA384: hasherSHA384 = hashlib.sha384()
        if useSHA512: hasherSHA512 = hashlib.sha512()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            if useMD5: hasherMD5.update(buf)
            if useSHA1: hasherSHA1.update(buf)
            if useSHA224: hasherSHA224.update(buf)
            if useSHA256: hasherSHA256.update(buf)
            if useSHA384: hasherSHA384.update(buf)
            if useSHA512: hasherSHA512.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        if useMD5: compositeHash = compositeHash + hasherMD5.hexdigest()
        if useSHA1: compositeHash = compositeHash + hasherSHA1.hexdigest()
        if useSHA224: compositeHash = compositeHash + hasherSHA224.hexdigest()
        if useSHA256: compositeHash = compositeHash + hasherSHA256.hexdigest()
        if useSHA384: compositeHash = compositeHash + hasherSHA384.hexdigest()
        if useSHA512: compositeHash = compositeHash + hasherSHA512.hexdigest()
        return compositeHash
    except:
        print('Error calculating hash of ', path)
        return 0
 
 
def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print('The following files are identical. The name could differ, but the content is identical')
        print('___________________')
        for result in results:
            for subresult in result:
                print('\t\t%s' % subresult)
            print('___________________')
 
    else:
        print('No duplicate files found.')

def loadDefaultScanOptions():
    #These values will be used if they are not set through config file or command line parameters
    scanOptions = {}
    scanOptions['FilterMode'] = 'EXCLUDE'
    scanOptions['FilterFile'] = ''
    scanOptions['SubDirs'] = 'TRUE'
    scanOptions['MaxFileSize'] = 0
    scanOptions['IncludeEmptyFiles'] = 'FALSE'
    scanOptions['Blocksize'] = 65536
    scanOptions['HashAlgorithm'] = 1
    return scanOptions

def loadConfigFileScanOptions(configFile):
    #These values will override the defaults if they are set
    scanOptions = {}
    scanOptions = loadDefaultScanOptions()
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
        scanOptions['Blocksize'] = int(config.get('Advanced', 'Blocksize'))
    if config.has_option('Advanced', 'HashAlgorithm') and (config.get('Advanced', 'HashAlgorithm').isnumeric()):
        scanOptions['HashAlgorithm'] = int(config.get('Advanced', 'HashAlgorithm'))
    return scanOptions

def loadFilters(filterFile):
    if os.path.exists(filterFile):    
        with open(scanOptions['FilterFile']) as f:
            filters = f.read().splitlines()
    else:
        filters = ""
    return filters

def printHashAlgorithms(algorithm):
    valSHA512 = 32
    valSHA384 = 16
    valSHA256 = 8
    valSHA224 = 4
    valSHA1 = 2
    valMD5 = 1
    useSHA512 = False
    useSHA384 = False
    useSHA256 = False
    useSHA224 = False
    useSHA1 = False
    useMD5 = False

    print('*  USING ALGORITHMS:')
    if algorithm >= valSHA512:
        useSHA512 = True
        algorithm = algorithm - valSHA512
        print('*  + SHA512 ')
    if algorithm >= valSHA384:
        useSHA384 = True
        algorithm = algorithm - valSHA384
        print('*  + SHA384 ')
    if algorithm >= valSHA256:
        useSHA256 = True
        algorithm = algorithm - valSHA256
        print('*  + SHA256 ')
    if algorithm >= valSHA224:
        useSHA224 = True
        algorithm = algorithm - valSHA224
        print('*  + SHA224 ')
    if algorithm >= valSHA1:
        useSHA1 = True
        algorithm = algorithm - valSHA1
        print('*  + SHA1 ')
    if algorithm >= valMD5:
        useMD5 = True
        algorithm = algorithm - valMD5
        print('*  + MD5 ')

def loadCommandLineScanOptions(args, scanOptions):
    if args['filterMode'] != None and (args['filterMode'].upper()=='INCLUDE' or args['filterMode'].upper()=='EXCLUDE' or args['filterMode'].upper()=='NONE'):
        scanOptions['FilterMode'] = args['filterMode'].upper()
    if args['filterFile'] != None:
        if os.path.exists(args['filterFile']):
            scanOptions['FilterFile'] = args['filterFile']
    if args['subDirs'] != None and (args['subDirs'].upper()=='TRUE' or args['subDirs'].upper())=='FALSE':
        scanOptions['SubDirs'] = args['subDirs'].upper()
    if args['maxFileSize'] != None:
        scanOptions['MaxFileSize'] = int(args['maxFileSize'])
    if args['includeEmptyFiles'] != None and (args['includeEmptyFiles'].upper()=='TRUE' or args['includeEmptyFiles'].upper())=='FALSE':
        scanOptions['IncludeEmptyFiles'] = args['includeEmptyFiles'].upper()
    if args['blocksize'] != None:
        scanOptions['Blocksize'] = int(args['blocksize'])
    if args['hashAlgorithm'] != None:
        scanOptions['HashAlgorithm'] = int(args['hashAlgorithm'])
    return scanOptions

if __name__ == '__main__':

    dups = {}
    scanOptions = {}
    scanOptions = loadDefaultScanOptions()
    
    parser = argparse.ArgumentParser(description='Search for duplicate files in one or more folders')
    parser.add_argument('-cfg', '--configFile', help='Configuration File for script', required=False)
    parser.add_argument('-fm', '--filterMode', help='Filter Mode', choices=['INCLUDE', 'EXCLUDE', 'NONE'], required=False)
    parser.add_argument('-ff', '--filterFile', help='File containing list of filters to be applied if File Mode is not NONE', required=False)
    parser.add_argument('-s', '--subDirs', help='Scan subdirectories of selected folders?', choices=['TRUE', 'FALSE'], required=False)
    parser.add_argument('-ms', '--maxFileSize', type=int, help='Maximum size of files to be scanned', required=False)
    parser.add_argument('-emp', '--includeEmptyFiles', help='Include files with no content in results?', choices=['TRUE', 'FALSE'], required=False)
    parser.add_argument('-bs', '--blocksize', type=int, help='Blocksize for file reads', required=False)
    parser.add_argument('-ha', '--hashAlgorithm', type=int, help='Algorithm(s) to be used for file hashing', required=False)
    parser.add_argument('-dirs', '--directories', nargs='+', help = 'List of directories to scan', required=True)
    args = vars(parser.parse_args())
    
    config = configparser.ConfigParser()
    scanOptions['ConfigFile']=""
    if args['configFile'] != None: scanOptions['ConfigFile'] = args['configFile']
    configFile = scanOptions['ConfigFile']
    print('************************************')
    if os.path.exists(configFile):
        scanOptions = loadConfigFileScanOptions(configFile)
    loadCommandLineScanOptions(args, scanOptions)
    filters = loadFilters(scanOptions['FilterFile'])
    folders = args['directories']

    printHashAlgorithms(scanOptions['HashAlgorithm'])
    print('*  FOLDER(S) TO SCAN: ', folders)
    print('*  SCAN OPTIONS USED: ', scanOptions)
    print('*  FILTERS: ', filters)
    print('************************************')

    for i in folders:
        # Iterate the folders given
        if os.path.exists(i):
            # Find the duplicated files and append them to the dups
            joinDicts(dups, findDup(i, scanOptions['FilterMode'], filters, scanOptions))
        else:
            print('%s is not a valid path, please verify' % i)
            sys.exit()
    printResults(dups)
