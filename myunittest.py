import unittest
from find_dups import loadDefaultScanOptions, loadConfigFileScanOptions, hashfile, findDup
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_hashfile(self):
        self.assertEqual(hashfile('c:\\invalidpath\\invalidfile.txt',65536,1),0)
        #Invalid blocksize should default to 65536
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', -1, 1),'b7356a4b8764b54b3e3119dc2394bc7e')
        #Invalid algorithm should default to MD5
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, -1),'b7356a4b8764b54b3e3119dc2394bc7e')
        #Check MD5 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 1),'b7356a4b8764b54b3e3119dc2394bc7e')
        #Check SHA1 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 2),'b38005fd56fa2de86f6458cb73d0d794912e94c0')
        #Check SHA224 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 4),'4f97a461d81e2aab7e1d7e0b208271317b07a6fe12d0fbbb1919fdc7')
        #Check SHA256 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 8),'2ec3d40c866e3e2829dbbaade913e97da18eae9a67ae786da7e430a5f1186716')
        #Check SHA384 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 16),'c8482ee90ab9cd3f50915d466c108cdef06b515954b53630aa2964a120adc883099314a4a6e47fb25daaf49ac1143070')
        #Check SHA512 is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 32),'8531c07a2237475934675ac39ef71e8d49dc1c2c48482eead108910112e233bdfa10f60da906a1759b265e6b0db9cd7eaa5e9ec70175c615cc31c3f22529fa05')
        #Check Full Concatenation of all hashing algorithms is calculated correctly
        self.assertEqual(hashfile('c:\\temp\\testfiles\\file1.log', 65536, 63),'b7356a4b8764b54b3e3119dc2394bc7eb38005fd56fa2de86f6458cb73d0d794912e94c04f97a461d81e2aab7e1d7e0b208271317b07a6fe12d0fbbb1919fdc72ec3d40c866e3e2829dbbaade913e97da18eae9a67ae786da7e430a5f1186716c8482ee90ab9cd3f50915d466c108cdef06b515954b53630aa2964a120adc883099314a4a6e47fb25daaf49ac11430708531c07a2237475934675ac39ef71e8d49dc1c2c48482eead108910112e233bdfa10f60da906a1759b265e6b0db9cd7eaa5e9ec70175c615cc31c3f22529fa05')
        

    def test_loadDefaultScanOptionsValidValues(self):
        testDict = {}
        testDict['FilterMode'] = 'EXCLUDE'
        testDict['FilterFile'] = ''
        testDict['SubDirs'] = 'TRUE'
        testDict['MaxFileSize'] = 0
        testDict['IncludeEmptyFiles'] = 'FALSE'
        testDict['Blocksize'] = 65536
        testDict['HashAlgorithm'] = 1
        self.assertDictEqual(loadDefaultScanOptions(), testDict) 


    def test_loadConfigFileScanOptionsValidValues(self):
        testDict = {}
        testDict['FilterMode'] = 'INCLUDE'
        testDict['FilterFile'] = 'c:\\temp\\sample-include-filters.txt'
        testDict['SubDirs'] = 'FALSE'
        testDict['MaxFileSize'] = 100000
        testDict['IncludeEmptyFiles'] = 'TRUE'
        testDict['Blocksize'] = 131072
        testDict['HashAlgorithm'] = 3
        self.assertDictEqual(loadConfigFileScanOptions('c:\\temp\\testfiles\\valid-config.txt'), testDict) 

    def test_loadConfigFileScanOptionsInValidValues(self):
        testDict = {}
        testDict['FilterMode'] = 'EXCLUDE'
        testDict['FilterFile'] = ''
        testDict['SubDirs'] = 'TRUE'
        testDict['MaxFileSize'] = 0
        testDict['IncludeEmptyFiles'] = 'FALSE'
        testDict['Blocksize'] = 65536
        testDict['HashAlgorithm'] = 1
        self.assertDictEqual(loadConfigFileScanOptions('c:\\temp\\testfiles\\bad-config.txt'), testDict)

    def test_loadConfigFileScanOptionsConfigNotFound(self):
        testDict = {}
        testDict['FilterMode'] = 'EXCLUDE'
        testDict['FilterFile'] = ''
        testDict['SubDirs'] = 'TRUE'
        testDict['MaxFileSize'] = 0
        testDict['IncludeEmptyFiles'] = 'FALSE'
        testDict['Blocksize'] = 65536
        testDict['HashAlgorithm'] = 1
        self.assertDictEqual(loadConfigFileScanOptions('c:\\invalidpath\\invalid-config-path.txt'), testDict) 

    def test_findDup(self):
        #Only non-zero sized files of any size should be found
        dups = {}
        results = []
        scanOptions = loadDefaultScanOptions()
        scanOptions['FilterMode'] = 'NONE'
        filters = []
        dups = findDup('c:\\temp\\testfiles', filters, scanOptions)
        results = list(filter(lambda x: len(x) > 1, dups.values()))
        expectedresults = [['c:\\temp\\testfiles\\bigfile1 - Copy.txt', 'c:\\temp\\testfiles\\bigfile1.txt'],
                           ['c:\\temp\\testfiles\\file1 - Copy.log', 'c:\\temp\\testfiles\\file1.log']]
        self.assertListEqual(results, expectedresults)

        #Zero-sized and non-zero sized files of any size should be found
        dups = {}
        results = []
        scanOptions = loadDefaultScanOptions()
        scanOptions['IncludeEmptyFiles'] = 'TRUE'
        scanOptions['FilterMode'] = 'NONE'
        filters = []
        dups = findDup('c:\\temp\\testfiles', filters, scanOptions)
        results = list(filter(lambda x: len(x) > 1, dups.values()))
        expectedresults = [['c:\\temp\\testfiles\\bigfile1 - Copy.txt', 'c:\\temp\\testfiles\\bigfile1.txt'],
                           ['c:\\temp\\testfiles\\emptyfile1.txt', 'c:\\temp\\testfiles\\emptyfile2.txt'],
                           ['c:\\temp\\testfiles\\file1 - Copy.log', 'c:\\temp\\testfiles\\file1.log']]
        self.assertListEqual(results, expectedresults)

        #Zero-sized and non-zero sized files of any size should be found, but only .log files
        dups = {}
        results = []
        scanOptions = loadDefaultScanOptions()
        scanOptions['IncludeEmptyFiles'] = 'TRUE'
        scanOptions['FilterMode'] = 'INCLUDE'
        filters = ['*.log']
        dups = findDup('c:\\temp\\testfiles', filters, scanOptions)
        results = list(filter(lambda x: len(x) > 1, dups.values()))
        expectedresults = [['c:\\temp\\testfiles\\file1 - Copy.log', 'c:\\temp\\testfiles\\file1.log']]
        self.assertListEqual(results, expectedresults)

        #Zero-sized and non-zero sized files of any size should be found, but only .txt files
        dups = {}
        results = []
        scanOptions = loadDefaultScanOptions()
        scanOptions['IncludeEmptyFiles'] = 'TRUE'
        scanOptions['FilterMode'] = 'INCLUDE'
        filters = ['*.txt']
        dups = findDup('c:\\temp\\testfiles', filters, scanOptions)
        results = list(filter(lambda x: len(x) > 1, dups.values()))
        expectedresults = [['c:\\temp\\testfiles\\bigfile1 - Copy.txt', 'c:\\temp\\testfiles\\bigfile1.txt'],
                           ['c:\\temp\\testfiles\\emptyfile1.txt', 'c:\\temp\\testfiles\\emptyfile2.txt']]
        self.assertListEqual(results, expectedresults)

        #Zero-sized and non-zero sized files of any size should be found, but only files less than 30,000 bytes
        dups = {}
        results = []
        scanOptions = loadDefaultScanOptions()
        scanOptions['IncludeEmptyFiles'] = 'TRUE'
        scanOptions['FilterMode'] = 'NONE'
        scanOptions['MaxFileSize'] = 30000
        filters = []
        dups = findDup('c:\\temp\\testfiles', filters, scanOptions)
        results = list(filter(lambda x: len(x) > 1, dups.values()))
        expectedresults = [['c:\\temp\\testfiles\\emptyfile1.txt', 'c:\\temp\\testfiles\\emptyfile2.txt'],
                           ['c:\\temp\\testfiles\\file1 - Copy.log', 'c:\\temp\\testfiles\\file1.log']]
        self.assertListEqual(results, expectedresults)

if __name__ == '__main__':
    unittest.main()