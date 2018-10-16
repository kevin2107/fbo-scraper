import os
import dill as pickle
import pandas as pd
import json
import re
import string


class Predict():
    '''
    Make 508 accessibility predictions based on fbo notice attachment texts.

    Parameters:
        json_data (dict): The JSON of a nightly fbo file, where each notice
                          has its attachments and their text.
    '''

    def __init__(self, json_data):
        self.json_data = json_data


    @staticmethod
    def transform_text(text):
        '''
        Strip punctuation and some common string formatting.

        Parameters:
            text (str): a string

        Returns:
            stripped_text (str): a string
        '''

        def remove_punctuation(text):
            regex = re.compile('[%s]' % re.escape(string.punctuation))
            s = regex.sub(' ', text)
            return s

        def remove_formatting(text):
            output = text.replace('\t', ' ').\
                          replace('\n', ' ').\
                          replace('\r', ' ').\
                          replace('\x0b', ' ').\
                          replace('\x0c', ' ')
            return output

        stripped_punctuation = remove_punctuation(text)
        stripped_text = remove_formatting(stripped_punctuation)
        return stripped_text


    @staticmethod
    def json_to_df(json_data):
        '''
        Converts the JSON of a nightly fbo file (with attachment texts) into a
        pandas dataframe.

        Arguments:
            json_data: refer to self.json_data

        Returns:
            df (pandas DataFrame): a pandas dataframe
        '''

        sol_number_keys = ['solnbr','awdnbr','linenbr','modnbr','donbr']
        texts = []
        attch_urls = []
        notice_numbers = []
        notice_types = []
        fbo_urls = []
        for notice_type in json_data:
            notices = json_data[notice_type]
            if not notices:
                continue
            else:
                for notice in notices:
                    if 'attachments' in notice:
                        notice_number_key = [x for x in notice if x in sol_number_keys][0]
                        try:
                            fbo_url = notice['url']
                        except:
                            # if there's no url, then what are we doing in here?!
                            continue
                        fbo_urls.append(fbo_url)
                        try:
                            notice_number = notice[notice_number_key]
                        except KeyError:
                            notice_number = ''
                        notice_numbers.append(notice_number)
                        attachments = notice['attachments']
                        #merged_attachment_dict = {k:v for d in attachments for k,v in d.items()}
                        for k in attachments:
                            attachment = attachments[k]
                            text = attachment['text']
                            texts.append(text)
                            attch_url = attachment['url']
                            attch_urls.append(attch_url)
        df = pd.DataFrame([notice_types,
                           notice_numbers,
                           fbo_urls,
                           attch_urls,
                           texts]).transpose()
        df.columns = ['notice type',
                      'notice number',
                      'notice url',
                      'attachment url',
                      'text']
        return df


    def predict(self):
        '''
        Convert FBO JSON into a dataframe, make predictions, return dataframe.

        Arguments:
            self

        Returns:
            df: a pandas DataFrame
        '''
        df = Predict.json_to_df(self.json_data)
        df['text'] = df['text'].astype(str)
        df['normalized_text'] = df['text'].apply(Predict.transform_text)
        with open('binaries/best_clf_scott.pkl', 'rb') as f:
            pickled_model = pickle.load(f)
        df['prediction'] = pickled_model.predict(df['normalized_text'])
        dec_func = pickled_model.decision_function(df['normalized_text'])
        decision_boundary_distance = abs(dec_func)
        df['decision boundary distance'] = decision_boundary_distance
        df = df.drop(labels=['text','normalized_text'], axis=1)
        return df

if __name__=='__main__':
    with open('nightly_files/fbo_nightly_20180506.json') as f:
        json_str = json.load(f)
        json_data = json.loads(json_str)
    predict = Predict(json_data)
    df = predict.predict()
    print(df['decision boundary distance'].value_counts())