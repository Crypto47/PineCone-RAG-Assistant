from langchain_community.document_loaders import csv_loader

### lets try to load
loader=csv_loader.CSVLoader('data.csv')
test=loader.load()

print(loader)