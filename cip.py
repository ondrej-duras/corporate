#!/usr/bin/env python2
#=vim high Comment ctermfg=brown

## Manual ############################################################# {{{ 1

VERSION = 2019.061701
MANUAL  = """
NAME: Change Implementation Procedures to PDF
FILE: cip.py
FILE: 085-PDF-ReportLab-Code2PDF.py
FILE: 087-PDF-ReportLab-NetConf2PDF.py
NOTE: ====== FUNCTIONAL DRAFT ONLY :-) ===========

DESCRIPTION:
  Converts Configuration Implementation Procedure File into PDF.
  For now it's very simple but functional exporter.

USAGE:
  cip.py -i CRQ123-AllDetails.txt -o CRQ123-4DNO.pdf

CLI PARAMETERS:
  -i   --input file
  -o   --output file

INPUT FORMAT:

 #=text - blue proportional text in human language
 #=code - black non-proportional code in computer language
 #=page - page delimiter
 #=hash - allows lines matching /^#/
 #=nohash - suppress lines matching /^#/ (default)
 #=fix - interprets <<< as yellow marker  (default)
 #=nofix - suppress yellow markers
 #=head Chapter 1 - prints a label "Chapter 1"
 #=cut - suppress following lines (default)
 #=pdfoutput <file> - saves exiting output and open new <file>

PREREQUISITIES:
  pip2 install reportlab
  pip2 install svglib3

SEE ALSO:
  https://github.com/ondrej-duras

VERSION: %s 
""" % (VERSION)

####################################################################### }}} 1
## Defaults and Packages `############################################# {{{ 1

import sys
import re


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


MODE_COLOR = 2
MODE_DEBUG = ""

FILE_INPUT  = ""
FILE_OUTPUT = ""
FLAG_OUTPUT = 0
fhin  = None
fhout = None


####################################################################### }}} 1
## Initiation ######################################################### {{{ 1

# That registers a font ...but also it attaches whole font into the PDF file
# .... so PDF file size increases significanly with each font used.
#pdfmetrics.registerFont(TTFont('Courier', 'cour.ttf'))
pdfmetrics.registerFont(TTFont('code', 'cour.ttf'))


#pdfmetrics.registerFont(TTFont('Times', 'Times.ttf'))
#pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
#pdfmetrics.registerFont(TTFont('Bookman', 'BOOKOS.TTF'))

pdfmetrics.registerFont(TTFont('text', 'BOOKOS.TTF'))

# A4: sirka=595 vyska=841
pageWidth,pageHeight=A4
#print "vyska=%i sirka=%i" % (height,width)


# BOOKOS.TTF   cour.ttf   arial.ttf   times.ttf   - basic
# BOOKOSB.TTF  courbd.ttf arialbd.ttf timesbd.ttf - bold
# BOOKOSBI.TTF courbi.ttf arialbi.ttf timesbi.ttf - bold italic
# BOOKOSI.TTF  couri.ttf  ariali.ttf  timesi.ttf  - italic
# lucon.ttf    - lucida console
# arimon__.ttf - arial monospaced
# arimonbd.ttf - arial monospaced bold
# BOKOS - Bookman Old Style
# times - Times New Roman

# HelvNeue35_W1G.ttf ... cislo udava hrubku ciary fontu
# HelvNeue45_W1G.ttf Helvetica font
# HelvNeue55_W1G.ttf
# HelvNeue65_W1G.ttf
# HelvNeue75_W1G.ttf


####################################################################### }}} 1
## CLI Interface ###################################################### {{{ 1

def interface():
  global MODE_COLOR, MODE_DEBUG
  global MANUAL, FILE_INPUT, FILE_OUTPUT

  # when no command-line parameters given, show the manual
  if len(sys.argv) < 2:
    print MANUAL
    exit(0)

  # handling command-line parameters
  idx = 1;
  while idx < len(sys.argv):
    argx=sys.argv[idx]; idx=idx+1
    #debug(str(idx)+" : "+argx)
    if re.match("-+i",argx):     FILE_INPUT  = sys.argv[idx]; idx=idx+1; continue # --input
    if re.match("-+o",argx):     FILE_OUTPUT = sys.argv[idx]; idx=idx+1; continue # --output
    if re.match("-+c",argx):     MODE_COLOR = 1;    continue  # --color
    if re.match("-+d",argx):     MODE_DEBUG = ".*"; print "debug"; continue # --debug
    if re.match("-+D",argx):     MODE_DEBUG=sys.argv[idx+1]; idx=idx+1; continue # --Debug <filter>
    if re.match("-+no-?c",argx): MODE_COLOR = 0;    continue # --no-color
    if re.match("-+no-?d",argx): MODE_DEBUG = "";   continue # --no-debug
    if re.match("-+e",argx):     TEST_ECHO.append(sys.argv[idx+1]); idx=idx+1; continue  # --echo <text>
    print("Wrong parameter '%s' !" % (argx))  # command-line syntax error handling

  # Handling TTY colors  
  if MODE_COLOR == 2:
    if sys.stdout.isatty(): MODE_COLOR = 1
    else:                   MODE_COLOR = 0
  if MODE_COLOR == 1:
    try:
       import colorama
       colorama.init()        
    except:
       MODE_COLOR = 0

####################################################################### }}} 1
## PDF Export ######################################################### {{{ 1

def pdfExport(FILE_INPUT,FILE_OUTPUT):
  global fhin,fhout
  
  bgline  = 820    # 1st line Y-coordinates / bottom-left point of the first letter is going to be printed at 20,820
  PGNUM   = 0      # page counter
  DIRTY   = 0      # =1 means there was printed something on the page already (DIRTY page)
  HASH    = 1      # 0= skips all lines matching /^#/
  COMMENT = '#!;'  # command line delimiters for comment highlighting
  FIX     = "<<<"  # "FIX" line - yellow background
  MODE    = 'cut'

  try:
    fhin  = open(FILE_INPUT,"r")
  except:
    print "#: Error: Cannot ope input file '%s' #1st !" % (FILE_INPUT)
    exit(1)
  if FILE_OUTPUT:
    try:
      fhout = canvas.Canvas(FILE_OUTPUT,pagesize=A4) 
      FLAG_OUTPUT = 1
      PGNUM=1
      fhout.setStrokeColorRGB(0,0,0)
      fhout.setFillColorRGB(0,0,0)
      fhout.setFont("code", 10)
    except:
      print "#: Error: Close the PDF file '%' #2nd !" % (FILE_OUTPUT)
      exit(2)
  else: 
    fhout = None # temporarily


  #for line in fhin:
  #  line = line.rstrip() # equivalent to chomp()
  line = "."
  fflag = True
  while fflag:
    try:
      line = fhin.readline()
      if line == "":
        fflag = False
        break
      line = line.rstrip()
    except:
      break

    # while there is none output file defined yet,
    # then prevent another attempt to inpetpret a line
    if fhout == None:
      if not re.match('#=pdfoutput',line):
         continue

    if re.match("#=",line):
      # POD - Plain Old Documentation Tags 
      if re.match('#=code',line):    # next lines are CODE
        fhout.setStrokeColorRGB(0,0,0)
        fhout.setFillColorRGB(0,0,0)
        fhout.setFont("code", 10)
        MODE='code'
        continue

      if re.match('#=text',line):    # next lines are TEXT
        fhout.setStrokeColorRGB(0,0,0.5)
        fhout.setFillColorRGB(0,0,0.5)
        fhout.setFont("text", 10)
        MODE='text'
        continue

      if re.match('#=page',line):    # a page delimiter, next lines are on the next page
        bgline = 820
        PGNUM = PGNUM + 1
        fhout.showPage()
        DIRTY = 0
        if MODE == 'code':
          fhout.setStrokeColorRGB(0,0,0)
          fhout.setFillColorRGB(0,0,0)
          fhout.setFont("code", 10)
        if MODE == 'text':
          fhout.setStrokeColorRGB(0,0,0.5)
          fhout.setFillColorRGB(0,0,0.5)
          fhout.setFont("text", 10)
        continue

      if re.match('#=cut',line):       # next lines are skipped / not exported to PDF
        MODE = 'cut'
        continue

      if re.match('#=hash',line):      # exports /^#/ lines also
        HASH = 1
        continue
      if re.match('#=nohash',line):    # do not export /^#/ lines (and FOLDs for example)
        HASH = 0
        continue
      if re.match('#=comment',line):   # starts highlighting of comments
        COMMENT = '#!;'               # String should contain all line comment delimiters (at least one)
        continue
      if re.match('#=nocomment',line): # prevent highlighting of comments
        COMMENT = ''                  # empty COMMENT means no comment highlighting enabled.
        continue
      if re.match('#=fix',line):       # allows use of <<< for yellow line highlighting
        FIX = '<<<'
        continue
      if re.match('#=nofix',line):     # restricts use of <<< for yellow line highlighting
        FIX = ''
        continue

      if re.match('#=head',line):      # Prints a Head or Label
        # removing a TAG name
        #HEAD = re.sub("^#=head","",line)
        HEAD = fhin.readline().rstrip()
        fhout.saveState()
        #fhout.setStrokeColorRGB(0.75,0.75,0.7)
        fhout.setStrokeColorRGB(0.95,0.95,0.9)
        fhout.setFillColorRGB(0.95,0.95,0.9)
        #fhout.rect(17,bgline-13,595-17-17,16, fill=1)
        fhout.rect(17,bgline-13,595-17-17,19.5, fill=1)
        # preparing a font/style
        #fhout.setStrokeColorRGB(0.3,0.3,0)
        #fhout.setFillColorRGB(0.3,0.3,0)
        fhout.setStrokeColorRGB(0.1,0.1,0.3)
        fhout.setFillColorRGB(0.1,0.1,0.3)
        fhout.setFont("text", 14)
        # printing a HEAD/LABEL onto paper
        fhout.drawString(20,bgline-10,HEAD); DIRTY=1
        # returns previous color
        fhout.restoreState()
        #if MODE == "text":
        #  fhout.setStrokeColorRGB(0,0,0.5)
        #  fhout.setFillColorRGB(0,0,0.5)
        #if MODE == "code":
        #  fhout.setStrokeColorRGB(0,0,0)
        #  fhout.setFillColorRGB(0,0,0)
        # line feeding (extra 10pc)
        bgline = bgline - 20
        if bgline < 20:
          bgline = 820
          PGNUM = PGNUM + 1
          fhout.showPage()
          DIRTY = 0

      if re.match('#=pdfoutput',line):   # destination file for output
        # flushing existing output into previous PDF file
        # of course, if any file has been opened
        if fhout:
          if DIRTY:
            fhout.showPage()
            DIRTY = 0
          try:
            print "Writing file '%s'" % (FILE_OUTPUT)
            fhout.save()
          except:
            print "# Error: The file '%s' is not writable ! #3x" % (FILE_OUTPUT)
        
        # Opens a NEW PDF file  
        FILE_OUTPUT = re.sub("^#=pdfoutput\s+","",line)
        if FILE_OUTPUT:
          try:
            print "Trying open new '%s' file..." % (FILE_OUTPUT)
            fhout = canvas.Canvas(FILE_OUTPUT,pagesize=A4) 
            FLAG_OUTPUT = 1
          except:
            print "#: Error: Close the PDF file '%' !" % (FILE_OUTPUT)
            exit(2)
          else:
            print "File '%s' opened." % (FILE_OUTPUT)
        else: 
          fhout = None # temporarily
          continue

        # Starting 1st page of new file
        bgline = 820
        PGNUM = PGNUM + 1
        DIRTY = 0
        if MODE == 'code':
          fhout.setStrokeColorRGB(0,0,0)
          fhout.setFillColorRGB(0,0,0)
          fhout.setFont("code", 10)
        if MODE == 'text':
          fhout.setStrokeColorRGB(0,0,0.5)
          fhout.setFillColorRGB(0,0,0.5)
          fhout.setFont("text", 10)
        continue 

    # skipping lines in "=cut" mode and HASH notes 
    if MODE == 'cut': continue 
    if (not HASH) and re.match("#",line): continue

    # Drawing yellow rectangle under text / yellow marker / FIX
    if FIX and (FIX in line):
      line = line.replace(FIX,'')
      fhout.saveState()
      fhout.setStrokeColorRGB(1.0,1.0,0.8)
      fhout.setFillColorRGB(1.0,1.0,0.8)
      fhout.rect(17,bgline-1,595-17-17,8, fill=1)
      # returns previous color
      fhout.restoreState()
      #if MODE == "text":
      #  fhout.setStrokeColorRGB(0,0,0.5)
      #  fhout.setFillColorRGB(0,0,0.5)
      #if MODE == "code":
      #  fhout.setStrokeColorRGB(0,0,0)
      #  fhout.setFillColorRGB(0,0,0)


    # highlingthing comments
    if COMMENT and re.match("\s*[%s]" % (COMMENT),line):
      fhout.saveState()
      fhout.setStrokeColorRGB(0.7,0,0)
      fhout.setFillColorRGB(0.7,0,0)
      fhout.drawString(20,bgline,line); DIRTY=1
      # returns previous color
      fhout.restoreState()
      #if MODE == "text":
      #  fhout.setStrokeColorRGB(0,0,0.5)
      #  fhout.setFillColorRGB(0,0,0.5)
      #if MODE == "code":
      #  fhout.setStrokeColorRGB(0,0,0)
      #  fhout.setFillColorRGB(0,0,0)
    else:  
      # standard color
      fhout.drawString(20,bgline,line); DIRTY=1
    bgline = bgline - 10
    if bgline < 20:
      bgline = 820
      PGNUM = PGNUM + 1
      fhout.showPage()
      if MODE == 'code':
        fhout.setStrokeColorRGB(0,0,0)
        fhout.setFillColorRGB(0,0,0)
        fhout.setFont("code", 10)
      if MODE == 'text':
        fhout.setStrokeColorRGB(0,0,0.5)
        fhout.setFillColorRGB(0,0,0.5)
        fhout.setFont("text", 10)
      DIRTY = 0

  if DIRTY: fhout.showPage()
  try:
    print "Writing file '%s'" % (FILE_OUTPUT)
    fhout.save()
  except:
    print "# Error: The file '%s' is not writable !" % (FILE_OUTPUT)
  fhin.close()


####################################################################### }}} 1
## Main procedure ##################################################### {{{ 1

if __name__ == "__main__":
  interface()
  #if (not FILE_INPUT) or (not FILE_OUTPUT):
  #  print "#! Error: input or output file name was not given !\n";
  #  exit(1)
  #pdfExport(FILE_INPUT,FILE_OUTPUT)
  if (not FILE_INPUT):
    print "#! Error: input file name was not given !\n";
    exit(1)
  pdfExport(FILE_INPUT,FILE_OUTPUT)


####################################################################### }}} 1
# --- end ---
