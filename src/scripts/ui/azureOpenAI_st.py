import importlib
import os,sys
import pandas as pd
from openai import AzureOpenAI
path = os.getcwd()
sys.path.append(path)
from config.modelConfig import azOpenAI_Endpoint,apiKey,table_file

# Function to read table and guidelines
def read_table(df, NHS):
  # Read a table (example: CSV file)
  filteredDf = df[df['NHS Number']==NHS].copy()
  if filteredDf.empty:
      raise ValueError(f"No patient record found for NHS Number {NHS}.")

  # filteredDf.drop('NHS Number',inplace=True,axis=1)
  data = []
  for k, v in filteredDf.to_dict(orient='records')[0].items():
      if k !='NHS Number':
          data.append(str(k) + ' is ' + str(v) + ',')
  responseTxt = ' '.join(data)
  filteredDf['PatientData'] = responseTxt
  return filteredDf


def read_guidelines(text):
  guides = text.strip()
  return guides


# Function to apply the guidelines using OpenAI
def apply_guidelines_to_table(ptData, niceGuide):
  # Convert table to text
  PatientData = ptData['PatientData'].values[0]

  # Create the prompt by combining guidelines and table text
  prompt = f"Here are some guidelines:\n{niceGuide}\n\n" \
           f"for a patient whose {PatientData}\n\n" \
           '''please provide a appropriate medication to be prescribed with side-effects
           based on the guidelines for the PatientData only in pointers.'''

  client = AzureOpenAI(
      azure_endpoint = azOpenAI_Endpoint,
      api_key = API_KEY,
      api_version="2024-02-15-preview"
  )
  # Make a request to the OpenAI API
  response = client.chat.completions.create(
      model='gpt-35-turbo',
      temperature=0.1,
      max_tokens=400,
      messages=[
          {"role": "system", "content": 'i am a medical practitioner'},
          {"role": "user", "content": prompt}
      ]
  )
  # Retrieve the updated table from the API response
  responseSuggestion = response.choices[0].message.content
  ptData['AI_Response'] = responseSuggestion
  return ptData


def aiResp(NHS):
  niceGuideExtract = importlib.import_module('src.scripts.nice.niceGuideExtract')
  niceUrls = importlib.import_module('src.scripts.nice.niceUrls')

  # Reload NICE modules to pick up latest definitions when running under Streamlit autoreload.
  niceGuideExtract = importlib.reload(niceGuideExtract)
  niceUrls = importlib.reload(niceUrls)

  # Read the table and guidelines from files
  nice_guideline_map = niceGuideExtract.extractNiceData()
  try:
      niceGuidelines = nice_guideline_map[niceUrls.PRIMARY_GUIDANCE_KEY]
  except KeyError as exc:
      raise RuntimeError(
          f"NICE guidance '{niceUrls.PRIMARY_GUIDANCE_KEY}' missing from extracted data."
      ) from exc

  guidelines_file = niceGuidelines
  df = pd.read_csv(table_file)
  NHS_Number = NHS
  healthTbl = read_table(df,NHS_Number)
  guidelines = read_guidelines(guidelines_file)

  updated_resp = apply_guidelines_to_table(healthTbl, guidelines)
  ptData = healthTbl['PatientData']
  aiOutput = updated_resp['AI_Response'].values[0]

  return {'PatientInfo':healthTbl,'AIResp':aiOutput,'NICE':niceGuidelines}


# if __name__ == '__main__':
#     aiResp(int('0238248234'))
