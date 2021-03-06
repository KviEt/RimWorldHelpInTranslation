# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import re
import codecs

class CParser(ET.XMLTreeBuilder):
   def __init__(self, html=0, target=None, encoding=None):
       ET.XMLTreeBuilder.__init__(self, html=0, target=None, encoding=None)
       # assumes ElementTree 1.3.0
       self._parser.CommentHandler = self.handle_comment

   def handle_comment(self, data):
       self._target.start(ET.Comment, {})
       self._target.data(data)
       self._target.end(ET.Comment)

pathOriginal = r".\Defs"
pathTranslation = r".\DefInjected"
pathTranslationOrg = r".\DefInjectedRaws"

#tagText is list of label which shoud be translated.
tagText = ["label", "rulesStrings", "description", "gerund", "verb", "deathMessage", "pawnsPlural", "fixedName", "gerundLabel", "pawnLabel", "labelShort",
    "labelSocial", "stuffAdjective", "labelMale", "labelFemale", "quotation", "formatString", "skillLabel", "customLabel",
      "text", "name", "summary", "jobString", "letterLabelFriendly", "arrivalTextFriendly", "successfullyRemovedHediffMessage",
      "arrivalTextEnemy", "letterLabelEnemy", "labelMechanoids", "recoveryMessage", "baseInspectLine", "beginLetter", "beginLetterLabel",
      "endMessage", "adjective", "reportString", "letterLabel", "letterText", "graphLabelY", "letter", "oldLabel", "labelSolidTended",
      "labelSolidTendedWell", "labelTendedInner", "labelTendedWellInner", "destroyedLabel", "labelTended", "labelTendedWell",
      "destroyedOutLabel", "destroyedLabel", "discoverLetterText", "discoverLetterLabel", "leaderTitle", "helpTexts", "rulesStrings",
           "instantlyOldLabel", "useLabel", "ingestCommandString", "ingestReportString", "helpText", "rejectInputMessage", "onMapInstruction"
          ]
allText = {}
allTextValue = {}
allTextExcess = {}
allDefClass = {}
XMLFiles = {}
XMLNewFiles = {}
outMissedResult = {}
outPerhaps = []
outWarning = []
outAbsent = []

def addElement(fileXML, elementText, text, nameDef, addTo):
    if("subsounds" not in elementText.lower()):
        if(nameDef not in addTo):
            addTo[nameDef] = []
        elementsList = addTo[nameDef]
        if(elementText not in elementsList):
            elementsList.append(elementText)
            allTextValue[elementText] = (text, fileXML)
        
def addClass(className ,defName, parentName, address, text, fileXML, abstract):
    if("subsounds" not in address.lower()):
        if(defName not in allDefClass):
            allDefClass[defName] = {}
        allDef = allDefClass[defName]
        if(className not in allDef):
            if(abstract):
                abstract = True
            allDef[className] = (abstract, parentName, [])
        allDef[className][2].append([address, text, fileXML])

def findText(element, tagPath, li, fileXML, nameDef, stage, className, parentName, abstract):
    for subElement in element:
        label = subElement.tag.lower()
        if(label in tagText):
            countSubElement = list(subElement)
            if(countSubElement):
                i = 0
                if(tagPath):
                    tagPathSub = tagPath + "." + label
                else:
                    tagPathSub = label
                for sub2Element in subElement:
                    text = sub2Element.text
                    if(stage == 1):
                        addClass(className ,nameDef, parentName, tagPathSub + "." + str(i), text, fileXML, abstract)
                    else:
                        if(text and stage == 2):
                            addElement(fileXML, tagPathSub + "." + str(i), text, nameDef, allText)
                    i = i + 1
            else:
                text = subElement.text
                if(stage == 1):
                    if(tagPath):
                        address = tagPath + "." + label
                    else:
                        address = label
                    addClass(className ,nameDef, parentName, address, text, fileXML, abstract)
                if(text and stage == 2):            
                    addElement(fileXML, tagPath + "." + label, text, nameDef, allText)
        else:
            listElement = list(subElement)
            isli = subElement.tag == "li"
            if(isli):
                if(stage == 1):
                    if(tagPath):
                        addClass(className ,nameDef, parentName, tagPath + "." + str(li), None, fileXML, abstract)
                    else:
                        addClass(className ,nameDef, parentName, (str(li))[:], None, fileXML, abstract)
            if(listElement):
                if(isli):
                    if(tagPath):
                        findText(subElement, (tagPath + "." + str(li))[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
                    else:
                        findText(subElement, (str(li))[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
                else:
                    if(tagPath):
                        findText(subElement, (tagPath + "." + label)[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
                    else:
                        findText(subElement, (label)[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
            if(isli):
                li = li + 1
            text = subElement.text
            if(stage == 1):
                if(nameDef not in allDefClass or className not in allDefClass[nameDef]):
                    addClass(className ,nameDef, parentName, "", None, fileXML, abstract)
            if(text):
                expectSTR = re.compile(u"[aA-zZ]+[ \t]+[aA-zZ]")
                result = expectSTR.match(text)
                if(not result):
                    expectSTR = re.compile(u"[a-z]+")
                    result = expectSTR.match(text)
                if(result and text != u"false" and text != u"true"):
                    if(tagPath):
                        outPerhaps.append(u"\n\nPerhaps %s necessary to translate"%(tagPath + u"." + subElement.tag) + u", text: %s\n"%text)
                    else:
                        outPerhaps.append(u"\n\nPerhaps %s necessary to translate"%("None" + u"." + subElement.tag) + u", text: %s\n"%text)

def findDef(root, fileXML):
    for element in root:
        name = element.tag
        if(name[-3:] == u"Def" and name != u"SongDef"):
            abstract = element.get("Abstract")
            if(abstract is None):
                abstract = element.get("abstract")
            parent = element.get("ParentName")
            if(not parent):
                parentName = element.get("parentName")
            if(not abstract and not parent):
                defName = element.find("defName")
                if(defName is None):
                    defName = element.find("DefName")
                if(defName is not None):
                    tagPath = defName.text
                    parent = element.get("ParentName")
                    if(parent):
                        findText(element, tagPath, 0, fileXML, name, 2, None, None, None)
                    else:
                        findText(element, tagPath, 0, fileXML, name, 2, None, None, None)
        else:
            findDef(element, fileXML)

def findAbstract(root, fileXML):
    for element in root:
        name = element.tag
        if(name[-3:] == u"Def" and name != u"SongDef"):
            className = None
            abstract = element.get("Abstract")
            if(abstract is None):
                abstract = element.get("abstract")
            if(abstract):
                className = element.get("Name")
                if(className is None):
                    className = element.get("name")
                if(className is None):
                    continue
            else:
                defName = element.find("defName")
                if(defName is None):
                    defName = element.find("DefName")
                if(defName is None):
                    continue
                else:
                    className = defName.text
            parentName = element.get("ParentName")
            if(not parentName):
                parentName = element.get("parentName")
            if(abstract or parentName):
                findText(element, None, 0, fileXML, name, 1, className, parentName, abstract)
        else:
            findAbstract(element, fileXML)

def gather(path, fileXML, funcSearch):
    tree = ET.parse(path)
    root = tree.getroot()
    funcSearch(root, fileXML)
    
def compare(path, nameDef, fileXML):
    try:
        tree = ET.parse(path)
    except ParseError as err:
        print u"\nError! Can't read xml file, path: %s, Reason: '%s'"%(path, err.message)
        raise err
    root = tree.getroot()
    for element in root:
        defName = re.compile(u"[aA-zZ]+")
        result = defName.match(element.tag)
        if(not result):
            print u"Warning! defName can't be empty"
            continue
        defNameTag = result.group(0)
        countSymbol = len(defNameTag)
        nameElement = element.tag[:countSymbol] + element.tag[countSymbol:].lower()
        if(nameElement in allText[nameDef]):
            allText[nameDef].remove(nameElement)
        else:
            if(fileXML not in allTextExcess):
                allTextExcess[fileXML] = []
            allTextExcess[fileXML].append(nameElement)
    
def findXMLORG(path, funcSearch):
    listOfDir = os.listdir(path)
    for fileXML in listOfDir:
        if ".xml" in fileXML:
            (head, tail) = os.path.split(path)
            gather(os.path.join(path, fileXML), fileXML, funcSearch)
        else:
            subDir = os.path.join(path, fileXML)
            if os.path.isdir(subDir):
                findXMLORG(subDir, funcSearch)

def findXMLTranslation(path, nameDef):
    listOfDir = os.listdir(path)
    for fileXML in listOfDir:
        if ".xml" in fileXML:
            compare(os.path.join(path, fileXML), nameDef, fileXML)          

def readXMLORG(funcSearch):
    listOfDir = os.listdir(pathOriginal)
    for element in listOfDir:
        sub = os.path.join(pathOriginal, element)
        if os.path.isdir(sub): 
            findXMLORG(sub, funcSearch)

def compareVar(addressParent, derivativeVars):
    for derivativeVar in derivativeVars:
        if(derivativeVar[0] == addressParent):
            return derivativeVar
    return None

def addDerVars(derivativeVarsOrg, nameIndexEnd, numberDer, listOfVars, derivativeVars, nameOfList, defineNumber):
    numberDerOrgExpect = 0
    for derivativeVarOrg in derivativeVarsOrg:
        if(nameOfList == derivativeVarOrg[0][:nameIndexEnd]):
            numberMatch = defineNumber.search(derivativeVarOrg[0])
            numberDerOrg = numberMatch.group(0)
            countSymbolNumberOrg = len(numberDerOrg)
            numberDerOrg = int(numberDerOrg)
            if(numberDerOrg != numberDerOrgExpect):
                numberDer = int(numberDer) + 1
                numberDerOrgExpect = numberDerOrgExpect + 1
            derivativeVarResult = derivativeVarOrg[:]
            derivativeVarResult[0] = derivativeVarResult[0][:nameIndexEnd]+str(numberDer)+derivativeVarResult[0][(nameIndexEnd+countSymbolNumberOrg):]
            listOfVars.append(derivativeVarResult)
            derivativeVar = compareVar(derivativeVarOrg[0], derivativeVars)
            derivativeVars.remove(derivativeVar)

def writingOutFile(outFile, outList):
   for strOut in outList:
      outFile.write(strOut)

def main():
    
    if(not os.path.exists(pathOriginal)):
        print "Defs folder is necessary for execution of program."
        return None

    if(not os.path.exists(pathTranslation)):
        print "Defs folder is necessary for execution of program."
        return None

    i = 0
    countTags = len(tagText)
    while(i < countTags):
        tagText[i] = tagText[i].lower()
        i = i + 1

    readXMLORG(findAbstract)

    defineNumber = re.compile("[0-9]+")

    for defName in allDefClass:
        allDef = allDefClass[defName]
        for className in allDef:
            if(not allDef[className][0]):
                relations = [className]
                parent = allDef[className][1]
                while(parent):
                    relations.append(parent)
                    if(parent in allDef):
                        parent = allDef[parent][1]
                    else:
                        parent = None
                relations.reverse()
                listOfVars = []
                countOfParents = len(relations)
                while(countOfParents != 1):
                    parent = relations[0]
                    derivative = relations[1]
                    derivativeVars = allDef[derivative][2][:]
                    nameOfList = None
                    nameIndexEnd = None
                    numberDer = None
                    if(listOfVars):
                        parentList = listOfVars[:]
                    else:
                        if(parent in allDef):
                            parentList = allDef[parent][2]
                        else:
                            parentList = []
                    for parentVar in parentList:
                        if(nameOfList and nameIndexEnd):
                            if(nameOfList == parentVar[0][:nameIndexEnd]):
                                numberMatch = defineNumber.search(parentVar[0])
                                numberDer = numberMatch.group(0)
                                exists = compareVar(parentVar[0], listOfVars)
                                if(not exists):
                                    listOfVars.append(parentVar)
                                continue
                            else:
                                addDerVars(allDef[derivative][2], nameIndexEnd, numberDer, listOfVars, derivativeVars, nameOfList, defineNumber)
                                nameOfList = None
                                nameIndexEnd = None
                                numberDer = None
                        derivativeVar = compareVar(parentVar[0], derivativeVars)
                        if(derivativeVar):
                            addressDerivative = derivativeVar[0]
                            numberMatch = defineNumber.search(addressDerivative)
                            if(numberMatch):
                                numberDer = numberMatch.group(0)
                                numberIndexEnd = numberMatch.end(0)
                                nameIndexEnd = numberIndexEnd - len(numberDer)
                                nameOfList = parentVar[0][:nameIndexEnd]
                                listOfVars.append(parentVar)
                                numberDer = int(numberDer) + 1
                            else:
                                listOfVars.append(derivativeVar)
                                derivativeVars.remove(derivativeVar)
                                if(parentVar in listOfVars):
                                    listOfVars.remove(parentVar)
                        else:
                            exists = compareVar(parentVar[0], listOfVars)
                            if(not exists):
                                listOfVars.append(parentVar)
                    if(nameOfList):
                        addDerVars(allDef[derivative][2], nameIndexEnd, numberDer, listOfVars, derivativeVars, nameOfList, defineNumber)
                    for additionVar in derivativeVars:
                        listOfVars.append(additionVar)
                    relations.pop(0)
                    countOfParents = len(relations)
                if(defName not in allText):
                    allText[defName] = []
                elementList = allText[defName]
                fileXML = allDef[className][2][0][2]
                for element in listOfVars:
                    if(element[1]):
                        address = className + "." + element[0].lower()
                        elementList.append(address) 
                        allTextValue[address] = (element[1], fileXML)

    readXMLORG(findDef)

    listOfDir = os.listdir(pathTranslation)
    for nameDef in listOfDir:
        notExpected = True
        if(nameDef in allText):
            notExpected = False
            sub = os.path.join(pathTranslation, nameDef)
            if os.path.isdir(sub): 
                findXMLTranslation(sub, nameDef)
        if((nameDef[-1] == 's' or nameDef[-1] == 'S') and nameDef[:-1] in allText):
            notExpected = False
            sub = os.path.join(pathTranslation, nameDef)
            nameDef = nameDef[:-1]
            if os.path.isdir(sub): 
                findXMLTranslation(sub, nameDef)
        if(notExpected):
            outWarning.append(u"\nWarning! Not expected %s folder in DefInjected folder\n"%nameDef)

    for key in allText.keys():
        allElement = allText[key]
        if(allElement):
            if(key not in outMissedResult):
               outMissedResult[key] = {}
            for element in allElement:
                nameFile = allTextValue[element][1]
                if(nameFile not in outMissedResult[key]):
                   outMissedResult[key][nameFile] = []
                path = os.path.join(pathTranslation, key)
                if(not os.path.exists(path)):
                    path = os.path.join(pathTranslation, key+'s')
                XMLPath = os.path.join(path, nameFile)
                if(os.path.isfile(XMLPath)):
                    if(key not in XMLFiles):
                        XMLFiles[key] = {}
                    XMLFiles[key][nameFile] = os.path.join(path, nameFile)
                if(key not in XMLNewFiles):
                    XMLNewFiles[key] = {}
                if(nameFile not in XMLNewFiles[key]):
                    XMLNewFiles[key][nameFile] = []
                XMLNewFiles[key][nameFile].append(element)
                outMissedResult[key][nameFile].append(u"\n\n\n%s with text:\n\t%s\n"%(element, allTextValue[element][0]))

    for key in allTextExcess.keys():
        outAbsent.append(u"\n\n%s file have labels which absent in Defs folder:\n"%key)
        allElement = allTextExcess[key]
        for element in allElement:
            outAbsent.append(u"\n\t%s\n"%element)

    for defName in XMLNewFiles.keys():
        for nameFile in XMLNewFiles[defName].keys():
            if(defName in XMLFiles and nameFile in XMLFiles[defName]):
                XMLPath = XMLFiles[defName][nameFile]
                XMLParser = CParser(encoding='utf-8')
                tree = ET.parse(XMLPath, XMLParser)
                root = tree.getroot()
            else:
                tree = ET.ElementTree()
                newRoot = ET.Element(u"LanguageData")
                tree._setroot(newRoot)
                root = tree.getroot()
            for element in XMLNewFiles[defName][nameFile]:
                subElement = ET.SubElement(root, element)
                subElement.text = allTextValue[element][0]
            XMLNewPath = os.path.join(pathTranslationOrg, defName)
            if(not os.path.exists(XMLNewPath)):
                os.makedirs(XMLNewPath)
            XMLNewPath = os.path.join(XMLNewPath, nameFile)
            xml = codecs.open(XMLNewPath, "w", "utf-8")
            xml.write(u'\ufeff')
            xml.write(u"<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
            xml.write(u"<%s>\n"%root.tag)
            for element in root:
                tag = element.tag
                if(tag is ET.Comment):
                   xml.write(u"\n\t<!--")
                else:
                   xml.write(u"\n\t<%s>"%tag)
                xml.write(element.text)
                if(tag is ET.Comment):
                   xml.write(u"-->\n")
                else:
                   xml.write(u"</%s>\n"%tag)
            xml.write(u"\n</%s>\n"%root.tag)
            xml.close()

    outDoc = codecs.open("Result.doc", "w", "utf-8")
    outDoc.write(u'\ufeff')
    writingOutFile(outDoc, outPerhaps)
    writingOutFile(outDoc, outWarning)
    for defName in outMissedResult:
       outDoc.write(u"\n\n=========================================================================")
       outDoc.write(u"\nIn %s folder:"%defName)
       for nameFile in outMissedResult[defName]:
          outDoc.write(u"\n\n-------------------------------------------------------------------------")
          outDoc.write(u"\nAt %s file:\n"%nameFile)
          writingOutFile(outDoc, outMissedResult[defName][nameFile])
          outDoc.write(u"\n-------------------------------------------------------------------------")
       outDoc.write(u"\n=========================================================================")
    writingOutFile(outDoc, outAbsent)
    outDoc.close()

if __name__ == "__main__":
    main()
