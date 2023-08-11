import streamlit as st
from PIL import Image
import easyocr as ocr
import numpy as np
import re
import pandas as pd
import mysql.connector as sql

st.set_page_config(page_title='BIZ CARD', page_icon=':card_index:', layout="wide")
st.title('------------------------------ :card_index: :green[ BIZ CARD] :card_index: -----------------------------')
col11, col12 = st.columns(2)
with col11:
    image = Image.open(r'istockphoto-1289388645-612x612.jpg')
    st.image(image)
with col12:
    st.subheader(':blue[BIZ CARD is an user-friendly web appilication developed to recognize, extract and store the details of a business card such as company name, card-holder name, Email Id, mobile number, address, website URL, etc. The application gets the Business card in an image format and extracts the information and stores in MySQL. The stored data is then displayed on streamlit page on the wish of the user.]')

# file-uploader
st.header('UPLOAD THE BUSINESS CARD IMAGE TO EXTRACT INFO')
st.write("#### SELECT AN IMAGE")
img = st.file_uploader(label = "",type=['png','jpg','jpeg'])


# extract info
@st.cache
def reader():
    read1 = ocr.Reader(['en'])
    return read1


phone_no = []
email = ''
pincode = ''
url = ''
address = []
state = []
city = []
area = []
name = []
desgn = []

if img is not None:
    read = reader()
    img1 = Image.open(img)
    st.image(img1)
    st.write(" ")

    result = read.readtext(np.array(img1))
    result_text = []  # empty list for results
    for text in result:
        result_text.append(text[1])
    # name
    name.append(result_text[0])
    # desgn
    desgn.append(result_text[1])

    for i, s in enumerate(result_text):
        # email
        if re.search(r'@', s.lower()):
            email = s.lower()

        #address
        if re.search(',+', s):
            address = re.split(',', s)

        # pincode
        match = re.search(r'\d{6,7}', s.lower())
        if match:
            pincode = match.group()
            try:
                a = re.split(' ', s)
                address.append(a[0])
                address.append(a[1])
            except:
                pass

        # phone no.
        match = re.search(r'(?:ph|phone|phno)?\s*(?:[+-]?\d\s*[\(\)]*){7,}', s)
        if match and len(re.findall(r'\d', s)) > 7:
            phone_no.append(s)

        # URL
        if re.match(r"(?!.*@)(www|.*[.]com$)", s):
            url = s.lower()
            url_id = i
# area
area.append(address[0])
# city
city.append(address[1])
# state
state.append(address[2])

#st.write(phone_no[0], email, pincode, url, state[0], city[0],area[0], name[0], desgn[0])

# CONNECTING TO MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="jaya1976",
                   database= "bizcards"
                  )
c = mydb.cursor(buffered=True)

# TABLE CREATION
c.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10)
                    )''')




