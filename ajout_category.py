
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd

# load env
load_dotenv()
OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
AZURE_OPENAI_ENDPOINT= os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

llm_gpt4o = AzureChatOpenAI(
    deployment_name="gpt4o",api_key=AZURE_OPENAI_API_KEY,api_version= "2024-02-01",
        temperature=0,
    max_tokens=800
)


# prompts
template_1 = """
en utilisant tes connaissances, classe l'oeuvre dans une des catégories suivantes : 

fiction/SF
fiction/fantasy
fiction/fantastique

non-fiction/lifestyle
non-fiction/parenting
non-fiction/histoire
non-fiction/santé

si aucune des catégories ne convient, tu peux générer une autre, en gardant la même structure (en commençant par fiction ou non-fiction).
n'ajoute rien d'autre.

exemple : 
harry potter et la chambre des secrets = fiction/fantastique

question: {oeuvre}

catégorie:"""
rag_prompt_1 = PromptTemplate.from_template(template_1)

# chain générative
chain_category = (
    {"oeuvre": RunnablePassthrough()}
    | rag_prompt_1
    | llm_gpt4o
    | StrOutputParser()
) # uniquement pour la partie analyse des résultats


# enrichissement du excel source
df = pd.read_excel("export_xls\liste_livre.xlsx")
df = df.drop('categorie', axis=1)
df['oeuvre'] = df[['Titre', 'Auteurs']].astype(str).agg(' - '.join, axis=1)

# fonction pour créer une colonne avec un résumé de la question. Servira à gagner en lisibilité sur les visuels
def find_category(oeuvre):
    result = chain_category.invoke(oeuvre)
    return result

df['categorie'] = df['oeuvre'].apply(find_category)

# Extraire un excel :
output_directory = "export_xls/"
output_file = f'{output_directory}liste_livre_category.xlsx'
df.to_excel(output_file, index=False)
print(f"Le fichier {output_file} a été créé avec succès.")