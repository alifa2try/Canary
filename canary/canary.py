# Imports
from nltk.tokenize import sent_tokenize, word_tokenize
from gensim import downloader as data
import json
import sys
import os
import random

def canaryPreprocessing(file, type):
    """ Used to pre-process an input file to order to efficient produce results. """
    
    # Pre-processes an Input file
    if type == "text":
        # User file imported, converted to lowercase and case ignored (NEED TO ADD CASE IGNORE)
        userFile = open(file).read().lower()
        # Tokenizing userFile into sentences, also removes Whitespace/Breaks
        sentenceTokens = sent_tokenize(userFile)
        return sentenceTokens
    # Pre-procosses an Argumentative Component
    elif type == "component":
        # Reading in stopWords.json
        with open("stopwords.json") as stopWordsFile:
            sWords = json.load(stopWordsFile)

             # Used to store Stopwords
            stopWords = []

            # Looping through JSON file to add to list
            for i in xrange(0, len(sWords["stopwords"])):
                stopWords.append(str(sWords["stopwords"][i]))

        # Tokenization (should switch to wordtokenizer by NLTK?)
        tokens = file.lower().split()
        # Removing Stop words
        tokens = [w for w in tokens if w not in stopWords]
        return tokens
    else:
        print("SEE DOCUMENTATION FOR CORRECT USAGES")


def canaryLocal(file):
    """ Finds Argumentative Components in a local file """

    # Store Components
    claim = []
    majorClaim = []
    premise = []
    components = []

    # Importing Indicators via "indicators.json"
    with open("indicators.json") as indicatorsFile:
        indicators = json.load(indicatorsFile)

        # Store Indicators in their respective lists
        claimIndicators = []
        majorClaimIndicators = []
        premiseIndicators = []

        # Looping through JSON file to add Indicators to their respective lists
        for i in xrange(0, len(indicators["indicators"])):
            # Claim
            for i in range(len(indicators["indicators"][i]["claim"])):
                claimIndicators.append(str(indicators["indicators"][0]["claim"][i]))
            i = 0
            # Major
            for i in range(len(indicators["indicators"][i]["major"])):
                majorClaimIndicators.append(str(indicators["indicators"][0]["major"][i]))
            i = 0
            # Premise
            for i in range(len(indicators["indicators"][i]["premise"])):
                premiseIndicators.append(str(indicators["indicators"][0]["premise"][i]))
            i = 0
        
        # Importing and pre-processing the User's input file
        sentenceTokens = canaryPreprocessing(file, "text")

        # Looping through userFile Tokens (sentences)
        for line in xrange(0, len(sentenceTokens)):
            # Claim Indicators loop
            for i in range(len(claimIndicators)):
                if (" " + claimIndicators[i] + " ") in (" " + sentenceTokens[line] + " "):
                    # Store current Component
                    claimComponent = str(sentenceTokens[line])
                    # Check to see if Component is already in list
                    if claimComponent not in str(claim):
                        # Add to found claims
                        claim.append(claimComponent)

            # Major Indicators loop
            for i in range(len(majorClaimIndicators)):
                # Indicator found in a given sentence
                if (" " + majorClaimIndicators[i] + " ") in (" " + sentenceTokens[line] + " "):
                    # Store current Component
                    claimMajorComponent = str(sentenceTokens[line])
                    # Check to see if Component is already in list
                    if claimMajorComponent not in str(majorClaim):
                        # Add to found claims
                        majorClaim.append(claimMajorComponent)

            # Premise Indicators loop
            for i in range(len(premiseIndicators)):
                # Indicator found in a given sentence
                if (" " + premiseIndicators[i] + " ") in (" " + sentenceTokens[line] + " "):
                    # Store current Component
                    premiseComponent = str(sentenceTokens[line])
                    # Check to see if Component is already in list
                    if premiseComponent not in str(premise):
                        # Add to found claims
                        premise.append(premiseComponent)

    # All components add to a list to be returned/re-used in other functions
    components.append(majorClaim)
    components.append(claim)
    components.append(premise)
    return components

def canaryRelations(claims, premises):
    """ Finds Argumentative Relations from a list of Claims/Premises """

    # Store Relations
    relations = []
    # Stores used premises
    usedPremises = []
    # Stores used claims
    leftoverPremises = []
    
    # Inputting pre-trained data from Wikipedia 2014+ (word-vectors)
    wordVectors = data.load("glove-wiki-gigaword-100")
    
    # Attempt Three
    for claim in claims:
        # Pre-processing each claim in order to efficiently compare it against a premise
        claimTokens = canaryPreprocessing(claim, "component")
        # Stores comparisons between a given premise and claims
        comparisons = []
        for premise in premises:
            if premise not in usedPremises:
                # Pre-processing each premise in order to efficiently compare it against a given claim
                premiseTokens = canaryPreprocessing(premise, "component")
                # Comparing how similar a given claim is to a premise (Calcuted via WMD)
                similarity = wordVectors.wmdistance(claimTokens, premiseTokens)
                # Adding each comparison to a list
                comparisons.append([str(claim), str(premise), similarity])
                # Used as a benchmark
                answer = comparisons[0]

        # Looping through the results for a give claim
        for item in comparisons:
            if item[2] < answer[2]:
                answer = item
        # Adding premise to used list
        usedPremises.append(answer[1])
        
        # Adding Components and their similarity to relations (list)
        relations.append([str(answer[0]), str(answer[1]), answer[2]])
    
    # Creating a new list to store premises that have not been used the first time round
    for premise in premises:
        if premise not in usedPremises:
            leftoverPremises.append(premise)
    
    # Attempt Two
    for leftoverPremise in leftoverPremises:
        # Check to see if it hasn't already been assigned (linked to a claim)
        if leftoverPremise not in usedPremises:
            # Pre-processing each premise in order to efficiently compare it against a given claim
            premiseTokens = canaryPreprocessing(leftoverPremise, "component")
            # Stores comparisons between a given premise and claims
            comparisons = []
            for claim in claims:
                # Pre-processing each claim in order to efficiently compare it against a premise
                claimTokens = canaryPreprocessing(claim, "component")
                # Comparing how similar a given claim is to a premise (Calcuted via WMD)
                similarity = wordVectors.wmdistance(claimTokens, premiseTokens)
                # Adding each comparison to a list
                comparisons.append([str(claim), str(leftoverPremise), similarity])
                # Used as a benchmark
                answer = comparisons[0]
            
        # Was having problems when we don't find any claims, quick solution
        if len(claims) != 0:
            # Looping through the results for a give claim
            for item in comparisons:
                if item[2] < answer[2]:
                    answer = item
            # Adding premise to used list
            usedPremises.append(answer[1])
            # Adding Components and their similarity to relations (list)
            relations.append([str(answer[0]), str(answer[1]), answer[2]])
    
    # Returning a list of Claims, supported by a given premise and their similartity score
    return relations

def canarySupports():
    """ Able to find what Claims support or oppose the given topic """
    print("CANARY SUPPORTS")

def canarySADFace(relations):
    """ Function used to output found Components and Relations in SADFace format """
    
    # Reading in JSON SADFace Template
    with open('./canarySADFace.json') as jsonFile:
        SADFace = json.load(jsonFile)

    # Need to loop through canaryRelations output and find out what premises are linked to what claims
    
    for relation in relations:
        # Randomly generate id's for each component
        id = random.randint(1, 1000)
        claimId = random.randint(1, 1000)
        premiseId = random.randint(1, 1000)

        # Creating a node for claim
        SADFace['nodes'].append({
            "id": str(claimId), 
            "metadata": {}, 
            "sources": [], 
            "text": str(relation[0]), 
            "type": "atom"
        })
        
        # Creating a node for premise
        SADFace['nodes'].append({
            "id": str(premiseId), 
            "metadata": {}, 
            "sources": [], 
            "text": str(relation[1]), 
            "type": "atom"
        })
        # Need to link the above elements
        SADFace['edges'].append({
            "id": str(id), 
            "source_id": str(premiseId), 
            "target_id": str(claimId)
        })

    # Outputting changes to JSON file
    with open('./canarySADFace.json', 'w') as f:
        json.dump(SADFace, f, indent=4)

def canarySADFaceLibrary(relations):
    print("NEED TO IMPORT LIBRARY")

    
if __name__ == "__main__":
    """ Used for testing the various functions """

    # Finding Components via Canary
    canary = canaryLocal(".././corpus/essay001.txt")  
    
    # Major
    canaryMajor = canary[0]
    # Claim
    canaryClaims = canary[1]
    # Premise
    canaryPremises = canary[2]
    """
    for claims in canaryClaims:
        print("Claims:")
        print(claims)
        print("\n")

    for premises in canaryPremises:
        print("Premises:")
        print(premises)
        print("\n")
    """
    # Finding Relations between Components
    relations = canaryRelations(canaryClaims, canaryPremises)

    # Test print
    for relation in relations:
        print("Relation:" + "\n")
        print("Claim: " + str(relation[0]))
        print("Premise: " + str(relation[1]))
        print("Similarity: " + str(relation[2]))
        print("\n")

    canarySADFace(relations)
    

    
    