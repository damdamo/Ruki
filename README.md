# Master Project
-------


## Extracts

First part of project is to extract abstract of publications on the website:  
http://vgibox.eu/repository/index.php/Main_Page  
(Page of all publications: http://vgibox.eu/repository/index.php/Category:Publication)

The script use the api of mediawiki for query:  
https://www.mediawiki.org/wiki/API:Query

We collect all abstract of all publications with different possibility.

## Usage

If you want to use this code it's very simple, you just need to modify
the config file and call the script like this:

``
python3 extract_abstracts.py
``

You can see your file/files fill with abstracts.  
You have some options to complete the collect (with true or false):  
* multiple_file: You can decide to have one abstract per file or just one file with all abstracts
* keywords: Moreover abstracts, you can add keywords that are avaible in the same page of abstract to have more informations
* title: Same as keywords for title
* xml: You can add tags for parsing easier your file. If you want to handle your file(s) differently because the weight of a keyword is not the same that a word.

XML hierarchy:  
* < informations >  
  * < title > ... < /title >  
  * < keyword >keyword_1< /keyword >...<keyword>keyword_n< /keyword >
  * < sentences > ... < /sentences >
* < /informations >
