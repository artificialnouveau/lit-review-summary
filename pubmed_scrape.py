from Bio import Entrez
import pandas as pd
from typing import List, Dict
import os
import requests
import PyPDF2
from io import BytesIO
from summarizer import Summarizer

def search_pubmed(keywords: List[str], year_start: int = 2000, year_end: int = 2022) -> pd.DataFrame:
    Entrez.email = "your_email@example.com"  # Replace with your email
    search_term = " AND ".join(keywords) + \
                  " AND human[title/abstract] AND English[lang] AND " + \
                  f"{year_start}:{year_end}[pubdate]"

    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=100)  # You can adjust retmax as needed
    record = Entrez.read(handle)
    handle.close()

    id_list = record["IdList"]

    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
    records = Entrez.parse(handle)
    
    data = []
    for record in records:
        if 'DOI' in record and 'TI' in record and 'AB' in record:
            authors = []
            if 'AU' in record:
                authors = ', '.join(record['AU'])

            mesh_terms = []
            if 'MH' in record:
                mesh_terms = ', '.join(record['MH'])

            journal = ''
            if 'JT' in record:
                journal = record['JT'][0]
                
            data.append({
                'DOI': record['DOI'][0],
                'Title': record['TI'][0],
                'Abstract': record['AB'][0],
                'Authors': authors,
                'Keywords': mesh_terms,
                'Journal': journal
            })
    handle.close()

    return pd.DataFrame(data)

def download_and_convert_pdfs(dois: List[str]):
    BASE_URL = "https://sci-hub.se/"
    PDF_DIR = "pdfs"
    TXT_DIR = "txts"
    
    # Ensure directories exist
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
    if not os.path.exists(TXT_DIR):
        os.makedirs(TXT_DIR)

    for doi in dois:
        try:
            response = requests.get(BASE_URL + doi, allow_redirects=True)
            if response.status_code == 200 and 'pdf' in response.headers['Content-Type']:
                # Save PDF
                pdf_path = os.path.join(PDF_DIR, f"{doi.replace('/', '_')}.pdf")
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                    
                # Convert to TXT
                txt_path = os.path.join(TXT_DIR, f"{doi.replace('/', '_')}.txt")
                with open(pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfFileReader(pdf_file)
                    text = ""
                    for page_num in range(reader.numPages):
                        text += reader.getPage(page_num).extractText()
                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)
            else:
                print(f"Failed to fetch or save PDF for DOI: {doi}")
        except Exception as e:
            print(f"Error processing DOI {doi}: {e}")


def extract_sentences_with_keyword(keyword: str, abstract: str, doi: str) -> List[str]:
  sentences = []
  # Extract from abstract
  for sentence in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', abstract):
    if keyword.lower() in sentence.lower():
      sentences.append(sentence)

    # Extract from text file
    txt_path = os.path.join(TXT_DIR, f"{doi.replace('/', '_')}.txt")
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for sentence in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content):
                if keyword.lower() in sentence.lower():
                    sentences.append(sentence)
    return sentences

def summary(text: str) -> str:
    model = Summarizer()
    return model(text)

# EXAMPLES
# ==================================
# Example keywords
keywords = ["diabetes", "treatment"]
# Example of how to search for papers using keywords on pubmed
df = search_pubmed(keywords)
# Run this if you want to save the pdfs and converted txt files of the pubmed papers
download_and_convert_pdfs(results['DOI'].tolist())


# Example of how to extract specific sentences with one keyword of interest:
search_keyword = "diabetes"  # Replace with your specific keyword

data = []
for _, row in results.iterrows():
    extracted_sentences = extract_sentences_with_keyword(search_keyword, row['Abstract'], row['DOI'])
    data.append({
        'DOI': row['DOI'],
        'ExtractedSentences': ' '.join(extracted_sentences)  # This combines all sentences from a paper into a single string.
    })

# Convert to DataFrame and merge with the original results DataFrame
sentences_df = pd.DataFrame(data)
merged_df = pd.merge(results, sentences_df, on="DOI")

# Optionally, you can now use the summary function to summarize the 'Abstract' or 'Extracted Sentences' columns:
merged_df['AbstractSummary'] = merged_df['Abstract'].apply(summary)
merged_df['SentenceSummary'] = merged_df['ExtractedSentences'].apply(summary)

# If you wish to save the merged dataframe:
# merged_df.to_csv("merged_findings.csv", index=False)

# Summarize the entire Abstract column and Extracted Sentences column
model = Summarizer()  # Initialize the model once to improve efficiency

all_abstracts = ' '.join(merged_df['Abstract'])
all_sentences = ' '.join(merged_df['ExtractedSentences'])

abstract_summary = model(all_abstracts)
sentence_summary = model(all_sentences)

print("Summary for All Abstracts:")
print(abstract_summary)
print('')
print("Summary for All Extracted Sentences:")
print(sentence_summary)
