# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import re
import codecs

pathOriginal = r".\Defs"
pathTranslation = r".\DefInjected"
pathTranslationOrg = r".\DefInjectedRaws"

tagText = ["label", "rulesStrings", "description", "gerund", "verb", "deathMessage", "pawnsPlural", "fixedName", "gerundLabel", "pawnLabel", "labelShort",
    "labelSocial", "stuffAdjective", "labelMale", "labelFemale", "quotation", "formatString", "skillLabel", "customLabel",
      "text", "name", "summary", "jobString", "letterLabelFriendly", "arrivalTextFriendly", "successfullyRemovedHediffMessage",
      "arrivalTextEnemy", "letterLabelEnemy", "labelMechanoids", "recoveryMessage", "baseInspectLine", "beginLetter", "beginLetterLabel",
      "endMessage", "adjective", "reportString", "letterLabel", "letterText", "graphLabelY", "letter", "oldLabel", "labelSolidTended",
      "labelSolidTendedWell", "labelTendedInner", "labelTendedWellInner", "destroyedLabel", "labelTended", "labelTendedWell",
      "destroyedOutLabel", "destroyedLabel", "discoverLetterText", "discoverLetterLabel", "leaderTitle", "helpTexts", "rulesStrings",
           "instantlyOldLabel", "useLabel", "ingestCommandString", "ingestReportString", "Description", "helpText", "rejectInputMessage", "onMapInstruction"
          ]
allText = {}
allTextValue = {}
allTextExcess = {}
allDefClass = {}
XMLFiles = {}
XMLNewFiles = {}

def addElement(fileXML, elementText, text, nameDef, addTo):
    if("subSounds" not in elementText):
        if(nameDef not in addTo):
            addTo[nameDef] = []
        elementsList = addTo[nameDef]
        if(elementText not in elementsList):
            elementsList.append(elementText)
            allTextValue[elementText] = (text, fileXML)
        
def addClass(className ,defName, parentName, address, text, fileXML, abstract):
    if("subSounds" not in address):
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
        if(subElement.tag in tagText):
            countSubElement = list(subElement)
            if(countSubElement):
                i = 0
                if(tagPath):
                    tagPathSub = tagPath + "." + subElement.tag
                else:
                    tagPathSub = subElement.tag
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
                        address = tagPath + "." + subElement.tag
                    else:
                        address = subElement.tag
                    addClass(className ,nameDef, parentName, address, text, fileXML, abstract)
                if(text and stage == 2):            
                    addElement(fileXML, tagPath + "." + subElement.tag, text, nameDef, allText)
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
                        findText(subElement, (tagPath + "." + subElement.tag)[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
                    else:
                        findText(subElement, (subElement.tag)[:], 0, fileXML, nameDef, stage, className, parentName, abstract)
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
                    print u"\nВозможно надо перевести " + tagPath + u"." + subElement.tag + u" значение:"
                    print text

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
        print u"\nОшибка! Невозможно прочитать xml файл по пути %s, Причина: '%s'"%(path, err.message)
        raise err
    root = tree.getroot()
    for element in root:
        nameElement = element.tag
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
                findXMLORG(subDir)

def findXMLTranslation(path, nameDef):
    listOfDir = os.listdir(path)
    for fileXML in listOfDir:
        if ".xml" in fileXML:
            compare(os.path.join(path, fileXML), nameDef, fileXML)          

def proofFile(path):
    tree = ET.parse(path)
    root = tree.getroot()
    element = root.find("ThoughtDef/stages")
    i = 0
    for sub in element:
        label = sub.find("label")
        print sub.tag == "li"
        print sub.tag
        if(label is not None):
            print label.text
        print i
        i = i + 1
        

def readXMLORG(funcSearch):
    listOfDir = os.listdir(pathOriginal)
    for element in listOfDir:
        sub = os.path.join(pathOriginal, element)
        if os.path.isdir(sub): 
            findXMLORG(sub, funcSearch)

readXMLORG(findAbstract)

def compareVar(addressParent, derivativeVars):
    for derivativeVar in derivativeVars:
        if(derivativeVar[0] == addressParent):
            return derivativeVar
    return None

defineNumber = re.compile("[0-9]+")

def addDerVars(derivativeVarsOrg, nameIndexEnd, numberDer, listOfVars, derivativeVars):
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
                            addDerVars(allDef[derivative][2], nameIndexEnd, numberDer, listOfVars, derivativeVars)
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
                    addDerVars(allDef[derivative][2], nameIndexEnd, numberDer, listOfVars, derivativeVars)
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
                    address = className + "." +element[0]
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
        print u"Внимание! Неожидаемый класс %s в переводе"%nameDef

for key in allText.keys():
    allElement = allText[key]
    if(allElement):
        for element in allElement:
            nameFile = allTextValue[element][1]
            print u"\nВ папке %s у файла %s, отсутствует:"%(key, nameFile),
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
            print u"%s значение: %s"%(element, allTextValue[element][0])

for key in allTextExcess.keys():
    print u"\nВ файле %s, не существующие переменные в defs:"%key
    allElement = allTextExcess[key]
    for element in allElement:
        print u"%s"%element

txt = codecs.open("Result.txt", "w", "utf-8")
txt.write(u'\ufeff')
for defName in allText:
    if(allText[defName]):
        txt.write(u"В папке %s:\n"%defName)
    for var in allText[defName]:
        txt.write(u"\tТребуется перевести: %s\n"%allTextValue[var][0])
txt.close()
