# -*- coding: utf-8 -*-
import sys
import datetime
import json
import os
if os.name == 'nt':
    sys.path.append("H:/fbo-scraper")
from utils import fbo_nightly_scraper as fbo, get_fbo_attachments, predict 

def get_nightly_data():
    now = datetime.datetime.now() - datetime.timedelta(1)
    current_date = now.strftime("%Y%m%d")
    nfbo = fbo.NightlyFBONotices(date = current_date)
    file_name = nfbo.get_and_write_file()
    json_str = nfbo.pseudo_xml_to_json(file_name)
    nightly_data = json.loads(json_str)
    return nightly_data 


if __name__ == '__main__':
    print("-"*80)
    print("Downloading most recent nightly FBO file from FTP...")
    nightly_data = get_nightly_data()
    print("Done downloading most recent nightly FBO file from FTP!")

    print("-"*80)
    print("Getting attachments and their text from each FBO notice...")
    fboa = get_fbo_attachments.FboAttachments(nightly_data)
    updated_nightly_data = fboa.update_nightly_data()
    print("Done getting attachments and their text from each FBO notice!")

    print("-"*80)
    print("Making predictions for each notice attachment...")
    predict = predict.Predict(nightly_data)
    df = predict.predict()
    print("Done making predictions for each notice attachment!")
    