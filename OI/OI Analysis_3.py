from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook

def Get_data(url):  
    # Set options for Microsoft Edge
    options = Options()
    options.use_chromium = True  # Use this option if using Edge Chromium

    # Specify the path to the WebDriver executable
    webdriver_path = r"C:\Users\anmol.chopra\Downloads\edgedriver_win64 (1)\msedgedriver.exe"

    # Initialize the WebDriver
    service = Service(webdriver_path)
    driver = webdriver.Edge(service=service, options=options)

    # Open a particular website
    # url = 'https://www.cmegroup.com/markets/agriculture/oilseeds/soybean.volume.html'
    driver.get(url)

    html_source = driver.page_source

    soup = BeautifulSoup(html_source, 'html.parser')

    # Locate all tables
    tables = soup.find_all('div', {'class': 'main-table-wrapper'})

    # Check if there are enough tables
    if len(tables) > 1:
        table = tables[1].find('table')  # Select the second table
    else:
        raise ValueError("The second table is not found on the page.")


    label_element = driver.find_element(By.XPATH, '//label[text()="Trade Date"]')

    # Find the adjacent sibling element containing the date
    date_element = label_element.find_element(By.XPATH, './following-sibling::div//span[@class="button-text"]')

    # Extract the date text from the element
    date_text = date_element.text

    # Extract table headers
    headers = []
    header_rows = table.find_all('thead')
    for header_row in header_rows:
        cols = header_row.find_all('th')
        for col in cols:
            colspan = int(col.get('colspan', 1))
            headers.extend([col.get_text(separator=' ').strip()] * colspan)

    # Extract table rows
    rows = []
    for row in table.find_all('tbody')[0].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 0:
            cols = [ele.get_text().strip() for ele in cols]
            rows.append(cols)

    # Create DataFrame
    df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
    driver.quit()

    return df,date_text


def data_transform(df,date_text):
    df = df[['Month','Open Interest']]
    df.columns = ['Month','OI','Open Interest']
    df = df.drop(columns='OI')
    df_new = df.T
    df_new = df_new.astype(str)
    df_new.columns = df_new.iloc[0]
    df_new = df_new.drop(df_new.index[0])
    df_new.insert(0,'Date',date_text.split(', ')[1] )
    return df_new




links = ['https://www.cmegroup.com/markets/agriculture/livestock/lean-hogs.volume.html','https://www.cmegroup.com/markets/agriculture/livestock/feeder-cattle.volume.html','https://www.cmegroup.com/markets/agriculture/livestock/live-cattle.volume.html']
products = ['Lean Hog','Feeder Cattle','Live Cattle']
for i in range(0,3):
    df,date_text = Get_data(links[i])
    temp_df1 = data_transform(df,date_text)
    # temp_df1.to_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\code\OI\OI Data-'+products[i]+'.csv', index=False)

    temp_df2 = pd.read_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\code\OI\OI Data-'+products[i]+'.csv')
    main_df = pd.concat([temp_df2, temp_df1], ignore_index=False)

    # Save the updated DataFrame to a CSV file
    main_df.to_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\FF Codes\Futures-First\OI\OI Data-'+products[i]+'.csv', index=False)



df1 = pd.read_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\FF Codes\Futures-First\OI\OI Data-Lean Hog.csv')
df1.drop_duplicates(subset='Date', keep='last', inplace=True)
df2 = pd.read_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\FF Codes\Futures-First\OI\OI Data-Feeder Cattle.csv')
df2.drop_duplicates(subset='Date', keep='last', inplace=True)
df3 = pd.read_csv(r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\FF Codes\Futures-First\OI\OI Data-Live Cattle.csv')
df3.drop_duplicates(subset='Date', keep='last', inplace=True)

file_path = r'\\corp.hertshtengroup.com\Users\India\Data\anmol.chopra\Documents\FF Codes\Futures-First\OI\OI Data-3.xlsx'

wb = Workbook()

wb.save(file_path)

# Save dataframes to different sheets in the cleared Excel file
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
    df1.to_excel(writer, sheet_name='Lean Hog', index=False)
    df2.to_excel(writer, sheet_name='Feeder Cattle', index=False)
    df3.to_excel(writer, sheet_name='Soybean', index=False)