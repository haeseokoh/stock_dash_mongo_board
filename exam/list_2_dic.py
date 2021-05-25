import re

check = \
    {'$and': [
        {'$and': [
            {'과제명': {'$regex': re.compile('.*(?=.*gal).*', re.IGNORECASE)}}, {'과제명': {'$regex': re.compile('.*(?=.*a).*', re.IGNORECASE)}}
        ]},
        {'$or': [{'개발모델명': {'$regex': re.compile('.*(?=.*sm-t).*', re.IGNORECASE)}}]}]}

my_list=[{'과제유형':['Smart/Tablet', 'OS UP', '기타(Mobile)']},{'등급':['D0', 'BL', 'RC']},]

my_list.to_dic