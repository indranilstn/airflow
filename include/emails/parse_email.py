from langchain_community.document_transformers import BeautifulSoupTransformer, Html2TextTransformer

bs_transformer = BeautifulSoupTransformer()
bs_transformer.transform_documents()

h2t_transformer = Html2TextTransformer()
h2t_transformer.transform_documents()