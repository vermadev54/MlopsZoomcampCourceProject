import argparse
import os
import pickle

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split




def dump_pickle(obj, filename):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)


def read_dataframe(filename: str):
    df = pd.read_csv(filename)
    return df


def preprocess(data: pd.DataFrame,\
               le_Gender: LabelEncoder,\
               le_Education_Level:LabelEncoder,\
               le_Marital_Status:LabelEncoder,\
               le_Income_Category:LabelEncoder,\
               le_Card_Category:LabelEncoder
              ):
    
    #fit encoder
    data['Gender_n'] = le_Gender.fit_transform(data['Gender'])
    data['Education_Level_n'] = le_Education_Level.fit_transform(data['Education_Level'])
    data['Marital_Status_n'] = le_Marital_Status.fit_transform(data['Marital_Status'])
    data['Income_Category_n'] = le_Income_Category.fit_transform(data['Income_Category'])
    data['Card_Category_n'] = le_Card_Category.fit_transform(data['Card_Category'])
    return data, le_Gender, le_Education_Level, le_Marital_Status, le_Income_Category, le_Card_Category 




def run(raw_data_path: str, dest_path: str, dataset: str = "green"):
    #initilize the encoder
    le_Gender = LabelEncoder()
    le_Education_Level = LabelEncoder()
    le_Marital_Status = LabelEncoder()
    le_Income_Category = LabelEncoder()
    le_Card_Category = LabelEncoder()
    
    # load parquet files
    data = read_dataframe(
        os.path.join(raw_data_path, f"credit_card_churn.csv")
    )
    
    data, le_Gender, le_Education_Level, le_Marital_Status, le_Income_Category, le_Card_Category = preprocess(data,\
                                                                                                             le_Gender,\
                                                                                                             le_Education_Level,\
                                                                                                             le_Marital_Status,\
                                                                                                             le_Income_Category,\
                                                                                                             le_Card_Category )
    
    
    data_n = data.drop(['Gender', 'Education_Level', 'Marital_Status', 'Income_Category', 'Card_Category'], axis = 1)
    data_n = data_n.drop('CLIENTNUM', axis = 1)
    train = data_n.drop('Attrition_Flag',  axis = 1)
    target = data_n['Attrition_Flag']
    
    
    train_ratio = 0.75
    validation_ratio = 0.15
    test_ratio = 0.10

    # train is now 75% of the entire data set
    # the _junk suffix means that we drop that variable completely
    x_train, x_test, y_train, y_test = train_test_split(train, target, test_size=1 - train_ratio)

    # test is now 10% of the initial data set
    # validation is now 15% of the initial data set
    x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, test_size=test_ratio/(test_ratio + validation_ratio)) 

    #print(x_train, x_val, x_test)    
    
   

    # create dest_path folder unless it already exists
    os.makedirs(dest_path, exist_ok=True)


    # save dictvectorizer and datasets
    dump_pickle(le_Gender, os.path.join(dest_path, "le_Gender.pkl"))
    dump_pickle(le_Education_Level, os.path.join(dest_path, "le_Education_Level.pkl"))
    dump_pickle(le_Marital_Status, os.path.join(dest_path, "le_Marital_Status.pkl"))
    dump_pickle(le_Income_Category, os.path.join(dest_path, "le_Income_Category.pkl"))
    dump_pickle(le_Card_Category, os.path.join(dest_path, "le_Card_Category.pkl"))
    dump_pickle((x_train, y_train), os.path.join(dest_path, "train.pkl"))
    dump_pickle((x_val, y_val), os.path.join(dest_path, "valid.pkl"))
    dump_pickle((x_test, y_test), os.path.join(dest_path, "test.pkl"))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data_path",
        help="the location where the raw NYC taxi trip data was saved"
    )
    parser.add_argument(
        "--dest_path",
        help="the location where the resulting files will be saved."
    )
    args = parser.parse_args()

    run(args.raw_data_path, args.dest_path)