from django.shortcuts import render,HttpResponse,redirect
from django.template import Template, Context
import os
import shutil
# from pprint import pprint
import glob
from . models import myuploadfile
import PyPDF2
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
def index(request):
   
    return render(request,"index.html")

def send_files(request):
    

    files = glob.glob('C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite\\media/*')
    for f in files:
      os.remove(f)
    for parent, dirnames, filenames in os.walk('C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite'):
            for fn in filenames:
                if fn.lower().endswith('.pdf'):
                     os.remove(os.path.join(parent, fn))
    if request.method == "POST" :
        name = request.POST.get("filename") 
        myfile = request.FILES.getlist("uploadfiles")
        s=0
        for f in myfile:
            myuploadfile(f_name=name,myfiles=f).save() 
            s=s+1
        print("file:",s)
        dir_path = r'C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite\\media'
        # list to store files
        res = []

        # Iterate directory
        for path in os.listdir(dir_path):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                res.append(path)
        # print(res)
        source = 'C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite\\media'
        destination = 'C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite'
 
        # gather all files
        allfiles = os.listdir(source)
 
        # iterate on all files to move them to destination folder
        for f in allfiles:
             src_path = os.path.join(source, f)
             dst_path = os.path.join(destination, f)
             shutil.move(src_path, dst_path)
        sum=''
        # pdfs=["karachi.pdf","islamabad.pdf"]
        # print(res)
        i=0
        # file=1
        sumtext=""
        totaltext=0
        while i<len(res):
                a=PyPDF2.PdfFileReader(res[i])
                b=a.getNumPages()
                # print("Merge File pages Success:",b)
                text=""
                
                for j in range(0,b): 
                    text+=a.getPage(j).extract_text()
                # print(file,len(text))
                # file=+1
                sumtext=sumtext+text
                totaltext=len(sumtext)

                # print(text.encode('utf-8'))
                
                stopwords = list(STOP_WORDS)
                nlp = spacy.load('en_core_web_sm')
                nlp.max_length = 15000000
                doc= nlp(text)
                tokens = [token.text for token in doc]
                # print((tokens).encode("utf8"))

                 
                punctuation='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\n'
                punctuation = punctuation + '\n'
                word_frequencies = {}
                for word in doc:
                    if word.text.lower() not in stopwords:
                        if word.text.lower() not in punctuation:
                            if word.text not in word_frequencies.keys():
                                word_frequencies[word.text] = 1
                            else:
                                word_frequencies[word.text] += 1
                        
                # print(word_frequencies)
                max_frequency = max(word_frequencies.values())
                # max_frequency
                for word in word_frequencies.keys():
                    word_frequencies[word] = word_frequencies[word]/max_frequency

                # print(word_frequencies)
                sentence_tokens = [sent for sent in doc.sents]
                # print(sentence_tokens)
                sentence_scores = {}
                for sent in sentence_tokens:
                    for word in sent:
                        if word.text.lower() in word_frequencies.keys():
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word.text.lower()]
                            else:
                                sentence_scores[sent] += word_frequencies[word.text.lower()]
                                
                # sentence_scores
                from heapq import nlargest
                select_length = int(len(sentence_tokens)*0.1)
                # select_length
                summary = nlargest(select_length, sentence_scores, key = sentence_scores.get)
                # summary
                final_summary = [word.text for word in summary]
                summary = ' '.join(final_summary)
                # print(text.encode('utf-8'))
                # print("...........................................Summary...............................")
                
                sum = sum+summary
                # print(summary.encode("utf-8"))
                
                # lengthsum=len(summary)
                # print("...........................................--------...............................")
                
                i+=1
        lengthsum=0
        lengthsum=len(sum)
        # print("/////////////////////////////////////////////////////////////")
        # from textwrap3 import wrap
        a=sum
        # x = wrap(sum, 30)
       
        # for i in range(len(x)):
        #        a =a+x[i]

        # print (a)
        # print(len(a))
       
        for parent, dirnames, filenames in os.walk('C:\\Users\\Track Computers\\OneDrive\\Desktop\\irr\\mysite'):
            for fn in filenames:
                if fn.lower().endswith('.pdf'):
                     os.remove(os.path.join(parent, fn))
        # sem =spacy.load("en_core_web_lg")
        # a=sem(a).vector
        # sumtext=sem(sumtext).vector
        # similarityy=sumtext.similarity(a)
        # nlp('cheese')
        # print(similarityy)
        sim = spacy.load('en_core_web_sm')
        # sim = spacy.load('de_core_news_sm')
        # ws = {}
        #data = 'Some long text'
        data = a
        train_corpus = sim(data)
        train_corpus = sim(" ".join([token.text for token in train_corpus if not token.is_stop and len(token) > 4]))
        test_corpus = sim(sumtext)
        ae = train_corpus.similarity(test_corpus)

        text1="Total Words in Summary:"
        text2="Total Words in all Documents:"
        text3="Similarity between documents and Summary is:"
        Summ="Summary"

        context= {
        'a': a,
        # 'similarityy':similarityy,
        "ae":ae,
        "lengthsum":lengthsum,
        "totaltext":totaltext,
        "text1":text1,
        "text2":text2,
        "text3":text3,
        "Summ":Summ

        }
        return render(request, 'index.html', context)

