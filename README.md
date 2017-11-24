# RUKI: Reconciliation and unification for knowledge information
-------


## Extracts

First part of project is to extract abstract of publications on the website:  
http://vgibox.eu/repository/index.php/Main_Page  
(Page of all publications: http://vgibox.eu/repository/index.php/Category:Publication)

The script use the api of mediawiki for query:  
https://www.mediawiki.org/wiki/API:Query

We collect all abstract of all publications with different possibility.

### Usage

If you want to use this code it's very simple, you just need to modify
the config file and call the script like this:

``
python3 extract_abstracts.py
``

You can see your file/files fill with abstracts.  

### Configuration

This is an configuration example of what you have:

```yaml
url: 'http://vgibox.eu/repository/api.php'

# Parameters to have id list
# continue is just to silence the warning

parameters_id:
  action: 'query'
  format: 'json'
  list: 'categorymembers'
  # cmtitle: 'Category:VGI_Domain'
  cmtitle: 'Category:Publication'
  continue: ''

# Paramaters to extract content of a page
parameters_extract_content:
  action: 'query'
  format: 'json'
  prop: 'revisions'
  rvprop: 'content'

output:
  file: 'Results/Extracts/Single/abstracts'
  folder: 'Results/Extracts/Multiple/'

options:
  multiple_file: true
  xml: false
  keywords: false
  title: false

```

You have some options to complete the collect (with true or false):  
* multiple_file: You can decide to have one abstract per file or just one file with all abstracts
* id: Can print id of the document on the website 
* keywords: Moreover abstracts, you can add keywords that are avaible in the same page of abstract to have more informations
* title: Same as keywords for title
* xml: You can add tags for parsing easier your file. If you want to handle your file(s) differently because the weight of a keyword is not the same that a word.

XML hierarchy:  
* < informations >  
  * < id > ... < /id >
  * < title > ... < /title >  
  * < keyword >keyword_1< /keyword >...<keyword>keyword_n< /keyword >
  * < sentences > ... < /sentences >
* < /informations >

Normally, you just need to modify 'output' and 'options'.

## OWL in python3

For this part we use [Owlready2](https://pypi.python.org/pypi/Owlready2) / [Nltk](http://www.nltk.org/)  
When nltk is downloaded launch ntlk with python3
```bash
import nltk
nltk.download()
```
It's open a window where we can choose different module for installation.
You have to go in "Corpora" and install "stopwords".
