from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re,os,json

class Doc():
    """
    DOCUMENT CLASS
    """
    def __init__(self):
        
        self.Files    = None
        self.rawSGM   = None
        self.rawAPF   = None
        self.DocId    = None
        self.DocType  = None 
        self.DateTime = None 
        self.Headline = None
        self.Text     = None
        self.Events   = None
    
    def showMentions(self):
        def colorit(t):
            ENDC = '\033[0m'
            colors = ['\033[1;34;41m','\033[1;34;42m','\033[1;34;43m','\033[1;34;44m',
                      '\033[1;34;45m','\033[1;34;46m','\033[1;34;47m','\033[1;34;48m',
                      '\033[1;32;41m','\033[1;32;42m','\033[1;32;43m','\033[1;32;44m',
                      '\033[1;32;45m','\033[1;32;46m','\033[1;32;47m','\033[1;32;48m',
                      '\033[1;33;41m','\033[1;33;42m','\033[1;33;43m','\033[1;33;44m',
                      '\033[1;33;45m','\033[1;33;46m','\033[1;33;47m','\033[1;33;48m',
                      '\033[1;36;41m','\033[1;36;42m','\033[1;36;43m','\033[1;36;44m',
                      '\033[1;36;45m','\033[1;36;46m','\033[1;36;47m','\033[1;36;48m',
                      '\033[1;37;41m','\033[1;37;42m','\033[1;37;43m','\033[1;37;44m',
                      '\033[1;37;45m','\033[1;37;46m','\033[1;37;47m','\033[1;37;48m',
                      '\033[1;30;41m','\033[1;30;42m','\033[1;30;43m','\033[1;30;44m',
                      '\033[1;30;45m','\033[1;30;46m','\033[1;30;47m','\033[1;30;48m',
                      '\033[1;35;41m','\033[1;35;42m','\033[1;35;43m','\033[1;35;44m',
                      '\033[1;35;45m','\033[1;35;46m','\033[1;35;47m','\033[1;35;48m',
                      '\033[1;31;41m','\033[1;31;42m','\033[1;31;43m','\033[1;31;44m',
                      '\033[1;31;45m','\033[1;31;46m','\033[1;31;47m','\033[1;31;48m',
                      '\033[1;31;40m','\033[1;31;40m','\033[1;31;40m','\033[1;31;40m',
                      '\033[1;31;40m','\033[1;31;40m','\033[1;31;40m','\033[1;31;40m']
            
            return f"{colors[t[-1]%8]}{t[1]}{ENDC}"
        
        text = self.rawSGM
        charseqs = []
        for i in range(len(self.Events)):
            event = self.Events[i]
            for mention in event['MENTIONS']:
                charseqs.append([mention['CHARSEQ'],mention['TEXT'],i])

        parts  = []
        lastindex = 0
        charseqs.sort()
        for c in charseqs:
            START,END = c[0][0],c[0][1]
            parts.append(text[lastindex:START-1])
            parts.append(colorit(c))
            lastindex=END
        parts.append(text[lastindex:])
        
        return str(len(self.Events))+'\n'+' '.join(parts).replace('  ',' ').replace('\n ','\n').replace('``','"').replace("''",'"')

class Ace05Parser():
    """
    PARSER CLASS
    """
    def __init__(self,path):
        self.path = path
        self.Docs = []
        
    def groupFiles(self):
        """
        There are 4 files, which has different information, for each document.
        *.ag.xml  :
        *.apf.xml : This file has the annotated entities and events with arguments.
        *.sgm     : This file has the raw text and includes metadata such as; DocID, DocType, Datetime, Headline, Text.
        *.tab     :
        """
        PATH_TO_SOURCES = self.path
        self.ALL_FILES = []
        for source in os.listdir(PATH_TO_SOURCES):
            for file in os.listdir(PATH_TO_SOURCES+source+'/timex2norm/'):
                self.ALL_FILES.append(PATH_TO_SOURCES+source+'/timex2norm/'+file)
                
        self.ALL_FILES.sort()
        self.groupedFiles = [self.ALL_FILES[doc_idx:doc_idx+4] for doc_idx in list(range(len(self.ALL_FILES)))[::4]]            
    
    def parseFiles(self):    
        
        for files in self.groupedFiles:
            
            docObject = Doc()
            docObject.Files = files
            docObject.Events = []
            agxml,apfxml,sgm,tab = files[0],files[1],files[2],files[3]
            
            # SGM Parse
            bs = BeautifulSoup(open(sgm,'r'))
            docObject.rawSGM = bs.text
            apf = open(apfxml,'r').read()
            docObject.rawAPF = apf
            docObject.DocId, docObject.DocType, \
            docObject.Datetime,docObject.Text = [attr.text for attr in bs.find_all(['docid','doctype','datetime','text'])]
            
            # APF.XML Parse
            tree = ET.parse(apfxml)
            root = tree.getroot()
            for event in root.findall('./document/event'):
                EVENT = event.attrib.copy()
                mentions = []
                for mention in event.findall('event_mention'):        
                    mention_ID = mention.attrib['ID']
                    mention_token = mention.find('anchor/charseq')
                    mention_text= mention_token.text
                    mention_charseq = [int(mention_token.attrib['START'])-1,int(mention_token.attrib['END'])]

                    mention_arguments = {}
                    for argument in mention.findall('event_mention_argument'):
                        REFID = argument.attrib['REFID']
                        ROLE = argument.attrib['ROLE']
                        TEXT = argument.find('./extent/charseq').text
                        CHARSEQ = [int(argument.find('./extent/charseq').attrib['START'])-1,int(argument.find('./extent/charseq').attrib['END'])]
                        mention_arguments[ROLE] = {'refid' : REFID, 'role' : ROLE, 'text' : TEXT, 'charseq' : CHARSEQ}
                    if mention_arguments == {}:
                        mention_arguments = None

                    mentions.append({'ID':mention_ID,'TEXT':mention_text,'CHARSEQ':mention_charseq,'ARGUMENTS':mention_arguments})
                EVENT['MENTIONS'] = mentions

                docObject.Events.append(EVENT)
                
            self.Docs.append(docObject)


if __name__ == "__main__":
    parser = Ace05Parser('../dataset/data/English/')
    parser.groupFiles()
    parser.parseFiles()

    
    with open('../dataset/parsed_documents.json','w') as f:
        json.dump([doc.__dict__ for doc in parser.Docs],f)