# epub2opendyslexic
Simple python web server for converting Smashwords epub files to an  OpenDyslexic release of the same book.
It might work for other epubs, but it wasn't written for or tested for anyting else than epubs that were generated 
by the smashwords MeatGrinder.

So who is this for? Its for people who:

* Are cognitively impaired and would like to read epub e-books using the OpenDyslexic font.
* Don't own a Kobo reader (that comes with OpenDyslexic already loaded)
* Don't own a device that allows for easy installation of custom fonts.
* Do have a reader or tablet with an App (like Google Play Books) that while not supporting custom installation of fonts, does respect epub-embeded fonts when used inside of the epub cascading stylesheet definition.

So what does it do:
* Embed the OpenDyslexic fonts into the epub file.
* Make the epub file use the embedded OpenDyslexic font.
* Make sure the base line-height is at least 130%
* Make sure the base font size is at least 1.125em
* Update the embedded cover art to show its an OpenDyslexic version.
* If a full-size cover-art jpeg is submitter instead of an epub: update it to show its an OpenDyslexic version. (This last one is meant purely for Smashwords authors who want to resubmit the converted epub to Smashwords using the updated cover art image.

Most of the time I have the latest beta of this server tunning on a VM on my home PC. Its not on 24/7, but its on pretty often, 
so if you have any epubs from smashwords published authors, please give it a try:

http://timelord-ninja.xs4all.nl/

If you are a SmashWords published author and would like to make an OpenDyslexic version of your book available, 
and you want an updated copyright notice for your OpenDyslexic-release, drop me a message if you want the 
copyright notice to read:  

    This version of this eBook is made available at zero cost in support 
    of people with cognitive disabilities who don't own a reading device 
    with support for system wide custom fonts. This eBook is a tuned version 
    of the regular edition made to use a 18 point font with at least 130% 
    line-height that has been tuned to use the OpenDyslexic font on readers 
    and devices that support custom fonts. FBReader and Androids Play Books 
    are examples of applications that don't support system wide custom fonts 
    but do support embedded custom fonts in eBooks. If you don't suffer from
    cognitive disabilities than please return to smashwords and purchase the
    regular edition of this eBook. If you plan to read this eBook on a device
    or application that supports system wide installation of custom fonts, 
    than also please return to smashwords and purchase the regular edition of 
    this eBook.

At the moment the copyright update requires manual work that I would be happy to do for you.

Currently this is a one man sparetime project and I don't have much time for extensive testing.
If you run into any issues or have any sugestions or even would like to offer a bit of help with
getting the CSS patches tuned a bit better or by cleaning up my python code, than please drop me
a message at rob@timelord.ninja .
