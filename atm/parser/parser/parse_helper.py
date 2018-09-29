# coding=utf-8

import re
from bs4 import BeautifulSoup
from file_helper import FileHelper
from str_helper import StrHelper
from nlp_helper import NLPHelper

class ParseHelper:
    
    @staticmethod
    def title2slug(title):
        s = list(title)
        slug = ''
        for c in s:
            if c.isalnum():
                slug += c
            if c == ' ':
                slug += '-'
        return slug.lower()
        
    @staticmethod
    def parseDoc(html, minContentWordCount = 128):
        soup = BeautifulSoup(html)    
        scripts = soup.findAll(['script', 'style', 'iframe'])
        for match in scripts:
            match.decompose()
            
        title = soup.find("title")
        titleContent = None
        if title != None:
            titleContent = title.text
        else:
            return [None, None]
        
        description = soup.find("meta", {"name": "description"})
        descriptionContent = None
        if description != None:
            descriptionContent = description.get("content")
            
        ogTitle = soup.find("meta", {"property": "og:title"})
        ogTitleContent = None
        if ogTitle != None:
            ogTitleContent = ogTitle.get("content")
        
        ogDescription = soup.find("meta", {"property": "og:description"})
        ogDescriptionContent = None
        if ogDescription != None:
            ogDescriptionContent = ogDescription.get("content")
        
        twitterTitle = soup.find("meta", {"name": "twitter:title"})
        twitterTitleContent = None
        if twitterTitle != None:
            twitterTitleContent = twitterTitle.get("content")
        
        twitterDescription = soup.find("meta", {"name": "twitter:description"})
        twitterDescriptionContent = None
        if twitterDescription != None:
            twitterDescriptionContent = twitterDescription.get("content")
        
        keyword = soup.find("meta", {"name": "keywords"})
        keywordContent = None
        if keyword != None:
            keywordContent = keyword.get("content")
        
        # Get title related Header
        headers = soup.find_all(['h1', 'h2'])
        titleHeader = None
        firstH1 = None
        firstH2 = None
        for h in headers:
            ht = h.text
            if len(ht) == 0:
                continue
            tagName = h.name
            if tagName == "h1":
                if firstH1 == None:
                    firstH1 = h
            elif tagName == "h2":
                if firstH2 == None:
                    firstH2 = h
            sim = StrHelper.getWordSimilarity(ht, titleContent)
            dis = StrHelper.getLevDistance(ht, titleContent) / len(ht)
            if sim > 50.0 or dis < 0.5:
                titleHeader = h
                break
        
        if titleHeader == None:
            if firstH1 != None:
                titleHeader = firstH1
            elif firstH2 != None:
                titleHeader = firstH2
        
        theParent = None
        theParentText = None
        found = False
        author = None
        if titleHeader != None:
            theParent = titleHeader.parent
            while theParent != None:
                tagName = theParent.name
                if tagName == "article" or tagName == "div":
                    theParentText = theParent.text
                    theParentTextList = theParentText.split()
                    if len(theParentTextList) >= minContentWordCount:
                        found = True
                        break
                elif tagName == "body" or tagName == "html":
                    break
                
                # next parent
                theParent = theParent.parent
        
            # no parent matched
            if not found:
                bodyNode = soup.find("body")
                theParentText = bodyNode.text
                titleHeaderText = titleHeader.text
                index = theParentText.find(titleHeaderText)
                if index >= 0:
                    theParentText = theParentText[index:]
                found = True
        else:
            return [False, None]
    
        # author
        if titleHeader != None:
            titleHeaderText = titleHeader.text
            index = theParentText.find(titleHeaderText)
            if index >= 0:
                pattern = r"By[\s]+[a-zA-Z\s]+"
                authorText = StrHelper.searchOneIgnoreCase(theParentText, pattern)
                print (authorText)
                if authorText != None:
                    indexAuthor = theParentText.find(authorText)
                    if indexAuthor > index:
                        # search count of linefeed between title and author
                        theText = theParentText[index:indexAuthor]
                        lines = theText.split('\n')
                        countLine = 0
                        for l in lines:
                            l = l.strip()
                            if len(l) > 0:
                                countLine += 1
                        if countLine <= 3:
                            index = authorText.find("\n")
                            if index > 0:
                                authorText = authorText[0:index]
                            authorText = authorText.replace("By", "").replace("by", "").strip()
                            # validate the word count of author
                            words = authorText.split()
                            if len(words) < 5:
                                author = authorText
                                print ("======>" + author)
                            else:
                                print ("======>skip, countWord=" + str(len(words)))
                        else:
                            print ("======>skip, countLine=" + str(countLine))
                                
            
        content = None
        summary = None
        summaryKeywords = None
        if found:
            content = theParentText.strip()
            summary = NLPHelper.getSummary(content)
            summaryKeywords = NLPHelper.getKeywords(summary)
            
        if summary == None or summaryKeywords == None:
            bodyNode = soup.find("body")
            theParentText = bodyNode.text
            summary = NLPHelper.getSummary(content)
            summaryKeywords = NLPHelper.getKeywords(summary)
        
        contentHtml = None
        if theParent != None:
            contentHtml = str(theParent)
            
        doc = {
            'title': titleContent,
            'ogTitle': ogTitleContent,
            'twTitle': twitterTitleContent,
            'description': descriptionContent,
            'ogDescription': ogDescriptionContent,
            'twDescription': twitterDescriptionContent,
            'keywords': keywordContent,
            'content': content,
            'contentHtml': contentHtml,
            'author': author,
            'summary': summary,
            'summaryKeywords': summaryKeywords
        }
        return [found, doc]

    @staticmethod
    def parseWordPressContent(html):
        titleValue = None
        descriptionValue = None
        contentValue = None
        
        soup = BeautifulSoup(html)    

        title = soup.find("title")
        if title != None:
            titleValue = title.text
        else:
            ogTitle = soup.find("meta", {"property": "og:title"})
            if ogTitle != None:
                titleValue = ogTitle.get("content")
        
        description = soup.find("meta", {"name": "description"})
        if description != None:
            descriptionValue = description.get("content")
        else:
            ogDescription = soup.find("meta", {"property": "og:description"})
            if ogDescription != None:
                descriptionValue = ogDescription.get("content")

        scripts = soup.findAll(['script', 'style', 'iframe'])
        for match in scripts:
            match.decompose()
            
        divList = soup.select("div#content")
        if (len(divList) == 1):
            contentValue = str(divList[0])


        if contentValue == None:
            divList = soup.select("div.content")
            if (len(divList) == 1):
                return str(divList[0])

        return titleValue, descriptionValue, contentValue

if __name__=="__main__":
    print("main")
    title = "abc Hello 123 &$#"
    slug = ParseHelper.title2slug(title)
    print (slug)
    
    html = FileHelper.readContent('./resource/wp_class_content.html')
    content = ParseHelper.parseWordPressContent(html)
    if content != None:
        print(len(content))

    html = FileHelper.readContent('./resource/wp_id_content.html')
    titleValue, descriptionValue, contentValue = ParseHelper.parseWordPressContent(html)
    if contentValue != None:
        print(len(contentValue))

        
