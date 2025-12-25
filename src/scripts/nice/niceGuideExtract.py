import json
import requests
import pandas as pd
from functools import lru_cache
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString
from src.scripts.nice import niceUrls
from config.logger import logit

# log = logit(r'C:\Users\MSI\PycharmProjects\dhsit_nhs\src\files\logs','NiceExtract')

def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return bs(text, 'html.parser').get_text(separator=' ', strip=True)

def baseTblData(symptom):
    # log.info('extracting table from url')
    url_hyp = niceUrls.build_search_url(symptom)
    try:
        response = requests.get(url_hyp, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Unable to reach NICE search endpoint for '{symptom}'.") from exc

    soup = bs(response.text, 'html.parser')
    payload_node = soup.find('script', {'id': '__NEXT_DATA__'})
    if payload_node is None or not payload_node.text:
        raise RuntimeError("NICE search payload missing from response.")

    try:
        payload = json.loads(payload_node.text)
        documents = (
            payload.get('props', {})
            .get('pageProps', {})
            .get('results', {})
            .get('documents', [])
        )
    except (json.JSONDecodeError, AttributeError) as exc:
        raise RuntimeError("Unable to parse NICE search payload.") from exc

    if not documents:
        raise RuntimeError("NICE search returned no documents.")

    rows = []
    for doc in documents:
        heading = doc.get('titleNoHtml') or _strip_html(doc.get('title', ''))
        rows.append({
            'links': niceUrls.ensure_absolute(doc.get('url') or doc.get('summaryUrl')),
            'heading': heading or doc.get('guidanceRef') or 'N/A',
            'ref_no': doc.get('guidanceRef'),
            'published': doc.get('publicationDate'),
            'last_updated': doc.get('lastUpdated') or doc.get('publicationDate'),
        })

    return pd.DataFrame(rows)


@lru_cache(maxsize=6)
def extractNiceData(symptom: str = niceUrls.DEFAULT_SYMPTOM):
    symptoms = symptom or niceUrls.DEFAULT_SYMPTOM
    baseData = baseTblData(symptoms)
    hyt_adults = baseData[
        baseData['heading'].str.contains('in adults', case=False, na=False)
    ].to_dict(orient='records')
    if not hyt_adults:
        raise RuntimeError("Unable to locate NICE hypertension guidance in search results.")

    resData = {}
    for items in hyt_adults:
        try:
            r = requests.get(items['links'], timeout=20)
            r.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"NICE guidance page could not be retrieved: {items['links']}") from exc

        webCont = bs(r.content, 'html.parser')
        extractedText = webCont.get_text(types=NavigableString).replace('\n',' ').strip()
        heading = items['heading']
        resData[heading] = extractedText
        clean_heading = heading.split('(')[0].strip()
        if clean_heading and clean_heading not in resData:
            resData[clean_heading] = extractedText
    return resData


if __name__ == '__main__':
    NiceData = extractNiceData()
    print(NiceData['Hypertension in adults: diagnosis and management'])
