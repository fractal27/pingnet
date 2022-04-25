import pandas as pd

def main():
    #get the path of the database file
    # db_file=os.path.join(os.path.dirname(__file__),'tempi.db')
    json_df=pd.read_json("times.json")
    html_df=pd.read_html("times.html")
    xlsx_df=pd.read_excel("times.xlsx")
    print("times.csv:",pd.read_csv("times.csv"))
    print("times.json:",json_df)
    print("times.html:",html_df)
    print("times.xmls(excel):",xlsx_df)

if __name__=='__main__':
    main()
