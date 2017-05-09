import sys, os, math, re

fOutput= open("bleu_out.txt", "w+")
if len(sys.argv)!=3:
	sys.exit(sys.argv[0])
else:
	candidate_file = sys.argv[1]
	reference_file = sys.argv[2]

	if os.path.isfile(reference_file):
		multipleReference= False;
	elif os.path.isdir(reference_file):
		multipleReference= True;


def computeNGrams(file, n):
	ngrams = []
	with open(file, 'r') as f:
		for line in f.readlines():
			line= re.sub("  "," ", line)
			words= line.strip().split(' ')
			#print words, len(words)
			line_ngrams={}
			#if len(words) < n:
			#	ngram= " ".join(words).strip()
			#	if ngram in line_ngrams:
			#		line_ngrams[ngram] += 1
			#	else:
			#		line_ngrams[ngram] = 1
			#else:
			end_index= len(words) - n
			for i in range(0, end_index+1):
				words_n= words[i : i+n]
				ngram= " ".join(words_n).strip()
				if ngram in line_ngrams:
					line_ngrams[ngram] += 1
				else:
					line_ngrams[ngram] = 1
			ngrams.append(line_ngrams)
		return ngrams


#candidate_ngrams= computeNGrams(sys.argv[1], 4)
#ref= 'C:/Python27/NLP Assignments/Homework 8/reference-4'

#print os.path.abspath(reference_file)
#print os.walk(os.path.abspath(reference_file))
def getCandidateNGrams(n):
	candidate_ngrams=[]
	candidate_ngrams= computeNGrams(candidate_file, n)
	return candidate_ngrams

def getReferenceNGrams(n):
	reference_ngrams=[]
	if not multipleReference:
		reference_ngrams= computeNGrams(reference_file, n)
		return reference_ngrams
	else:
		for root, dirs, files in os.walk(reference_file):
			#print root, dirs, files
			reference_files=[]
			for name in files:
				reference_files.append(name)
		for ref in reference_files:
			ref= os.path.join(root, ref)
			ngrams_list= computeNGrams(ref, n)
			reference_ngrams.append(ngrams_list)
		#print "R", reference_ngrams
		return reference_ngrams

#getReferenceNGrams(4)
#getCandidateNGrams(4)unt

def getWordCountOfFile(ngrams):
	word_count=0
	for line in ngrams:
		for i, count in line.iteritems():
			word_count += count
	return word_count


def getWordCountOfLine(ngrams):
	word_count=0
	for i, count in ngrams.iteritems():
		word_count += count
	return word_count

def computeBLEU_NGrams():
	if not multipleReference:
		pn=[]
		for n in range(1, 5):
			reference_ngrams= getReferenceNGrams(n)
			candidate_ngrams= getCandidateNGrams(n)
			if n==1:
				candidate_word_count= getWordCountOfFile(candidate_ngrams)
				reference_word_count= getWordCountOfFile(reference_ngrams)
				bp=	computeBrevityPenalty(candidate_word_count, reference_word_count)

			total_count=0
			for cand_line_index, cand_line in enumerate(candidate_ngrams):
				count=0
				ref_line= reference_ngrams[cand_line_index]
				for cand_ngram, cand_count in cand_line.iteritems():
					if cand_ngram in ref_line:
						clipped_count= min(cand_count, ref_line[cand_ngram])
						count += clipped_count
				total_count += count
#				print total_count, getWordCountOfFile(candidate_ngrams)
			result= float (total_count)/getWordCountOfFile(candidate_ngrams)
			pn.append(result)
		return bp, pn

	else:
		pn=[]
		for n in range(1, 5):
			reference_ngrams=[]
			candidate_ngrams= getCandidateNGrams(n)
			reference_ngrams= getReferenceNGrams(n)

			if n==1:
				#print reference_ngrams
				reference_word_count=0
				candidate_word_count= getWordCountOfFile(candidate_ngrams)
				for cand_line_index in range(len(candidate_ngrams)):
					word_count_list=[]
					for ref in reference_ngrams:
						word_count= getWordCountOfLine(ref[cand_line_index])
						word_count_list.append(word_count)
					closest_reference_length= min(word_count_list)
					reference_word_count += closest_reference_length
				bp= computeBrevityPenalty(candidate_word_count, reference_word_count)
				
			total_count=0
			for cand_line_index, cand_line in enumerate(candidate_ngrams):
				count=0
				for cand_ngram, cand_count in cand_line.iteritems():
					maxcount=-1
					for ref in reference_ngrams:
						if cand_ngram in ref[cand_line_index]:
							clipped_count= min(cand_count, ref[cand_line_index][cand_ngram])
							if clipped_count > maxcount:
								maxcount=clipped_count
					if maxcount > 0:
						count += maxcount
				total_count+=count
			result= float (total_count)/getWordCountOfFile(candidate_ngrams)
			pn.append(result)
		return bp, pn

def computeBrevityPenalty(candidate_word_count, reference_word_count):
	if candidate_word_count > reference_word_count:
		bp= 1
	else:
		fraction=  float (reference_word_count)/candidate_word_count
		bp= math.exp(1-fraction)
	return bp

def computeBLEU():
	BLEU=0.0
	bp, pn= computeBLEU_NGrams()
	#print bp, pn
	sum_exp=0.0
	for p in pn:
		w = 1.00/len(pn)
		if p > 0:
			sum_exp += w * math.log(p)
	BLEU= bp * math.exp(sum_exp)
	#print BLEU
	fOutput.write(str(BLEU))

computeBLEU()