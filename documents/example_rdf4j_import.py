#! /usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
######################### IMPORT ##########################
from __future__ import division
from os import listdir
from os.path import isfile, join

import os.path
import time
import datetime
import sys
import ntpath
import os.path
import re
# import division
# For moving files
import shutil
# To call an external programm or command (here : kdu_compress)
import subprocess
from subprocess import call
from subprocess import Popen, PIPE
# To get the number of processor (for multithreading kdu_compress)
import multiprocessing
# To communicate with Sesame HTTP REST interface
import urllib
import pycurl
# To use a real logger
import logging
####################### END IMPORT ########################
###########################################################


###########################################################
######################## CLASSES ##########################

# Redirect stdout and stderr to a logger in Python
# http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())


# Putting a pyCurl XML server response into a variable (Python)
#  http://stackoverflow.com/questions/256564/putting-a-pycurl-xml-server-response-into-a-variable-python
class Test:
   def __init__(self):
       self.contents = ''

   def body_callback(self, buf):
       self.contents = self.contents + buf

####################### END CLASSES #######################
###########################################################





###########################################################
# SET THESE VARIABLES
###########################################################

# FTP_DEPOSIT=/usr/share/iipimage/
FTP_DEPOSIT="/images/images-to-add/"
PUBLIC_STORAGE="/images/public_storage/"
ARCHIVE_ORIGINALS="/images/archive_originals/"
working_dir="/images/processing/"
ERROR_DIR="/images/error/"
kdu_compress="/opt/Linux-x86-32/kdu_compress"

SESAME_USER_AND_PASSWORD="sesameEditor:randomPassword"


# DEBUG=1
# IS_SIMULATING=true
# PRINT_FOR_EXCEL=true
PRINT_FOR_EXCEL = True

# IS_SIMULATING = True
IS_SIMULATING = False

DEBUG = None

prefixes='''
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX p:<http://saussure.com/property/>
PREFIX saussure:<http://saussure.com/ressource/>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
'''

# graph_file="file://rdf-annotation-c.xml"
graph_file="file://test_001_2013-04-08.xml"
endpoint_update="http://129.194.69.133:8080/openrdf-sesame/repositories/mass4/statements"
endpoint_query="http://129.194.69.133:8080/openrdf-sesame/repositories/mass4"




###########################################################
# DO NOT MODIFY FROM THIS POINT
###########################################################

# - Déplacement de "cote.tif" vers $ARCHIVE/originals
# - Conversion de $ARCHIVE/originals $TEMP/cote.jp2
# - If conversion NOT successful : LOG + send message ?
# - If conversion successful :
# - Déplacement de $TEMP/cote.jp2 vers $PUBLIC_STORAGE/$cote.jp2
# - Génération d'un XML ou JSON ou N3...
# - (SPARQL check) if already exists : LOG + send message ?
# - Else, INSERT dans la base RDF ud XML, JSON ou N3

matched=0
notMatched=0
matched_but_ambiguous=0
fullNumberMatched=0
malformed=0
saussure_objects={}
saussure_objects_not_matched={}
saussure_objects_only_matched={}




###########################################################
######################## FUNCTIONS ########################
###########################################################
def getLocalTime():
return time.asctime( time.localtime(time.time()) )



###########################################################
#
# Construct triples to insert
# Test if they are already in the database
#
###########################################################
def construct_N3_and_test_presence(prefixes, graph_file, endpoint, firstInSansExt, section, box, enveloppes, feuillet):

########## if enveloppes + surface don't exist INSERT ANYWAY
fullInserQuery = ""
# library="bge"
library=""
# section = library + "_" + section
# n3_triple='''saussure:%s rdf:type saussure:Library ;
# p:hasSection saussure:%s .''' % (library, section)
#TODO ajouter la section
# fullInserQuery += n3_triple + "\n"
# print n3_triple + "\n"

box = section + "_" + box
n3_triple='''saussure:%s rdf:type saussure:Section ;
p:hasArchiveBox saussure:%s .''' % (section, box)
# askSectionArchiveBox = ask_sparql(prefixes, n3_triple, endpoint)
fullInserQuery += n3_triple + "\n"
## IF USED AS STRING
subcontainer = mergeString(box, mergeArray(enveloppes, "_"), "_")
surfaceEcriture = mergeString(subcontainer, mergeArray (feuillet, "_"), "_")
if (len(surfaceEcriture) == 0) :
logging.error('''The "feuillet" seems empty .' ''')
return (False, fullInserQuery)

# If there is any subdivision
if ( len(subcontainer) > len(box) ) :
n3_triple='''saussure:%s rdf:type saussure:%s ;
p:hasSubdivisions saussure:%s .''' % (box, "ArchiveBox", subcontainer)
fullInserQuery += n3_triple + "\n"

n3_triple='''saussure:%s rdf:type saussure:%s ;
p:hasSurfaceEcriture saussure:%s .''' % (subcontainer, "Subdivisions", surfaceEcriture)
fullInserQuery += n3_triple + "\n"
# If there's no subdivision ("feuillet" directly in the box)
else :
n3_triple='''saussure:%s rdf:type saussure:%s ;
p:hasSurfaceEcriture saussure:%s .''' % (box, "ArchiveBox", surfaceEcriture)
fullInserQuery += n3_triple + "\n"



if not IS_SIMULATING:
n3_triple="saussure:%s rdf:type saussure:Surface_d_ecriture ." % surfaceEcriture
if (  checkPresenceInTripleStore_askWrapper(prefixes, graph_file, n3_triple, endpoint)  ) :
return (False, fullInserQuery)
n3_triple='''?anything p:hasCote "%s" .''' % surfaceEcriture
if (  checkPresenceInTripleStore_askWrapper(prefixes, graph_file, n3_triple, endpoint)  ) :
return (False, fullInserQuery)

photo = surfaceEcriture + "-DOT-jp2"
n3_triple='''saussure:%s rdf:type saussure:Surface_d_ecriture ;
p:hasCote "%s";
p:hasPhoto saussure:%s . ''' % (surfaceEcriture, surfaceEcriture, photo)
# n3_triple='''saussure:%s rdf:type saussure:Surface_d_ecriture ;
# p:hasCote "%s";
# p:hasSurfaceCouverte saussure:%s .''' % (surfaceEcriture, surfaceEcriture, photo)

fullInserQuery += n3_triple + "\n"
# print n3_triple + "\n"
# askSurfaceEcritureLong = ask_sparql(prefixes, n3_triple, endpoint)
jp2Filename = firstInSansExt + ".jp2"
source = "http://saussure.unige.ch/bge/manuscript/"+ jp2Filename
if not IS_SIMULATING:
n3_triple='''saussure:%s rdf:type saussure:Photo .''' % photo
if (  checkPresenceInTripleStore_askWrapper(prefixes, graph_file, n3_triple, endpoint)  ) :
return (False, fullInserQuery)

n3_triple='''?anything p:hasFilename "%s" .''' % jp2Filename
if (  checkPresenceInTripleStore_askWrapper(prefixes, graph_file, n3_triple, endpoint)  ) :
return (False, fullInserQuery)

n3_triple='''saussure:%s rdf:type saussure:Photo ;
p:hasCote "%s" ;
p:hasSource "%s" ;
p:hasFilename "%s" .''' % (photo, surfaceEcriture, source, jp2Filename)
fullInserQuery += n3_triple + "\n"

# If we arrived here, it should be ok to insert the data in the triple-store !
return (True, fullInserQuery)

def ask_sparql( prefixes, graph_file, n3_triple, endpoint ):
# askQuery = '''%s
# ASK { %s }
# ''' % (prefixes,n3_triple)

askQuery = '''%s
ASK { GRAPH <%s>
{
%s
}
} ''' % (prefixes, graph_file, n3_triple)

askQuery = urllib.urlencode({"query":askQuery})
# print askQuery

# Putting a pyCurl XML server response into a variable (Python)
#  http://stackoverflow.com/questions/256564/putting-a-pycurl-xml-server-response-into-a-variable-python
t = Test()
c = pycurl.Curl()
c.setopt(pycurl.URL, endpoint)
c.setopt(pycurl.HTTPHEADER, ['Accept: application/sparql-results+json, */*;q=0.5', 'Accept-Charset: UTF-8', 'Content-Type: application/x-www-form-urlencoded'])
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, askQuery)
c.setopt(pycurl.VERBOSE, 0)
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 8)
c.setopt(c.FAILONERROR, True)
# Necessary to save the result in a variable
c.setopt(c.WRITEFUNCTION, t.body_callback)

try:
c.perform()
# c.getinfo(pycurl.EFFECTIVE_URL)
http_code = c.getinfo(pycurl.HTTP_CODE)
c.close()
# logging.info( "http_code : " + str(http_code) +"  (expect code : 200)" )
if ( t.contents.lower() == "true" ) :
return True
elif ( t.contents.lower() == "false" ) :
return False
else :
return None
except pycurl.error, error:
errno, errstr = error
logging.error('An error occurred when contacting the triple-store: ' + errstr )
return None


def insert_sparql( prefixes, graph_file, n3_triples, endpoint ):
insertQuery = '''
%s
INSERT DATA {
  GRAPH <%s> {
%s
  }
  } ''' % (prefixes, graph_file, n3_triples )
# print insertQuery
insertQuery = urllib.urlencode({"update":insertQuery})

# Putting a pyCurl XML server response into a variable (Python)
#  http://stackoverflow.com/questions/256564/putting-a-pycurl-xml-server-response-into-a-variable-python
t = Test()

c = pycurl.Curl()
c.setopt(pycurl.URL, endpoint)
c.setopt(pycurl.HTTPHEADER, ['Accept: application/sparql-results+json, */*;q=0.5', 'Accept-Charset: UTF-8', 'Content-Type: application/x-www-form-urlencoded'])
# c.setopt(pycurl.HTTPHEADER, ['Accept: application/sparql-results+json, */*;q=0.5'])
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, insertQuery)
c.setopt(pycurl.VERBOSE, 0)
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 8)
c.setopt(c.FAILONERROR, True)
# Authentication
c.setopt(c.USERPWD, SESAME_USER_AND_PASSWORD)
c.setopt(c.HTTPAUTH, c.HTTPAUTH_DIGEST)
# Necessary to save the result in a variable
c.setopt(c.WRITEFUNCTION, t.body_callback)
try:
c.perform()
http_code = c.getinfo(pycurl.HTTP_CODE)
c.close()
# logging.info("http_code : " + str(http_code)+"  (expect code : 204)")
# Response expected when on successful insert :
# HTTP/1.1 204 NO CONTENT
if ( http_code == 204 ) :
return True
else :
return None

except pycurl.error, error:
errno, errstr = error
logging.error('!!!! An error occurred when contacting the triple-store: ' + errstr )
return None

############################## tiff2jp2 ############################################

def tiff2jp2(input_temp, output_temp) :
global kakadu_cmd
if not IS_SIMULATING:
nb_processors = multiprocessing.cpu_count()
nb_processors = str(nb_processors)
#TODO Check if the command executed correctly
# kakadu_process = subprocess.Popen([kdu_compress, "-i", input, "-o", output], stdout=subprocess.PIPE)
kakadu_cmd = [kdu_compress, "-i", input_temp, "-o", output_temp, "-rate", "-,0.5", "Clayers=2" ,"Creversible=yes", "Clevels=8" ,"Cprecincts={256,256},{256,256},{128,128}", "Corder=RPCL", "ORGgen_plt=yes", "ORGtparts=R", "Cblk={64,64}", "-num_threads", nb_processors ]
kakadu_process = subprocess.Popen(kakadu_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# Wait for the external program to finish
kakadu_process.wait()
# logging.info("################################")
logging.info("# kdu_compress returncode : " + str(kakadu_process.returncode) )
# logging.info("################################")
# logging.info("")
# logging.info("################################")
# logging.info("# kdu_compress stdout :")
logging.info("################################\n" + kakadu_process.stdout.read() )
# Test if stderr is not empty
kdu_stderr = kakadu_process.stderr.read()
if len(kdu_stderr) > 0 :
logging.error("################################")
logging.error("# kdu_compress stderr :")
logging.error("################################")
logging.error( kdu_stderr )
logging.error("################################")
logging.info("")

# if kdu_compress executed correctly
if kakadu_process.returncode == 0 :
return True
else :
return False
else:
print "KDU did nothing because this is a simulation "
# Return value
return True


def moveFromToWrapper (message, fileToMove, fromDir, destDir, logLevel) :
if logLevel == "warning" :
logging.warning(message+"from " + fromDir+" to " + destDir)
else :
logging.info(message+" from " + fromDir +"to " + destDir)
# if os.path.exists(destDir+fileToMove) :
try:
shutil.move(fileToMove, destDir)
except:
logging.error("moving the file (shutil.move) failed")

def setLogger (logging, loggingFile) :
# Basic logging configuration
logging.basicConfig(
filename=loggingFile,
level=logging.DEBUG,
# datefmt='%y-%m-%d %H:%M'),
# filemode='w',
# format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
# format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s'
)

# Preserve the "default" logger (without this, only STDOUT and STDERR are logged)
first_logger = logging.getLogger()
s0 = StreamToLogger(first_logger, logging.INFO)

# Redirect STDOUT to the log file
# stdout_logger = logging.getLogger('STDOUT')
# sl = StreamToLogger(stdout_logger, logging.INFO)
# sys.stdout = sl

# Redirect STDERR to the log file
stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl

# print "Test to standard out"
# raise Exception('Test to standard error')

def printForExcel (status, firstInSansExt, section, box, enveloppes, feuillet, ending) :
print "%s\t" % status ,
print firstInSansExt ,
print "\t"+section ,
print "\t"+box ,
enveloppesString = ""
print "\t"+mergeArray(enveloppes, "_") ,
print "\t"+mergeArray(feuillet, "_") ,
endingString = mergeArray(ending, "_")
if len(endingString) > 0 :
print "\t"+endingString ,
# print "\t" ,
# print filename
print ""

################################ checkPresenceInTripleStore_askWrapper ##############################

def checkPresenceInTripleStore_askWrapper(prefixes, graph_file, n3_triple, endpoint):
#logging.info("Testing (SPARQL ASK) :")
#logging.info(n3_triple)
askResult = ask_sparql(prefixes, graph_file, n3_triple, endpoint)
#logging.info("Return : " + str(askResult) )
if askResult :
logging.error('''The triple "%s" already exists .''' % n3_triple)
# return (False, fullInserQuery)
return askResult

############################## mergeString #####################################
def mergeString (string1, string2, separator) :
tempString = ""
if ( len(string1) > 0 ) and ( len(string2) > 0 ) :
tempString += string1+separator+string2
elif ( len(string1) > 0 ) and ( len(string2) == 0 ) :
tempString += string1
elif ( len(string1) == 0 ) and ( len(string2) > 0 ) :
tempString += string2
return tempString

############################## mergeArray #####################################
#
#  transform [x1, ..., xn] to x1_x2_ ... _xn
#
###############################################################################
def mergeArray (arrayToMerge, separator) :
tempString = ""
if len(arrayToMerge) > 0 :
for temp in arrayToMerge :
tempString += temp+separator

# Removes the last character (it should be "separator")
if len(tempString)> 0 :
tempString = tempString[:-1]
return tempString

#
# la peste soit de ces langages sans typage statique
#
def mergeBackTokens (startRange, firstInSansExtArray, firstRegex, secondRegex) :
mergeIndex = -1
removeIndex = -1
for i in range(startRange,len(firstInSansExtArray)):
if re.match(firstRegex, firstInSansExtArray[i] )  is not None:
if ( i+1 < len(firstInSansExtArray) ) and re.match(secondRegex, firstInSansExtArray[i+1] ) is not None:
mergeIndex = i
removeIndex = i+1
break
if mergeIndex >= 0 :
# Merge (with underscore) element at "i" and "i+1"
firstInSansExtArray[mergeIndex] += "_"+firstInSansExtArray[removeIndex]
firstInSansExtArray[removeIndex:removeIndex+1] = []

############################# tokeniszeAndSyntaxe  ###################################
#
# Analyze a filename, extracts the section, box, enveloppe, feuillet parts
#
######################################################################################

def tokeniszeAndSyntaxe ( filename ):
global IS_SIMULATING
filename = filename.strip()
# Removes path
firstIn = ntpath.basename(filename)
# Removes extension
firstInSansExt = os.path.splitext(firstIn)[0]
# Split on token "_" ...
firstInSansExtArray = firstInSansExt.split("_")
# ... and merge back tokens that need to be together
# MERGE BACK TOKENS
###
### from here -- does the same thing as the regular expression in the following function
### should be removed
###
mergeBackTokens(0,firstInSansExtArray,"^ms$", "^fr$")
mergeBackTokens(0,firstInSansExtArray,"^arch$", "^saussure$")
mergeBackTokens(0,firstInSansExtArray,"^cours$", "^univ$")
mergeBackTokens(2,firstInSansExtArray,"^(1ere|[2-4]eme)$", "^couv$")
mergeBackTokens(2,firstInSansExtArray,"^(1ere|[2-4]eme)$", "^couv$")
mergeBackTokens(2,firstInSansExtArray,"^bis$", "^v$")
mergeBackTokens(2,firstInSansExtArray,"^piece$", "[0-9]+(v|r|bis|bis_v)?")
# Attention, deux passes !
mergeBackTokens(2,firstInSansExtArray,"^garde$", "^(ant|post)$")
mergeBackTokens(2,firstInSansExtArray,"^garde_(ant|post)$", "^v$")
# print filename.splitlines(True)

# Reset/init values
section      = ""
box          = ""
enveloppes   = []
feuillet     = []
ending       = []
section_box=""
section_box_enveloppes=""
# Get the section : ms_fr or arch_saussure
temp = firstInSansExtArray[0]
if re.match("^(ms_fr|arch_saussure|cours_univ)$", temp )  is not None:
section = temp

temp = firstInSansExtArray[1]
if re.match("^([0-9]+(b|bis)?)$", temp )  is not None:
box = temp


i=2
outBreak = None
# # De 3 à longueur (=de 1ère enveloppe à dernier élément)
# # for i in range(3,len(firstInSansExtArray)):
# De 2 à longueur (=de 1ère enveloppe à dernier élément)
for i in range(2,len(firstInSansExtArray)):
# if re.match("^([0-9]+(b|bis)?)$", firstInSansExtArray[i] ) is not None:
# TODO  (f|p|piece_)    => "piece" really useful ?
if not re.match("^(((0|z)+)|(env)|(dossier)|(garde_(ant|post)(_v)?)|(1ere_couv|[2-4]eme_couv)|((f|p|piece_)[0-9]+(v|r|bis|bis_v)?(_[0-9]+(v|bis|bis_v)?)?))$", firstInSansExtArray[i] ) is not None:
# enveloppes = enveloppes + "_" + firstInSansExtArray[i]
enveloppes.append(firstInSansExtArray[i])
else:
outBreak = True
break;
outBreak2 = False
# Si on est sorti à cause du break (=que le token n'est pas une enveloppe)
if outBreak :
# ((_env)|(_dossier)|(_(f|p)[0-9]+(v|r)?(_[0-9]+v?)?))
feuilletTTT = ""
for j in range(i,len(firstInSansExtArray)):
feuilletTTT += "_"+firstInSansExtArray[j]

if re.match("^((_(0|z)+)?((_env)|(_dossier)|(_garde_(ant|post)(_v)?)|(_1ere_couv)|(_[2-4]eme_couv)|(_(f|p|piece_)[0-9]+(v|r|bis|bis_v)?(_[0-9]+(v|bis|bis_v)?)?)){1,2})$", feuilletTTT ) is not None or re.match("^_[0]+$", feuilletTTT )  is not None :
feuillet.append(firstInSansExtArray[j])
# elif re.search("(_1ere_couv|_[2-4]eme_couv|(_(0|z)+))$", feuilletTTT ) is not None :
elif re.search("(piece|_(0|z)+)$", feuilletTTT ) is not None :
feuillet.append(firstInSansExtArray[j])
else:
outBreak2 = True
break;
if outBreak2 :
for k in range(j,len(firstInSansExtArray)):
ending.append(firstInSansExtArray[k])
# print ending
section_box = section + "_" + box
section_box_enveloppes = section_box + "_" + mergeArray(enveloppes, "_")

return (filename, firstIn, firstInSansExt, firstInSansExtArray, section, box, enveloppes, feuillet, ending, section_box, section_box_enveloppes)
#############################################################################################
#
# Analyze a filename, extracts the section, box, enveloppe, feuillet parts, insert triples, create jpeg files
#
#############################################################################################

def processFilename ( filename, action, traceFile ):
global logging
filename, firstIn, firstInSansExt, firstInSansExtArray, section, box, enveloppes, feuillet, ending, section_box, section_box_enveloppes = tokeniszeAndSyntaxe(filename)

firstInFullPath = FTP_DEPOSIT+"/"+firstIn

if action == "SECOND PARSING":
global saussure_objects_only_matched
global fullNumberMatched
if section_box_enveloppes in saussure_objects_only_matched:
fullNumberMatched = fullNumberMatched+1
else :
if not IS_SIMULATING:
logging.info("")
logging.info("########   Processing " + firstInSansExt )
logging.info("")

regexForCompleteFilename  = "^(?P<sect>ms_fr|arch_saussure|cours_univ)"   # 1. section
regexForCompleteFilename += "(_(?P<box>[0-9]+(bis|[a-z])?))"              # 2. box
regexForCompleteFilename += "(_(?P<subdiv>[0-9]+[a-zA-Z]*(_[0-9]+[a-zA-Z]*)*))?"         # 3. subdivision / envelopes
regexForCompleteFilename += "(_(?P<feuil>.*))"                          # 4. feuillet

match = re.match(regexForCompleteFilename, firstInSansExt)

xsection = ""
xbox = ""
xsenveloppes = ""
xsfeuillet = ""
xsending = ""
xenveloppes = []
xfeuillet = []
xending = []
if match is not None :
xsection = match.group('sect')
xbox = match.group('box')
if match.group('subdiv') is not None :
  xsenveloppes = match.group('subdiv')
  xenveloppes = xsenveloppes.split('_')
if match.group('feuil') is not None :
  xsfeuillet = match.group('feuil')
  xfeuillet = xsfeuillet.split('_')

if match is not None :
global matched
matched = matched+1
section = xsection
box = xbox
enveloppes = xenveloppes
feuillet = xfeuillet
ending = xending
section_box = section + "_" + box
section_box_enveloppes = section_box + "_" + mergeArray(enveloppes, "_")
# print firstInSansExt
# print(firstInSansExt, section, box, enveloppes, feuillet, ending, section_box, section_box_enveloppes)
traceFile.write(firstInSansExt+';'+xsection+';'+xbox+';'+xsenveloppes+';'+xsfeuillet+'\n')

# print firstInSansExt+';'+xsection+';'+xbox+';'+xsenveloppes+';'+xsfeuillet+';'+xsending+'\n'
if IS_SIMULATING:
global saussure_objects
saussure_objects[section_box_enveloppes]=section_box_enveloppes
return

isValidToInsert, full_n3_triples = construct_N3_and_test_presence(prefixes, graph_file, endpoint_query, firstInSansExt, section, box, enveloppes, feuillet)

if isValidToInsert :
if not IS_SIMULATING:
# logging.info("This manuscript doesn't seem to be present in the triple-store.")
logging.info("\n<RDF>\n" + full_n3_triples + "\n</RDF>")
else :
if not IS_SIMULATING:
logging.error("The manuscript (or part of the structure that represents it) seem to be already present in the triple-store. Please check the log file.")
print("----already in the db")
# logging.warning("Moving original from " + FTP_DEPOSIT + " to " + ERROR_DIR)

moveFromToWrapper("Moving original file ", firstInFullPath, FTP_DEPOSIT, ERROR_DIR, "warning")
logging.error("Here are the triples constructed so far : \n" + full_n3_triples)
return False

#TODO check if last modification is older than 2hours
# logging.info("  Moving original file to " + working_dir)
if not IS_SIMULATING:
moveFromToWrapper("Moving original file ", firstInFullPath, FTP_DEPOSIT, working_dir, "info")
# logging.info("Moving original file to ")
# logging.info("\t" + working_dir)
# shutil.move(firstInFullPath, working_dir)
# Convert to JPEG2000
if not IS_SIMULATING:
logging.info("  Converting to JPGE2000")

input_temp  = working_dir + firstIn
output_temp = working_dir+"/"+firstInSansExt+".jp2"
conversion_result = tiff2jp2(input_temp, output_temp)
# exit();

if conversion_result:
logging.info("KDU - Conversion successful")
# logging.info("  Moving original file from " + working_dir + " to " + ARCHIVE_ORIGINALS)
# Move From To : message, file, sourceDir, DestDir
moveFromToWrapper("Moving original file ", input_temp, working_dir, ARCHIVE_ORIGINALS, "info")
# logging.info("\t" + working_dir)
# logging.info("to")
# logging.info("\t" + ARCHIVE_ORIGINALS)
# shutil.move(input_temp, ARCHIVE_ORIGINALS)
# logging.info("  Moving JP2000 file from " + working_dir + " to " + PUBLIC_STORAGE)
moveFromToWrapper("Moving JP2000 file ", output_temp, working_dir, PUBLIC_STORAGE, "info")
# logging.info("\t" + working_dir)
# logging.info("to")
# logging.info("\t" + PUBLIC_STORAGE)
# shutil.move(output_temp, PUBLIC_STORAGE)
logging.info("Inserting in the triple-store")

insert_return = insert_sparql(prefixes, graph_file, full_n3_triples, endpoint_update)
if insert_return :
logging.info("RDF Insert successful !")
# logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!")
# logging.info("!        SUCCESS        !")
# logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!")
# logging.info("")
# logging.info("")
return True
else :
logging.error("RDF Insert problem !!!")
logging.error("FAILED")
return False
else :
logging.error("KDU - ERROR")
logging.error("!!!! ERROR : Conversion failed")
logging.error("")
# logging.warning("  Moving original from " + working_dir + " to " + ERROR_DIR)
moveFromToWrapper("Moving original file ", input_temp, working_dir, ERROR_DIR, "warning")
# logging.warning("Moving original file from ")
# logging.warning("\t" + working_dir)
# logging.warning("to")
# logging.warning("\t" + ERROR_DIR)
# shutil.move(input_temp, ERROR_DIR)
if os.path.isfile(output_temp) :
# logging.warning("  Moving JP2000 file from " + working_dir + " to " + ERROR_DIR)
moveFromToWrapper("Moving JP2000 file ", output_temp, working_dir, ERROR_DIR, "warning")
# logging.warning("\t" + working_dir)
# logging.warning("to")
# logging.warning("\t" + ERROR_DIR)
# shutil.move(output_temp, ERROR_DIR)
else :
logging.warning("The JP2000 file '%s' doesn't seem to have been created, " % output_temp)
logging.warning("therefore, no reason to move it to %s . " % ERROR_DIR)
return False
else:  # match is None
if not IS_SIMULATING:
logging.info("")
logging.error("######################")
logging.error("#####    ERROR   #####")
logging.error("The filename doesn't match any recognized/acceptable pattern.")

# if the filename doesn't match the regex
# Check if the filename is malformed (=contains some common forbidden characters)
global notMatched
notMatched = notMatched+1
if re.search("(-)|( )|(__)|(^$)", firstInSansExt)  is not None:
# print "Malformed"
global malformed
malformed=malformed+1

if IS_SIMULATING:
global saussure_objects_not_matched
saussure_objects_not_matched[section_box_enveloppes]=section_box_enveloppes
if PRINT_FOR_EXCEL:
printForExcel("ERROR", firstInSansExt, section, box, enveloppes, feuillet, ending)

# if re.search("(-)|( )|(__)|(^$)", firstInSansExt ) is not None:
# print "* Caractère interdit [espace ( ), tiret (-) ou double underscore(__)]"
# if re.match("^$", section ) is not None:
# print "* Section empty !"
# if re.match("^$", box ) is not None:
# print "* Box empty !"
# if len(feuillet) < 1 :
# print "* feuillet empty !"
# else:
# print "* problème avec syntaxe du feuillet !"

return

logging.warning("According to the predefined patterns,")
logging.warning("the filename '%s' was tokenized like this :" % firstInSansExt)
# elif DEBUG:
logging.info("\tsection    : "+section)
logging.info("\tbox        : "+box)

# for env in enveloppes :
logging.info("\tenveloppes : " + mergeArray(enveloppes, "_") )
# for feuilletTemp in feuillet :
logging.info("\tfeuillet   : "+ mergeArray(feuillet, "_") )
logging.info("\tOriginal   : "+filename)

# logging.warning("  Moving original file to " + ERROR_DIR)
# logging.warning("Moving original file to ")
# logging.warning("\t" + ERROR_DIR)
if not IS_SIMULATING:
moveFromToWrapper("Moving original file to ", firstInFullPath, FTP_DEPOSIT, ERROR_DIR, "warning")
# shutil.move(firstInFullPath, ERROR_DIR)

logging.error("####   END ERROR   ###")
logging.error("######################")
logging.info("")


###########################################################
###################### END FUNCTIONS ######################
###########################################################

outputToPHP = False
if ( len(sys.argv) > 2 ) :
if ( sys.argv[2] == "outputToPHP" ) :
IS_SIMULATING = False
outputToPHP = True
###########################################################
# BEGIN MAIN
###########################################################

xout = open('_name_struct.csv', 'w')
xout.write("Filename;Section;Boite;Subdivision;Feuillet, page, dossier, enveloppe...;Suffixe libre\n")

if IS_SIMULATING:
File = str(sys.argv[1])
# setLogger(logging,"DDEDEDE.txt")
# setLogger(logging,"/dev/null")
logging = None

print "############################################################"
print "############################################################"
print "################ !!!! SIMULATION !!!! ######################"
print "####### !!!! NOTHING WILL ACTUALLY BE DONE !!!! ############\n"
print "*** " + getLocalTime()
print "###########################################################"
print "###########################################################"

if PRINT_FOR_EXCEL:
print "status",
print "\tname",
print "\tsection",
print "\tbox",
print "\tenveloppes",
print "\tfeuillet",
print "\tending",
print ""
with open(File) as infile:
for filename in infile:
processFilename( filename, '', xout )
# Diff
saussure_objects_only_matched = set(saussure_objects.keys()) - set(saussure_objects_not_matched.keys())

print "\t************************"
print "SECOND PARSING BEGIN"

with open(File) as infile:
for filename in infile:
processFilename( filename , "SECOND PARSING", xout)

print "SECOND PARSING END"
print "fullNumberMatched =>" + str(fullNumberMatched)
print "\t************************\n"

print ""
print "Matched (matched) : " + str(matched)
print "Not matched (notMatched) : " + str(notMatched)
print "Matched (matched_but_ambiguous) : " + str(matched_but_ambiguous)
print "Malformed (malformed) : " + str(malformed)
print ""

rapport_matched = 100.0 * matched/(notMatched+matched+matched_but_ambiguous)
rapport_not_matched = 100 * notMatched/(notMatched+matched+matched_but_ambiguous)
rapport_matched_but_ambiguous = 100 * matched_but_ambiguous/(notMatched+matched+matched_but_ambiguous)
print("Matched : %.3f" % rapport_matched) + " %"
print("Not matched : %.3f" % rapport_not_matched) + " %"
print ("Matched (but ambiguous) : %.3f" % rapport_matched_but_ambiguous)  + " %"
print ""
elif outputToPHP:
filename, firstIn, firstInSansExt, firstInSansExtArray, section, box, enveloppes, feuillet, ending, section_box, section_box_enveloppes = tokeniszeAndSyntaxe(sys.argv[1])
print section
print box
# print mergeArray(enveloppes, "_") ,
# print mergeArray(feuillet, "_") ,
# endingString = mergeArray(ending, "_")
# if len(endingString) > 0 :
# print endingString
print mergeArray(enveloppes, "_")
print mergeArray(feuillet, "_")
print mergeArray(ending, "_") # if string empty, return an empty string for PHP script (variable definied in PHP, even if empty).
else :
start_time = time.time()

# Set the logger with Basic logging configuration and
# redirection of STDOUT and STDERR to the logging file
setLogger(logging,"log_auto_alim_"+datetime.datetime.now().isoformat().replace('T','_')+".log")

logging.info("############################################################")
logging.info("############################################################")
logging.info("################ BEGINNING AUTO ALIMENTATION ###############")
logging.info("############################################################")
logging.info(" *** " + getLocalTime() )
logging.info("")

# ls -t -r  =>  sort by modification date (-t), reverse order (-r)
# ftp_deposit_content=`ls -t -r $FTP_DEPOSIT`
# http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
ftp_deposit_content = [ f for f in listdir(FTP_DEPOSIT) if isfile(join(FTP_DEPOSIT,f)) ]
if len(ftp_deposit_content) == 0 :
logging.info("The folder is empty. Nothing to do !")
else:
logging.info("The folder contains : ")
# print ftp_deposit_content
for firstIn in ftp_deposit_content:
logging.info("   "+firstIn)
logging.info("")
for firstIn in ftp_deposit_content:
print firstIn
processFilename( firstIn, '', xout )

logging.info("")
logging.info("*** " + getLocalTime() )
logging.info("*** Executed in : " + str(time.time() - start_time) + " seconds" )
logging.info("############################################################")
logging.info("################# END AUTO ALIMENTATION ####################")
logging.info("############################################################")
logging.info("############################################################\n\n\n")

xout.close()

###########################################################
# END MAIN
###########################################################
