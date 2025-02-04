import streamlit as st
import spacy
from annotated_text import annotated_text

@st.cache_resource(show_spinner=False)
def load_models():
    french_model=spacy.load("./models/fr")
    english_model=spacy.load("./models/en")
    models={"English": english_model, "French": french_model}
    return models

def process_text(doc, selected_entities, annonymize=False):
    tokens = []
    for token in doc:
        if (token.ent_type_=="PERSON") & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda")) 
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        else:
            tokens.append(" " + token.text + " ")
      
    if annonymize:
        annonymized_tokens = []
        for token in tokens:
            if type(token) == tuple:
                annonymized_tokens.append(("X" * len(token[0]), token[1], token[2])) 
            else:
                annonymized_tokens.append(token)
        return annonymized_tokens    
    return tokens

models = load_models()

selected_language = st.sidebar.selectbox("Select a language", options=["English", "French"])
selected_entities = st.sidebar.multiselect("Select the entities you want to detect & annonymize", 
                                           options=["LOC", "PER", "ORG"],
                                           default=["LOC", "PER", "ORG"],
                                           )

selected_model = models[selected_language]

text_input = st.text_area("Type a text to annonymize")

uploaded_file = st.file_uploader("or Upload a file", type=["doc", "docx", "pdf", "txt"])

if uploaded_file is not None:
    text_input=uploaded_file.getvalue()
    text_input=text_input.decode("utf-8")
    
st.markdown(f"input text: {text_input}")

annonymize = st.checkbox("Annonymize")

doc = selected_model(text_input)
tokens = process_text(doc, selected_entities, annonymize=annonymize)
annotated_text(*tokens)