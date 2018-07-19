# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 10:42:53 2018

@author: Faishal
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 12:23:50 2018

@author: Faishal
"""
from google.oauth2 import service_account
import googleapiclient.discovery
from google.auth.transport.requests import AuthorizedSession
import gspread
import pandas as pd
import sys
import logging
from sqlalchemy import create_engine
from flask import Flask, redirect, url_for, request, render_template 

app = Flask(__name__)

@app.route('/success/<name>,<int:work>')
def success(name, work):
    #Extract from Google Sheet
    scope = ['https://spreadsheets.google.com/feeds']
    
    #attach credential file from developer google (API)
    credentials = service_account.Credentials.from_service_account_file('file(API from gsheet).json', scopes=scope)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)
    
    #input gsheet ID
    #keysheet = request.args.get('keysheet')
    sheet = gc.open_by_key(name)
    
    #select number of sheet
    #worksheetid = request.args.get(0)
    worksheet = sheet.get_worksheet(work)
    list_of_lists = worksheet.get_all_values()
    
    #Transform
    names = sheet.title
    names = names.replace('xlsx', '').replace('xls', '').replace('csv', '').replace('.', '').replace('-', '_').replace(' ', '_').lower()
    
    suffixs = worksheet.title
    suffixs = suffixs.replace(' ', '_').replace('-', '_').lower()
    
    df = pd.DataFrame()
    df = df.append(list_of_lists)
    
    df.columns = df.iloc[0]
    mantap = df.reindex(df.index.drop(0))
    
    #Load to Table
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        conn = create_engine('postgresql://username:hostname:5432/password')
    except:
        logger.error("ERROR: Unexpected error: Could not connect to PostgreSQL instance.")
        sys.exit()

    logger.info("SUCCESS: Connection to RDS PostgreSQL instance succeeded")

    df.to_sql(name + '_' + suffix , conn, if_exists='replace', index=None)        
    return render_template('flask.html', tables=[mantap.head().to_html()], sheet=names, worksheet=suffixs, hasil=names + '_' + suffixs )

@app.route('/index',methods = ['POST', 'GET'])
def index():    
    return render_template('index.html')
   
@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['nm']
      no = request.form['num']
      return redirect(url_for('success', name = user, work = no))
   else:
      user = request.args.get('nm')
      no = request.args.get('num')
      return redirect(url_for('success', name = user, work = no))
      
if __name__ == '__main__':
   app.run(debug = True)
