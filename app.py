import streamlit as st
from scraping import ImmoWeb

st.title("Web Scraping")

url = "[immoweb](https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance)"
link = "[github](https://github.com/mdifils/webscraping)"
message = f"""
This is a small demo about web scraping. In this demo, we'll be collecting properties informations on {url} website.
You can choose the type of property to be scraped. For each type of property, there are more than 300 pages.
But for simplicity, you can choose up to 3 pages to be scraped. For more details visit my {link}.
"""
st.write(message)

def get_data(property_type, nb_page):

    apartments = ImmoWeb(property_type)
    with st.spinner("In progress ..."):
        df = apartments.get_properties_info(apartments, pages=nb_page)
    return df 

def main():
    # creating two containers
    header = st.container()
    data = st.container()

    with header:
        col1, col2 = st.columns(2)
        with st.form(key="form1"):
            with col1:
                property_type = st.selectbox("Choose the property type: ", ("apartment", "house"))
            with col2:
                nb_page = st.slider("choose the number of pages: ",min_value=1, max_value=3)
            submit = st.form_submit_button("Scrape")

    if submit:
        df = get_data(property_type, nb_page)
        with data:
            st.dataframe(df)

if __name__ == "__main__":
    main()