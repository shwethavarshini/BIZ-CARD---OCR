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
                   password="password",
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
if st.button("Upload data to MySQL"):
    sql = """INSERT INTO card_data(card_holder,designation,mobile_number,email,website,area,city,state,pin_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    c.execute(sql, (name[0], desgn[0], phone_no[0], email, url, area[0], city[0], state[0], pincode))
    mydb.commit()
    st.success("#### Uploaded to database successfully!")

# MODIFICATIONS
if st.button("Click to modify stored data"):
    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="large")
    try:
        with column1:
            c.execute("SELECT card_holder FROM card_data")
            result = c.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            c.execute("select * from card_data WHERE card_holder=%s", (selected_card,))
            result = c.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            card_holder = st.text_input("Card_Holder", result[0])
            designation = st.text_input("Designation", result[1])
            mobile_number = st.text_input("Mobile_Number", result[2])
            email = st.text_input("Email", result[3])
            website = st.text_input("Website", result[4])
            area = st.text_input("Area", result[5])
            city = st.text_input("City", result[6])
            state = st.text_input("State", result[7])
            pin_code = st.text_input("Pin_Code", result[8])

            if st.button("Do and save changes"):
                # Update the information for the selected business card in the database
                c.execute("""UPDATE card_data SET card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (card_holder, designation, mobile_number, email, website, area, city, state, pin_code, selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            c.execute("SELECT card_holder FROM card_data")
            result = c.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            if st.button(f"Yes Delete {selected_card}'s Business Card"):
                c.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")

    if st.button("View updated data"):
        c.execute("select * from card_data")
        updated_df = pd.DataFrame(c.fetchall(), columns=["Card_Holder", "Designation", "Mobile_Number", "Email", "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)




