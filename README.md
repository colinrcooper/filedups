# filedups
Python script for finding duplicate files

usage: find_dups.py [-h] [-cfg CONFIGFILE] [-fm {INCLUDE,EXCLUDE,NONE}]
                    [-ff FILTERFILE] [-s {TRUE,FALSE}] [-ms MAXFILESIZE]
                    [-emp {TRUE,FALSE}] [-bs BLOCKSIZE] [-ha HASHALGORITHM]
                    -dirs DIRECTORIES [DIRECTORIES ...]
                    
optional arguments:
  -h, --help            show this help message and exit
  -cfg CONFIGFILE, --configFile CONFIGFILE
                        Configuration File for script
  -fm {INCLUDE,EXCLUDE,NONE}, --filterMode {INCLUDE,EXCLUDE,NONE}
                        Filter Mode
  -ff FILTERFILE, --filterFile FILTERFILE
                        File containing list of filters to be applied if File
                        Mode is not NONE
  -s {TRUE,FALSE}, --subDirs {TRUE,FALSE}
                        Scan subdirectories of selected folders?
  -ms MAXFILESIZE, --maxFileSize MAXFILESIZE
                        Maximum size of files to be scanned
  -emp {TRUE,FALSE}, --includeEmptyFiles {TRUE,FALSE}
                        Include files with no content in results?
  -bs BLOCKSIZE, --blocksize BLOCKSIZE
                        Blocksize for file reads
  -ha HASHALGORITHM, --hashAlgorithm HASHALGORITHM
                        Algorithm(s) to be used for file hashing
  -dirs DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]
  
  Values supplied through the commandline take precedence over values supplied in a config file.
