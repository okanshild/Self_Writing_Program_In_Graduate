def printHelpInfo():
	print("""
Useful: 
		
	python PseAAC.py -t 1/2 -w 0.05 -r 100 -i inputFilename -o outputFilename

  parameter description:

	-t: The type of PseAAC. 1 -> Type 1 PseAAC[default]; 
							2 -> Type 2 PseAAC.(Only this)

	-w: The weight factor for the sequence order effect and used to put weight to the additional pseudo nucleic acid components with respect to the conventional nucleic acid components. The users are allowed to select the weight factor from 0.1 to 1.0 . The default is 0.5.

	-r: It represents the counted rank (or tier) of the correlation along a protein sequence. It must be non-Negative integer and smaller than L-1. 

	-i: The input filename. (required)

	-o: The output filename. (required)

		""")
	exit(0)

def detectingPythonVersionAndOutputHelpInfo():
	if sys.version[0] == '2':
		print("""\nVersionError: The current python version: '%s',
		You must use python version 3 or later to run this script!\n"""%((sys.version).split('\n')[0]))
		exit(0)
	else:
		pass

	try:
		if sys.argv[1] == "--help":
			printHelpInfo()
		else:
			pass
	except:
		printHelpInfo()

def obtainExternalParameters():
	try:
		if sys.argv[1] == "-t":
			typeOfPseAAC = int(sys.argv[2])
		else:
			assert 0
		if sys.argv[3] == "-w":
			weightFactor = float(sys.argv[4])
		else:
			assert 0
		if sys.argv[5] == "-r":
			lambdaPara = int(sys.argv[6])
		else:
			assert 0
		if sys.argv[7] == "-i":
			in_filename = sys.argv[8]
		else:
			assert 0
		if sys.argv[9] == "-o":
			out_filename = sys.argv[10]
		else:
			assert 0
	except:
			printHelpInfo()
	return typeOfPseAAC, weightFactor, lambdaPara, in_filename, out_filename


def detectingTheRationalityOfLambdaPara(in_file, lambdaPara):
	seqLens = []

	f = open(in_file)
	for eachline in f:
		if eachline[0] == ">":
			pass
		else:
			seqLens.append(len(eachline.strip('\n')))

	seqMinLen = min(seqLens)
	if lambdaPara > (seqMinLen-1):
		print("Parameter Error : The Lambda Parameter must samller than L-1!")
		exit(0)




def obtainAminoAcidPhysicoChemicalDict(filename):
	phychemdict = dict()
	phyChemList = []

	count_line = 0
	f = open(filename)
	for eachline in f:
		count_line += 1
		temp = eachline.strip().split("\t")
		if count_line == 1:
			aminoAcid = temp[1:]
		else:
			phyChemList.append(temp[0])
			phychemdict[temp[0]] = dict()
			count_num = 0
			for each in temp[1:]:
				count_num += 1
				phychemdict[temp[0]][aminoAcid[count_num-1]] = float(each)
	f.close()

	return phychemdict, aminoAcid, phyChemList


def generateCsvFormatLinebyType1PseAAC(in_file, out_file, weightFact, lambdaPara, phyChemDict, aminoAcid, phyChemList):
	pass


def generateCsvFormatNoteLineType2(lambdaPara, aminoAcid, phyChemList):
	noteLine = 'class'
	for eachAA in aminoAcid:
		noteLine += ",%s_f"%(eachAA)

	for i in range(lambdaPara):
		for eachName in phyChemList:
			noteLine += ",%s_%d"%(eachName,(i+1))
	return noteLine+'\n'

def calculateOccurenceFrequencyOfAminoAcid(sequence, aminoAcid):
	occurfrequency = dict()
	seqLen = len(sequence)
	for each in aminoAcid:
		eachCount = sequence.count(each)
		if eachCount == 0:
			occurfrequency[each] = 0
		else:
			occurfrequency[each] = eachCount/seqLen
	
	return occurfrequency


def calculateAllCorrelationFactorAndOccurenceFrequencyType2(sequence, phyChemDict, lambdaPara, aminoAcid, phyChemList):
	corrFactorsDict = dict()

	occurfrequency = calculateOccurenceFrequencyOfAminoAcid(sequence, aminoAcid)

	for eachName in phyChemList:
		corrFactorsDict[eachName] = dict()
		for lamPa in range(1,(lambdaPara+1)):
			temp = []
			for resideIndex in range(len(sequence)-lamPa):
				preAA = sequence[resideIndex]
				backAA = sequence[resideIndex+lamPa]
				try:
					tempNumber = phyChemDict[eachName][preAA]*phyChemDict[eachName][backAA] # correlation function
					temp.append(tempNumber)
				except:
					continue

			corrFactorsDict[eachName][lamPa] = sum(temp)/len(temp)

	return corrFactorsDict, occurfrequency


def calculateFeatureValueByCorrFactorsDictAndOccurfrequencyType2(corrFactorsDict, occurfrequency, weightFact, lambdaPara, aminoAcid, phyChemList):
	featureValueStr = ''

	corrSum = 0
	for eachkey in phyChemList:
		corrSum += sum(corrFactorsDict[eachkey].values())
	corrPart = corrSum*weightFact
	
	for eachAA in aminoAcid:
		featureValueStr += ',%.6f'%(occurfrequency[eachAA]/(1+corrPart))

	for i in range(lambdaPara):
		for phyChemKey in phyChemList:
			featureValueStr += ',%.6f'%((weightFact*corrFactorsDict[phyChemKey][i+1])/(1+corrPart))

	return featureValueStr+'\n'


def generateCsvFormatLinebyType2PseAAC(in_file, out_file, weightFact, lambdaPara, phyChemDict, aminoAcid, phyChemList):
	g = open(out_file,'w')
	g.write(generateCsvFormatNoteLineType2(lambdaPara, aminoAcid, phyChemList))
	g.close()

	f = open(in_file)
	count_line = 0
	for eachline in f:
		if eachline[0] == '>':
			count_line += 1
			sampleType = re.findall(r'@(\d)@', eachline)[0]
		else:
			sequence = eachline.strip()
			[corrFactorsDict, occurfrequency] = calculateAllCorrelationFactorAndOccurenceFrequencyType2(sequence, phyChemDict, lambdaPara, aminoAcid, phyChemList)
			tempLine = calculateFeatureValueByCorrFactorsDictAndOccurfrequencyType2(corrFactorsDict, occurfrequency, weightFact, lambdaPara, aminoAcid, phyChemList)
			g = open(out_file,'a')
			g.write("%s%s"%(sampleType,tempLine))
			g.close()

	f.close()



import re
import sys

detectingPythonVersionAndOutputHelpInfo()
[typeOfPse, weightFact, lambdaPara, in_file, out_file] = obtainExternalParameters()
detectingTheRationalityOfLambdaPara(in_file, lambdaPara)

if __name__ == '__main__':
	phyChemStandFile = r'/home/zhaoyaw/myPythonScript/featureExtract/standard_value/nine_physicochemical_properties_of_amino_acid_Stand.txt'
	[phyChemDict, aminoAcid, phyChemList] = obtainAminoAcidPhysicoChemicalDict(phyChemStandFile)

	if typeOfPse == 1:
		generateCsvFormatLinebyType1PseAAC(in_file, out_file, weightFact, lambdaPara, phyChemDict, aminoAcid, phyChemList)
	elif typeOfPse == 2:
		generateCsvFormatLinebyType2PseAAC(in_file, out_file, weightFact, lambdaPara, phyChemDict, aminoAcid, phyChemList)
	else:
		printHelpInfo()

	print("------Finished!------")
