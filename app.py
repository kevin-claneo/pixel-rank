import streamlit as st
import pandas as pd
import requests
import json
import re

# Streamlit App Configuration
def setup_streamlit():
    st.set_page_config(page_title="PixelRank with DataForSEO", page_icon="🏅", layout="wide")
    st.image("https://www.claneo.com/wp-content/uploads/Element-4.svg", width=600, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    st.title("🏅 PixelRank with DataForSEO")
    st.markdown("## Analyze the SERP pixel ranks for a set of keywords")
    st.divider()

# creating the Restclient
class RestClient:
    domain = "sandbox.dataforseo.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def request(self, path, method, data=None):
        connection = HTTPSConnection(self.domain)
        try:
            base64_bytes = b64encode(
                ("%s:%s" % (self.username, self.password)).encode("ascii")
                ).decode("ascii")
            headers = {'Authorization' : 'Basic %s' %  base64_bytes, 'Content-Encoding' : 'gzip'}
            connection.request(method, path, headers=headers, body=data)
            response = connection.getresponse()
            return loads(response.read().decode())
        finally:
            connection.close()

    def get(self, path):
        return self.request(path, 'GET')

    def post(self, path, data):
        if isinstance(data, str):
            data_str = data
        else:
            data_str = dumps(data)
        return self.request(path, 'POST', data_str)

language_options = ["Afrikaans","Albanian","Amharic","Arabic","Armenian","Azerbaijani","Basque","Belarusian","Bengali","Bosnian","Bulgarian","Catalan","Cebuano","Chinese (Simplified)","Chinese (Traditional)","Corsican","Croatian","Czech","Danish","Dutch","English","Esperanto","Estonian","Finnish","French","Frisian","Galician","Georgian","German","Greek","Gujarati","Haitian Creole","Hausa","Hawaiian","Hebrew","Hindi","Hmong","Hungarian","Icelandic","Igbo","Indonesian","Irish","Italian","Japanese","Javanese","Kannada","Kazakh","Khmer","Kinyarwanda","Korean","Kurdish","Kyrgyz","Lao","Latvian","Lithuanian","Luxembourgish","Macedonian","Malagasy","Malay","Malayalam","Maltese","Maori","Marathi","Mongolian","Myanmar (Burmese)","Nepali","Norwegian","Nyanja (Chichewa)","Odia (Oriya)","Pashto","Persian","Polish","Portuguese (Portugal","Punjabi","Romanian","Russian","Samoan","Scots Gaelic","Serbian","Sesotho","Shona","Sindhi","Sinhala (Sinhalese)","Slovak","Slovenian","Somali","Spanish","Sundanese","Swahili","Swedish","Tagalog (Filipino)","Tajik","Tamil","Tatar","Telugu","Thai","Turkish","Turkmen","Ukrainian","Urdu","Uyghur","Uzbek","Vietnamese","Welsh","Xhosa","Yiddish","Yoruba","Zulu"]
country_options = ["Afghanistan", "Albania", "Antarctica", "Algeria", "American Samoa", "Andorra", "Angola", "Antigua and Barbuda", "Azerbaijan", "Argentina", "Australia", "Austria", "The Bahamas", "Bahrain", "Bangladesh", "Armenia", "Barbados", "Belgium", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Belize", "Solomon Islands", "Brunei", "Bulgaria", "Myanmar (Burma)", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Sri Lanka", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Republic of the Congo", "Democratic Republic of the Congo", "Cook Islands", "Costa Rica", "Croatia", "Cyprus", "Czechia", "Benin", "Denmark", "Dominica", "Dominican Republic", "Ecuador", "El Salvador", "Equatorial Guinea", "Ethiopia", "Eritrea", "Estonia", "South Georgia and the South Sandwich Islands", "Fiji", "Finland", "France", "French Polynesia", "French Southern and Antarctic Lands", "Djibouti", "Gabon", "Georgia", "The Gambia", "Germany", "Ghana", "Kiribati", "Greece", "Grenada", "Guam", "Guatemala", "Guinea", "Guyana", "Haiti", "Heard Island and McDonald Islands", "Vatican City", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Kazakhstan", "Jordan", "Kenya", "South Korea", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Lesotho", "Latvia", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", "Mauritius", "Mexico", "Monaco", "Mongolia", "Moldova", "Montenegro", "Morocco", "Mozambique", "Oman", "Namibia", "Nauru", "Nepal", "Netherlands", "Curacao", "Sint Maarten", "Caribbean Netherlands", "New Caledonia", "Vanuatu", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Norway", "Northern Mariana Islands", "United States Minor Outlying Islands", "Federated States of Micronesia", "Marshall Islands", "Palau", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn Islands", "Poland", "Portugal", "Guinea-Bissau", "Timor-Leste", "Qatar", "Romania", "Rwanda", "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Vietnam", "Slovenia", "Somalia", "South Africa", "Zimbabwe", "Spain", "Suriname", "Eswatini", "Sweden", "Switzerland", "Tajikistan", "Thailand", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "United Arab Emirates", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "North Macedonia", "Egypt", "United Kingdom", "Guernsey", "Jersey", "Tanzania", "United States", "Burkina Faso", "Uruguay", "Uzbekistan", "Venezuela", "Wallis and Futuna", "Samoa", "Yemen", "Zambia"]



def keywords_from_excel():
    df = pd.read_excel(uploaded_file)
    column_name_mapping = {
    'Query': 'keyword',
    'QUERY':'keyword',
    'query':'keyword',
    'KEYWORD': 'keyword',
    'Keyword': 'keyword',}
    df.rename(columns=column_name_mapping, inplace=True)
    return df['keyword'].tolist()

def extract_domain(url):
    match = re.search(r"https?://(?:www\.|m\.|[^/]+\.)*?([^/\.]+\.[^/]+)(?:/.*|$)", url)
    domain = match.group(1) if match else url
    return domain

def calculate_pixelrank(df, domain):
    pixelrank = 0
    for _, row in df.iterrows():
        for item in row['items']:
            if 'domain' in item and domain in item['domain']:
                return pixelrank
            if 'rectangle' in item and item['rectangle']:
                pixelrank += item['rectangle']['height']
    return pixelrank

# Main Function
def main():
    setup_streamlit()
    with st.sidebar:
        st.header("Configuration")
        username = st.text_input("DataForSEO Username")
        password = st.text_input("DataForSEO Password", type="password")
        language = st.selectbox("Language", options=language_options, index=language_options.index("German"))
        country = st.selectbox("Country", options=country_options, index=country_options.index("Germany"))
        device = st.selectbox("Device", options=["desktop", "mobile"], index=1)
        domain = extract_domain(st.text_input("Domain"))
        uploaded_file = st.file_uploader("Upload Excel Sheet", type=['xlsx'])

    if st.button("Fetch SERP Data"):
        if not username or not password:
            st.warning("Please enter valid DataForSEO credentials.")
        elif not uploaded_file:
            st.warning("Please upload an Excel file with a keyword column.")
        else:
            st.success("Fetching data...")
            data = get_pixel_ranks(keywords, language, country, device, username, password)
            st.write(data)

if __name__ == "__main__":
    main()
