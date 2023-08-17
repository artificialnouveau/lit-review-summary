# Basic Literature Review Search and Summary

Certainly! Below is a `README.md` file for your code.

---

# PubMed Paper Search and Analysis

This script provides functionality to search for papers on PubMed based on a given set of keywords. It then downloads the papers in PDF format and converts them to TXT for further analysis. The script also allows extracting specific sentences containing a particular keyword from the abstract and the paper's text content. Additionally, it provides the capability to generate extractive summaries for abstracts and extracted sentences.

## Setup

### Requirements:

- Python 3.x
- The required libraries can be installed using the following command:
  
  ```
  pip install biopython pandas requests PyPDF2 bert-extractive-summarizer
  ```

## Functions:

1. `search_pubmed()`: This function searches for papers on PubMed based on given keywords and some default filters (e.g., human studies, English language, etc.). It returns the results in a DataFrame format.

2. `download_and_convert_pdfs()`: This function takes a list of DOIs (Digital Object Identifier) and attempts to download each paper in PDF format from Sci-Hub. It also converts these PDFs into TXT files for subsequent analysis.

3. `extract_sentences_with_keyword()`: This function extracts specific sentences from the paper's abstract and its text content based on a given keyword.

4. `summary()`: Utilizes the BERT model to provide an extractive summary for the given text.

## Usage:

1. Make sure to set your email in the `search_pubmed()` function where `Entrez.email` is set.

2. Define your list of keywords, for example:
  
  ```python
  keywords = ["diabetes", "treatment"]
  ```

3. Search for papers using the defined keywords:

  ```python
  df = search_pubmed(keywords)
  ```

4. Download the papers in PDF format and convert them to TXT:

  ```python
  download_and_convert_pdfs(df['DOI'].tolist())
  ```

5. Extract specific sentences using a keyword:

  ```python
  search_keyword = "diabetes"
  data = []
  for _, row in df.iterrows():
      extracted_sentences = extract_sentences_with_keyword(search_keyword, row['Abstract'], row['DOI'])
      data.append({
          'DOI': row['DOI'],
          'ExtractedSentences': ' '.join(extracted_sentences)
      })
  sentences_df = pd.DataFrame(data)
  merged_df = pd.merge(df, sentences_df, on="DOI")
  ```

6. To generate summaries for the abstract or extracted sentences:

  ```python
  merged_df['AbstractSummary'] = merged_df['Abstract'].apply(summary)
  merged_df['SentenceSummary'] = merged_df['ExtractedSentences'].apply(summary)
  ```

7. For summarizing the entire "Abstract" column or "Extracted Sentences" column:

  ```python
  all_abstracts = ' '.join(merged_df['Abstract'])
  all_sentences = ' '.join(merged_df['ExtractedSentences'])
  abstract_summary = model(all_abstracts)
  sentence_summary = model(all_sentences)
  ```
