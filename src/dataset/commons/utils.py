from pymongo import MongoClient
import re
import pandas as pd
import os
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_mongo_docs():
    URI = "mongodb://%s:%s@localhost:27017/echr" % ("echr_read", "echr_read")
    client = MongoClient(URI)
    database = client['echr']
    hejud = database["hejud"]
    return hejud

def extract_paragraph_numbers(text,pattern=r'(§{1,2})\s*(\d+)(?:-(\d+))?'):
    try:
        
        pattern = re.compile(pattern)
        
        matches = pattern.findall(text)
        
        if not matches:
            return []
        
        last_match = matches[-1]
        start = int(last_match[1])
        end = int(last_match[2]) if last_match[2] else start

        return list(range(start, end + 1))
    
    except Exception as e:
        print("Could not parse out the paragraph number")
        return None 
def split_paragraph_tuple(input_tuple, paragraph_pattern=r'§{1,2}\s*(\d+)(?:-(\d+))?'):
    text, size, font, link = input_tuple
    
    pattern = re.compile(paragraph_pattern)
    
    matches = list(pattern.finditer(text))
    
    if len(matches) < 2:
        return [input_tuple]
    
    paragraphs = [match.group() for match in matches]
    if all(paragraph == paragraphs[0] for paragraph in paragraphs):
        return [input_tuple]
    
    # Get the starting positions of each match
    match_positions = [match.start() for match in matches]
    
    # Split the text at the positions of the paragraph tags
    result = []
    start = 0
    for i in range(1, len(match_positions)):
        prev_pos = match_positions[i - 1]
        curr_pos = match_positions[i]
        
        if curr_pos - prev_pos < 100:
            result.append((text[start:curr_pos].strip(), size, font, None))
            start = curr_pos
            
    result.append((text[start:].strip(), size, font, link))
    
    return result

def sentence_extraction(id, docs):
    document = docs.find_one({'_id': id})
    
    paragraphs = []
    try:
        if document is None:
            return []
        
        sentences = document["sentences"]
        print(id)
        flag = 0
        i = 0
        while i < len(sentences):
            if "PROCEDURE".lower() in sentences[i].lower():
                i += 1
                break
            i += 1
        j = 0
        
        while j < len(sentences[i:]):
            if "FOR THESE REASONS, THE COURT".upper() in sentences[j].upper():
                j += 1
                break
            j += 1
        
        sentences = create_para_sub_para(sentences=sentences[i:j+1])
        return sentences
    except Exception as e:
        print(f"Doc not present for this id : {id}")
        
        return []
    
def extract_paragraphs_from_sentences(id, sentences, paragraph_no):
    paragraphs = []
    try:
        for doc in sentences:
            match = re.match(r'\d+', doc[0][:5])
            if match:
                if int(match.group()) == paragraph_no:
                    paragraphs.append(doc)
        return paragraphs[0]
    except Exception as e:
        print(f"Paragraph issue for : {id} and paragraph number : {paragraph_no} \n issue : {e}")
        
        return []
    
def create_para_sub_para(sentences):
    
    final_document = []
    previous_number = 0
    document = []
    
    for sentence in sentences:
        match = re.match(r'\d+', sentence[:5])
        if match:
            if int(match.group()) == previous_number + 1:
                previous_number = int(match.group())
                final_document.append(document)
                document = []
        if len(sentence) > 30:
            document.append(sentence)
    if len(document) > 0:
        final_document.append(document)
    
    return final_document[1:]
def truncate_to_one_decimal(num):
    return int(num * 10) / 10.0

def compare(num1, num2):
    return (truncate_to_one_decimal(num1) == truncate_to_one_decimal(num2)) or (abs(truncate_to_one_decimal(num1) - truncate_to_one_decimal(num2)) <0.2)

def extract_paragraph_from_html(id, paragraph, docs):
    document = docs.find_one({'_id': id})
    paragraphs = []
    try:
        if document is None:
            print("document not present")
            return []
        html = document["html"]
        if not html:
            print("No HTML content found")
            return []
        paragraphs = extract_paragraphs_within_class(html, "s30EEC3F8", str(paragraph))
             
        return paragraphs
    except Exception as e:
        print(f"Paragraph not present for this id : {id}")
        return []
    
def extract_paragraphs_within_class(html_content, target_class, target_string):
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')

    results = []
    capture = False
    for p in paragraphs:
        text = p.get_text()
        p_class = p.get('class', [])
        if f"{target_string}." in text[:5] and target_class in p_class:
            capture = True
        if capture:
            results.append(text)
            next_sibling = p.find_next_sibling('p')
            if next_sibling and target_class in next_sibling.get('class', []):
                break

    return results

def find_overlapping_paragraphs(paragraphs1, paragraphs2, threshold=0.7):
    try:
        vectorizer = TfidfVectorizer().fit_transform(paragraphs1 + paragraphs2)
        vectors = vectorizer.toarray()
        similarity_matrix = cosine_similarity(vectors[:len(paragraphs1)], vectors[len(paragraphs1):])
        
        overlapping_pairs = []
        for i in range(len(paragraphs1)):
            for j in range(len(paragraphs2)):
                if similarity_matrix[i, j] > threshold:
                    overlapping_pairs.append((paragraphs1[i], paragraphs2[j], similarity_matrix[i, j]))
        
        return overlapping_pairs
    except Exception as e:
        print("issue with similarity check. Ignoring this datapoint")
        return None

def capture_paragraphs(id, paragraph_no, sentences):
    sentence_paragraphs = extract_paragraphs_from_sentences(id, sentences, paragraph_no)
    
    return sentence_paragraphs

def capture_case_heading(id, docs):
    try:
        document = docs.find_one({'_id': id})
        
        return document['docname']
    except Exception as e:
        print(f"Case Heading : no doc present for id : {id}")
        return ""
    
def extract_and_format_url(link):
    match = re.search(r'itemid%22:\[%22(001-\d+)%22\]', link)
    if match:
        item_id = match.group(1)
        formatted_id = f"{item_id.zfill(6)}"
        return formatted_id
    return None


if __name__ == "__main__":
    docs  = get_mongo_docs()
    sentences = sentence_extraction("001-57675", docs)
    flag = True
    for i in sentences:
        if flag:
            print(flag)
            flag = not flag
        if("37. " in i):
            print(i)
    additional_paragraphs = extract_paragraphs_from_sentences("001-57675", sentences, 37)
    print(capture_case_heading("001-57675",docs))
    
    print(additional_paragraphs)
    