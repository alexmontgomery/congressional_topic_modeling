# Overview
- Scraping Scripts: used to scrape documents of interest from congress.gov, which are loaded into a Supabase data table for storage.
- Topic Modeling: once the scraped documents have been collected and cleaned, the documents are fed through NLP models (FASTopic and LDA at this point) to perform topic modeling.
