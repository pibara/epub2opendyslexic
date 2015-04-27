#!/usr/bin/python
import cherrypy
import sys
import zipfile
import uuid
import os
import shutil
import bs4
import BeautifulSoup
import cssutils
import re
from os.path import expanduser

def patchcontent(filename,myuuid):
    #Fetch the XML content into a tree
    fil=open(filename,"r")
    tree=BeautifulSoup.BeautifulSoup(fil.read())
    fil.close()
    #Add font item entries for each of the opendyslexic fonts.
    for font in ["Bold","BoldItalic","Italic","Regular"]:
        fontfile="fonts/OpenDyslexic-" + font + ".otf"
        tag = BeautifulSoup.BeautifulSoup("<item href=\"fonts/OpenDyslexic-" + font + ".otf\" media-type=\"application/x-font-opentype\" id=\"" + font + "\" />")
        tree.manifest.append(tag)
    #Update the uuid
    tree.metadata.find("dc:identifier").string=str(myuuid)
    #Write the updated tree back to xml
    fil=open(filename,"w")
    fil.write(tree.prettify())
    fil.close()
    return

def addopendyslexicbox(filename):
    #FIXME: Here we should add an opendyalexic banner to the image.
    return

def insertfontface(stylesheet,index,text):
    rule=cssutils.css.CSSFontFaceRule()
    rule.cssText=text
    stylesheet.insertRule(rule,index)

def patchstylesheet(filename):
    #First parse the old stylesheet.
    stylesheet=cssutils.parseFile(filename)
    #Process every rule that has a style attached to it.
    for cssrule in stylesheet.cssRules:
        if hasattr(cssrule, 'style'):
            #Make everything OpenDyslexic
            cssrule.style.fontFamily = "OpenDyslexic"
            #Add 0.125em to the font size and use 1.125em as default if undefined. 
            if not "em" in cssrule.style.fontSize:
                cssrule.style.fontSize= "1.125em"
            else:
                cssrule.style.fontSize = str(float(re.sub("[^0-9.]", "", cssrule.style.fontSize))+0.125) + "em"
            #Add 30% to the line height and use 130% as default if undefined.
            if not "%" in  cssrule.style.lineHeight:
                cssrule.style.lineHeight = "130%"
            else:
                cssrule.style.lineHeight = str(int(re.sub("[^0-9]", "", cssrule.style.lineHeight))+30) + "%"
    #Insert an extra fontface rule for each bold/italic flag combination.
    insertfontface(stylesheet,1,"""@font-face {
font-family: 'OpenDyslexic';
src:url(fonts/OpenDyslexic-Regular.otf);
}""")
    insertfontface(stylesheet,2,"""@font-face {
font-family: "OpenDyslexic";
src: url("fonts/OpenDyslexic-Bold.otf");
font-weight: bold;
}""")
    insertfontface(stylesheet,3,"""@font-face {
font-family: "OpenDyslexic";
src: url("fonts/OpenDyslexic-Italic.otf");
font-style: italic, oblique;
}""")
    insertfontface(stylesheet,4,"""@font-face {
font-family: "OpenDyslexic";
src: url("fonts/OpenDyslexic-BoldItalic.otf");
font-weight: bold;
font-style: italic, oblique;
}""")
    #Write back the patched CSS file.
    output=open(filename,"w")
    output.write(stylesheet.cssText)
    output.close()
    return

def patchtoc(filename,myuuid):
    #Fetch the XML content into a tree
    fil=open(filename,"r")
    tree=bs4.BeautifulSoup(fil.read(),"xml")
    fil.close()
    #Update the uuid
    tree.head.find("meta",{"name" : "dtb:uid"})["content"]=myuuid
    #Write the updated tree back to xml
    fil=open(filename,"w")
    fil.write(tree.prettify())
    fil.close()
    return

class ToOpenDyslexic(object):
    def index(self):
        #Return a very basic upload form
        return """
        <html><body>
            <h2>Smashwords Opendyslexic epub converter</h2>
            <form action="upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="myFile" /><br />
            <input type="submit" />
            </form>
        </body></html>
        """
    index.exposed = True
    def upload(self, myFile):
        workdir = expanduser("~") + "/.epub2opendyslexic"
        if not os.path.exists(workdir):
            os.mkdir(workdir)
        debug = False
        #First check for nasty hacking tricks in filename.
        if "/" in myFile.filename :
            return "<html><body><h1>Invalid filename</h1></body></html>"
        #Than check the uploaded file has an epub extension.
        if myFile.filename[-5:] != ".epub":
            return "<html><body><h1>Not an epub!</h1></body></html>"
        #Determine input/output filenames and paths.
        infilename = myFile.filename
        outfilename = infilename[:infilename.rindex(".")] + "-opendyslexic.epub"
        infile=workdir + "/" + infilename
        outfile=workdir + "/" + outfilename
        #First write the uploaded file to the working dir.
        inputfile=open(infile ,"w")            
        size = 0
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)
            inputfile.write(data)
        inputfile.close()
        #Determine a directory path for our temporary stuff.
        tmpdir=workdir + "/" + myFile.filename +"-zipdata.tmp"
        #See if the file we got was an actual zipfile just for sure.
        try:
            epubold=zipfile.ZipFile(infile,"r")
        except:
            return "<html><body><h1>Epub is not a valid zip file!</h1></body></html>"
        #Create an empty zipfile for our transformed epub.       
        epubnew=zipfile.ZipFile(outfile,"w")
        #Get a new UUID so our epub can get an new unique one.
        myuuid=uuid.uuid4() 
        #Now walk trough each file in the epub.        
        for filename in epubold.namelist():
            if filename == "mimetype":
                #This should be the first entry and the only one that needs to be stored without compression.
                mimetype=epubold.open(filename)
                content=mimetype.read()
                epubnew.writestr(filename, content, zipfile.ZIP_STORED)
            else:
                #We extract the file to our working directory.
                epubold.extract(filename,tmpdir)
                fullpath = tmpdir+"/"+filename
                if filename == "content.opf":
                    #patch the content.opf to contain the extra font files and use the new uuid.
                    patchcontent(fullpath,myuuid)
                if filename == "cover.jpg":
                    #Place an opendyslexic banner on the cover image.
                    addopendyslexicbox(fullpath)
                if filename == "stylesheet.css":
                    #Patch the stylesheet to use opendyslexic font and suffiiently large font and lineheight.
                    patchstylesheet(fullpath)
                if filename == "toc.ncx":
                    #Patch the table of content with our new uuid.
                    patchtoc(fullpath,myuuid)
                #Finaly write the (patched or unpatched) file to the output epub zip.
                epubnew.write(fullpath,filename,zipfile.ZIP_DEFLATED)
                #We are done with the extracted file, delete it.
                if not debug:
                    os.remove(fullpath)
        #We are done with the input file, close and delete it.
        epubold.close()
        if not debug:
            os.unlink(infile)
        #No more need for our workingdirectory, delete it.
        if not debug:
            shutil.rmtree(tmpdir)
        #Add the opendyslexic font files to the output epub zip.
        for font in ["Bold","BoldItalic","Italic","Regular"]:
            filename = "OpenDyslexic-" + font + ".otf"
            source = "/usr/share/fonts/opentype/opendyslexic/" + filename
            target = "fonts/" + filename
            epubnew.write(source,target,zipfile.ZIP_DEFLATED)
        #Output epub is ready, close it.
        epubnew.close()
        #Than open it again so we can feed it to serve_fileobj
        rfil = open(outfile,"r")
        #Create a response containing the output file.
        result = cherrypy.lib.static.serve_fileobj(rfil,disposition='attachment',
                         content_type='.epub',name=outfilename)
        #Once we have the response created, we don't need to keep a copy no more.
        if not debug:
            #FIXME: we don't want to be keeping this, but things currently go wrong if we don't.
            #os.unlink(filename)
            pass
        #Return the converted epub file
        return result
    upload.exposed = True

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 1080,'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(ToOpenDyslexic())
