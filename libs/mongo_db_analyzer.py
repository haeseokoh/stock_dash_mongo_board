import json
import traceback
import pandas as pd

from libs.mongo_api import db_init

def db_read_colums_data_form_option(db, col):
    columns = None
    col_option = None
    
    # 컬럼의 정보가 저장되어 있으면 저장된 정보를 바탕으로 재정렬하여 가져온다
    if db and col:
        db_config_inst = db_init(db, col + '_option')
        try:
            if hasattr(db_config_inst, 'db_col'):
                x = db_config_inst.db_col.find_one(filter={'value': 'columns'})
                # print('db_read_colums_data_form_option :',x)
                if x:
                    columns = x.get('option')
                    col_option = col + '_option'
        except Exception:
            print('----------- fail to read columns')
            traceback.print_exc()
            db_inst = db_init(db, col)
            columns = list(db_inst.find({}).next().keys())
            
    return columns, col_option
    

def db_read_colums_data(db, col, intermediate_value):
    columns = []

    d = json.loads(intermediate_value[0])
    print('db_read_colums_data prev intermediate_value:', d)

    # submit_button이 눌러 지지 않은 경우는 이전 값을 그대로 돌려보내고 유지 한다.
    # submit_button이 눌러지지 않아도 update_output에서 submit_button을 Output으로 처리 하고 있어 콜백이 호출이 된다
    if d['db'] == db and d['col'] == col:
        if 'columns' in d:
            return intermediate_value

    d['db'] = db
    d['col'] = col
    d['columns'], d['col_option'] = db_read_colums_data_form_option(db, col)
    
    intermediate_value = json.dumps(d)  # , ensure_ascii=False).encode('utf8')
    print('db_read_colums_data:', intermediate_value)
    
    return [intermediate_value]


def db_read_analyzer_data(db, col, intermediate_value):

    d = json.loads(intermediate_value[0])
    print('db_read_analyzer_data prev intermediate_value:', d)
    
    # submit_button이 눌러 지지 않은 경우는 이전 값을 그대로 돌려보내고 유지 한다.
    # submit_button이 눌러지지 않아도 update_output에서 submit_button을 Output으로 처리 하고 있어 콜백이 호출이 된다
    # if d['db'] == db and d['col'] == col:
    #     if 'columns' in d:
    #         return intermediate_value
    #
    # d['db'] = db
    # d['col'] = col
    
    # 컬럼의 정보가 저장되어 있으면 저장된 정보를 바탕으로 재정렬하여 가져온다
    if db and col:
        db_config_inst = db_init(db, col + '_option')
        
        try:
            x = db_config_inst.db_col.find_one(filter={'value': 'anlayze_db'})
            print(x)
            d['anlayze_db'] = x.get('option')
        except Exception:
            print('----------- fail to read anlayze_db')
            traceback.print_exc()
        
    intermediate_value = json.dumps(d)  # , ensure_ascii=False).encode('utf8')
    print('db_read_analyzer_data:', intermediate_value)
    
    return [intermediate_value]

def db_analyzer(db, col, intermediate_value):
    d = json.loads(intermediate_value[0])
    # db = db_init(d.get('db'), d.get('col'))
    db = db_init(db, col)
    total_size = 0
    
    options = []
    
    print('anlayze_db :', db)
    if hasattr(db, 'db_col'):
        total_size = db.db_col.count_documents({})
    
    if d.get('columns'):
        for x in d.get('columns'):
            try:
                unique = db.db_col.find().distinct(x)
                if '' in unique:
                    unique.remove('')
                if ' ' in unique:
                    unique.remove(' ')
                if None in unique:
                    unique.remove(None)
            
                unique_n = len(unique)
            except Exception:
                print('----------- {} fail to db.db_col.find().distinct(x) in db_analyzer'.format(x))
                traceback.print_exc()
                unique_n = 0
            
            if unique_n > 0:
                try:
                    print(x, type(unique[0]).__name__, unique_n, unique if unique_n < 100 else '카테고리로 분류 할 수 없습니다')
    
                    if type(unique[0]).__name__ in ['float', 'int']:
                        # https://stackoverflow.com/questions/50900220/get-min-and-max-value-in-single-query-in-mongodb
                        # min = db.db_col.find({}).sort(x, 1).limit(1)
                        # max = db.db_col.find({}).sort(x, -1).limit(1)
                        unique.sort()
                        max = unique[-1]
                        min = unique[0]
                        print('---- {} {}'.format(min, max))
                        # https://community.plotly.com/t/dash-range-slider-with-date/17915/9
                        # dcc.Slider(min=numdate[0],  # the first date
                        #            max=numdate[-1],  # the last date
                        #            value=numdate[0],  # default: the first
                        #            marks={numd: date.strftime('%d/%m') for numd, date in
                        #                   zip(numdate, df['DATE'].dt.date.unique())})
                        # ])
                        dropdown_src = json.dumps(
                            {'field': x, 'type': 'slider', 'options': {'min': min, 'max': max, 'value': [min, max]}})
                        options.append(
                            {"label": '{} (type:{}, items count:{})'.format(x, type(unique[0]).__name__, unique_n),
                             "value": dropdown_src})
                    elif type(unique[0]).__name__ in ['datetime']:
                        unique.sort()
                        max = unique[-1].isoformat()
                        min = unique[0].isoformat()
                        print('---- {} {}'.format(min, max))
                        dropdown_src = json.dumps(
                            {'field': x, 'type': 'date_picker', 'options': {'min': min, 'max': max, 'value': [min, max]}})
                        options.append(
                            {"label": '{} (type:{}, items count:{})'.format(x, type(unique[0]).__name__, unique_n),
                             "value": dropdown_src})
                    else:
                        if unique_n < 100:
                            dropdown_src = json.dumps(
                                {'field': x, 'type': 'select', 'options': [{'label': i, 'value': i} for i in unique]})
                            options.append(
                                {"label": '{} (type:{}, items count:{})'.format(x, type(unique[0]).__name__, unique_n),
                                 "value": dropdown_src})
                            print('--- option append', x, type(unique[0]).__name__, unique_n)
                        else:
                            # print('카테고리로 분류 할 수 없습니다')
                            result = db.db_col.aggregate([{
                                "$group": {
                                    "_id": '$' + x,
                                    "count": {"$sum": 1}
                                }
                            }])
                            
                            l_r = [{x: r["_id"], 'count': r["count"]} for r in result]
                            
                            df = pd.DataFrame(l_r)
                            # print(df)
                            df = df.sort_values(by=['count'], ascending=False)
                            print('************ more than >1 ***************')
                            f_df = df[df['count'] > 1]
                            # print('df.count :', f_df.count())
                            print('f_df.count :', len(f_df))
                            print(f_df)
                            # for i, row in df.iterrows():
                            #     print(i, row)
                            len_df = len(df)
                            if total_size / 10 > len_df:
                                src_list = f_df[x].to_list()
                                if len(src_list) > 100:
                                    src_list = src_list[:100]
                                print(src_list)
                                dropdown_src = json.dumps(
                                    {'field': x, 'type': 'select', 'options': [{'label': i, 'value': i} for i in src_list]})
                                options.append(
                                    {"label": '{} (type:{}, count of trim sorted items:{} from {})'.format(x,
                                                                                                   type(unique[0]).__name__,
                                                                                                   len(src_list), len_df),
                                     "value": dropdown_src})
                                print('--- option append', x, type(unique[0]).__name__, unique_n)
                except Exception:
                    try:
                        raise TypeError("Again !?!")
                    except:
                        pass
                    print('label {} {} {}'.format(x, type(unique[0]).__name__, unique_n))
                    print(unique)
                    traceback.print_exc()
        
        print('-------------options update-----------------')
        # pprint(options)
        db_option = db_init(d.get('db'), d.get('col') + '_option')
        db_option.db_col.create_index('value', unique=True)
        db_option.db_col.update_one({'value': 'anlayze_db'}, {"$set": {'value': 'anlayze_db', 'option': options}},upsert=True)
        
    return options, total_size