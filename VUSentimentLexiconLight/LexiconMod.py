import sys
import codecs
import logging
import os
import re
from collections import defaultdict
from lxml import etree

__module_dir = os.path.dirname(__file__)

def load_lexicons(language, path=None):
        if path is None:
            path = __module_dir
        folder_per_lang = {}
        folder_per_lang['nl'] = 'Lexicons/NL-lexicon'
        folder_per_lang['en'] = 'Lexicons/EN-lexicon'
        folder_per_lang['de'] = 'Lexicons/DE-lexicon'
        folder_per_lang['fr'] = 'Lexicons/FR-lexicon'
        folder_per_lang['it'] = 'Lexicons/IT-lexicon'
        folder_per_lang['es'] = 'Lexicons/ES-lexicon'

        config_file = os.path.join(path,folder_per_lang[language],'config.xml')
        
        lexicons_obj = etree.parse(config_file) #pylint: disable=E1101
        lexicons = {}
        default_id = None
        first_id = None
        for lexicon in lexicons_obj.findall('lexicon'):
            this_id = lexicon.get('id')
            if first_id is None: first_id = this_id
            default = (lexicon.get('default','0') == '1')
            if default_id is None and default:
                default_id = this_id
            filename = lexicon.find('filename').text
            description = lexicon.find('description').text
            resource = lexicon.find('resource').text
            lexicons[this_id] = (filename,description,resource)
        if default_id is None: default_id = first_id
        return lexicons,default_id,path,folder_per_lang

def show_lexicons(language, path=None):
    '''Show available lexicons

    Keyword arguments:
    language -- one of 'nl','en','de','fr','it','es'
    path -- specify path if different from package installation (default = None)
    '''
    if path is None:
      path = __module_dir
    lexicons, default_id, this_folder, folder_per_lang = load_lexicons(language, path)
    print('')
    print('#'*30)
    print('Available lexicons for',language)
    for lex_id, (filename, description, resource) in lexicons.items():
        if lex_id == default_id:
            print('  Identifier: "'+lex_id+'" (Default)')
        else:
            print('  Identifier:"'+lex_id+'"')
        print('    Desc:',description.encode('utf-8'))
        print('     Res:',resource.encode('utf-8'))
        print('    File:',os.path.join(this_folder,folder_per_lang[language],filename.encode('utf-8')))
        print('')
    print('#'*30)
    print('')

class LexiconSent:

    def __init__(self,language='nl',lexicon_id=None, path=None):
        if path is None:
          path = os.path.dirname(__file__)

        self.VERSION = '1.0'
        logging.debug('Loading lexicon for '+language)
        self.sentLex = {}
        self.negators = set()
        self.intensifiers = set()
        #self.posOrderIfNone = 'nvar'  ##Order of pos to lookup in case there is Pos in the KAF file
        self.posOrderIfNone = ['noun','prep','verb','adj','adv']
        self.resource = "unknown"

        self.load_resources(language,lexicon_id, path)

        self.spacyMapSet = False

        self.__load_lexicon_xml()

    def load_resources(self,language,my_id=None, path=None):
        if path is None:
          path = os.path.dirname(__file__)
        lexicons, default_id, this_folder, folder_per_lang = load_lexicons(language, path)

        id_to_load = None
        if my_id is None:
            id_to_load = default_id
        else:
            if my_id in lexicons:
                id_to_load = my_id
            else:
                id_to_load = default_id

        self.filename = os.path.join(this_folder,folder_per_lang[language],lexicons[id_to_load][0])
        self.resource = lexicons[id_to_load][1]+" . "+lexicons[id_to_load][2]

    def getResource(self):
        return self.resource

    def __load_lexicon_xml(self):
        logging.debug('Loading lexicon from the file'+self.filename)
        from collections import defaultdict
        d = defaultdict(int)
        tree = etree.parse(self.filename)  #pylint: disable=E1101
        for element in tree.getroot().findall('Lexicon/LexicalEntry'):
            pos = element.get('partOfSpeech','')
            type = element.get('type','')
            short_pos = pos

            type = element.get('type','')
            d[type] += 1
            lemma_ele = element.findall('Lemma')[0]
            lemma = ''
            if lemma_ele is not None:
                lemma = lemma_ele.get('writtenForm')

            sent_ele = element.findall('Sense/Sentiment')[0]
            polarity = strength = '' #pylint: disable=W0612
            if sent_ele is not None:
                #print sent_ele
                polarity = sent_ele.get('polarity','')
                strength = sent_ele.get('strength','')

            if lemma != '':
                if type != '':
                    if type == 'polarityShifter':
                        self.negators.add(lemma)
                    elif type == 'intensifier':
                        self.intensifiers.add(lemma)
                elif polarity != '':
                    self.sentLex[(lemma,short_pos)] = polarity

    def _setSpacyTags(self):
        self.posMap = {
            'ADJ' : 'adj',
            'ADP' : 'prep',
            'ADV' : 'adv',
            'AUX' : 'verb',
            'CONJ' : 'other',
            'CCONJ' : 'other',
            'DET' : 'other',
            'INTJ' : 'adv',
            'NOUN' : 'noun',
            'NUM' : 'none',
            'PART' : 'other',
            'PRON' : 'noun',
            'PROPN' : 'noun',
            'PUNCT' : 'none',
            'SCONJ' : 'other',
            'SYM' : 'none',
            'VERB' : 'verb',
            'X' : 'other',
            'SPACE' : 'none'
        }
        self.spacyMapSet = True

    def isIntensifier(self,lemma):
        '''Return boolean whether lemma is an intensifier'''
        return lemma in self.intensifiers

    def isNegator(self,lemma):
        '''Return boolean whether lemma is a negator'''
        return lemma in self.negators

    def getPolarity(self, lemma, pos, spacyPos = True):
        '''Get polarity of lemma, POS couple
        
        Keyword arguments:
        lemma -- the lemma to be checked
        pos -- part-of-speech tag from the following: 'adj','adv','noun','prep','verb','other'
        spacyPos -- boolean, use spacy POS tag mapping (default = True)
        '''
        if spacyPos:
            if not self.spacyMapSet:
                self._setSpacyTags()
            pos = self.posMap[pos]

        if pos:
            return self.sentLex.get((lemma,pos),'unknown')
        else:
            for newpos in self.posOrderIfNone:
                if (lemma,newpos) in self.sentLex:
                    logging.debug('Found polarify for '+lemma+' with PoS '+newpos)
                    return self.sentLex[(lemma,newpos)]
            return 'unknown'

    def getLemmas(self):
        '''Get all lemmas from the dictionary'''
        for (lemma,pos) in self.sentLex: yield (lemma,pos)
    
    def getDocSentiment(self, lemmas, pos_tags, negatorAction = 'ignoreSent',
     intensifierMultiplier = 2, returnCounts = False, spacyPos = True):
        '''Get sentiment category for a document

        Keyword arguments:
        lemmas  -- Iterable with the lemmas to be checked
        pos_tags -- Iterable with the pos tags corresponding to the lemmas (see getPolarity for more info)
        negatorAction -- Action to take for lemma after negator: 'flip', 'ignoreNeg', 'ignoreSent' (default: 'ignoreSent)
        intensifierMultiplier -- Numeric, multiplier for sentiment words preceded by intensifier
        returnCounts -- Boolean, return document-level counts of positive, negative, negations and intensifiers (default = False)
        spacyPos -- boolean, use spacy POS tag mapping. To be passed to getPolarity (default = True)
        '''

        if len(lemmas) != len(pos_tags):
            raise Exception('The lemmas and POS tags elements do not correspond in terms of length')
        
        docProperties = {
            'numPositive' : 0,
            'numNegative' : 0,
            'numNegPositive' : 0,
            'numNegNegative' : 0,
            'numIntPositive' : 0,
            'numIntNegative' : 0,
            'numNegations' : 0,
            'numIntensifiers' : 0
        }

        previous_negator = False
        previous_intensifier = False

        #Loop over document lemmas + pos tags
        for lemma, pos in zip(lemmas, pos_tags):
            if self.getPolarity(lemma, pos, spacyPos) == 'positive':
                if previous_negator:
                    docProperties['numNegPositive'] += 1
                elif previous_intensifier:
                    docProperties['numIntPositive'] += 1
                else:
                    docProperties['numPositive'] += 1
                previous_intensifier = False
                previous_negator = False
            elif self.getPolarity(lemma, pos, spacyPos) == 'negative':
                if previous_negator:
                    docProperties['numNegNegative'] += 1
                elif previous_intensifier:
                    docProperties['numIntNegative'] += 1
                else:
                    docProperties['numNegative'] += 1
                previous_intensifier = False
                previous_negator = False
            elif self.isNegator(lemma):
                docProperties['numNegations'] += 1
                previous_negator = True
                previous_intensifier = False
            elif self.isIntensifier(lemma):
                docProperties['numIntensifiers'] += 1
                previous_intensifier = True
                previous_negator = False

        totalPositive = docProperties['numPositive'] + intensifierMultiplier*docProperties['numIntPositive']
        totalNegative = docProperties['numNegative'] + intensifierMultiplier*docProperties['numIntNegative']

        if negatorAction == 'flip': #Add negated positives to negative category and vice versa
            totalPositive += docProperties['numNegNegative']
            totalNegative += docProperties['numNegPositive']
        elif negatorAction == 'ignoreNeg': #Ignore negations completely
            totalPositive += docProperties['numNegPositive']
            totalNegative += docProperties['numNegNegative']
        #Third option is to ignore negated words for sentiment counts, hence no block for that

        if totalPositive == 0 and totalNegative == 0:  
            guess='neutral'
        elif totalPositive > totalNegative: 
            guess='positive'
        elif totalPositive < totalNegative: 
            guess='negative'
        elif docProperties['numNegators'] > 0: 
            guess='negative'
        else: 
            guess='neutral'

        if returnCounts:
            return guess, docProperties

        return guess



