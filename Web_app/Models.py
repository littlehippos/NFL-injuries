import cPickle
import pandas as pd
from flask import g


def get_dnp_model():
    dnp_model = getattr(g, '_dnp_model', None)
    if dnp_model is None:
        # 'Football-data/Models/Model_1.pkl'
        with open('Web_app/models/injury_class_model_play_or_no.pkl', 'rb') as fid:
            dnp_model = g._dnp_model = cPickle.load(fid)
    return dnp_model


def get_dnp_features():
    dnp_features = getattr(g, '_dnp_features', None)
    if dnp_features is None:
        # 'Football-data/Models/Model_1_features.pkl'
        with open('Web_app/models/injury_class_features_play_or_no.pkl', 'rb') as fid:
            dnp_features = g._dnp_features = cPickle.load(fid)
    return dnp_features


def get_model_2a():
    model_2a = getattr(g, '_model_2a', None)
    if model_2a is None:
        # 'Football-data/Models/Model_2a_dnp_false.pkl'
        with open('Web_app/models/injury_reg_model_played.pkl', 'rb') as fid:
            model_2a = g._model_2a = cPickle.load(fid)
    return model_2a


def get_model_2a_features():
    model_2a_features = getattr(g, '_model_2a_features', None)
    if model_2a_features is None:
        # 'Football-data/Models/Model_2a_dnp_false_features.pkl'
        with open('Web_app/models/injury_reg_model_played_features.pkl', 'rb') as fid:
            model_2a_features = g._model_2a_features = cPickle.load(fid)
    return model_2a_features


def get_model_2b():
    model_2b = getattr(g, '_model_2b', None)
    if model_2b is None:
        # 'Football-data/Models/Model_2b_dnp_true.pkl'
        with open('Web_app/models/injury_reg_model2.pkl', 'rb') as fid:
            model_2b = g._model_2b = cPickle.load(fid)
    return model_2b


def get_model_2b_features():
    model_2b_features = getattr(g, '_model_2b_features', None)
    if model_2b_features is None:
        # 'Football-data/Models/Model_2b_dnp_true_features.pkl'
        with open('Web_app/models/injury_reg_features2.pkl', 'rb') as fid:
            model_2b_features = g._model_2b_features = cPickle.load(fid)
    return model_2b_features


def get_player_info(conn, player_name, curr_week, max_available_data):
    print player_name, '\n'

    sql_query = """ SELECT DISTINCT position, team FROM Injuries
                WHERE name == '{}' """.format(player_name)
    query_results = pd.read_sql_query(sql_query, conn)
    position = query_results['position'].iloc[0]
    team = query_results['team'].iloc[0]

    season_stats = []
    for i in range(1, int(curr_week)):
        tmp = {'Week': 1, 'Status': 'NA', 'Injury': 'NA', 'Prediction_to_play': 'NA'}

        sql_query = """SELECT DISTINCT week_num, injury_type, status, dnp
                    FROM Injuries
                    WHERE season == '2016'
                    and name == '{}'
                    and week_num == '{}' """.format(player_name, i)
        query_results = pd.read_sql_query(sql_query, conn)


        if i == 1:
            print query_results
        try:
            tmp['Week'] = i
            tmp['Status'] = query_results['status'].iloc[0].capitalize()
            tmp['Injury'] = query_results['injury_type'].iloc[0].capitalize()
            dnp = query_results['dnp'].iloc[0]
            if dnp == '0':
                will_play = 'Yes'
            else:
                will_play = 'No'
            tmp['Prediction_to_play'] = will_play
        except:
            if i <= int(max_available_data):
                tmp['Week'] = i
                tmp['Status'] = 'None'
                tmp['Injury'] = 'None'
                tmp['Prediction_to_play'] = 'Yes'

        season_stats.append(tmp)

    print '\n Season stats', season_stats

    return position, team, season_stats


def DNPmodel(injury_type, position, status):
    forest_loaded = get_dnp_model()
    features = get_dnp_features()

    df = pd.DataFrame(0, columns=features, index=[0])

    feature1 = "position_{}".format(position)
    feature2 = "injury_type_{}".format(injury_type.lower())
    feature3 = "status_{}".format(status)

    df[feature1] = 1
    df[feature2] = 1
    df[feature3] = 1

    prediction = forest_loaded.predict(df)
    prediction_prob = forest_loaded.predict_proba(df)[0][int(prediction)]
    print '\n prediction probability', prediction_prob, type(prediction_prob)
    return prediction[0], prediction_prob*100



def Injurymodel(injury_type, position, status, dnp):
    if dnp == 0:
        forest_loaded = get_model_2a()
        features = get_model_2a_features()
    elif dnp == 1:
        forest_loaded = get_model_2b()
        features = get_model_2b_features()

    df = pd.DataFrame(0, columns=features, index=[0])

    feature1 = "position_{}".format(position)
    feature2 = "injury_type_{}".format(injury_type)
    feature3 = "status_{}".format(status)

    df[feature1] = 1
    df[feature2] = 1
    df[feature3] = 1

    prediction = forest_loaded.predict(df)

    return round(prediction, 1)


def create_pred_table(curr_week, curr_status, curr_injury, dnp_pred, weeks_pred, season_stats):

    pred_table = season_stats

    # Forecast how many more weeks that weeks_pred will be true
    weeks_forward = 0
    for pred in pred_table:
        if pred['Status'].lower() == curr_status.lower() and pred['Injury'].lower() == curr_injury.lower():
            weeks_forward += 1
    print '\n weeks forward', weeks_forward

    last_week_predicted = int(curr_week) + int(weeks_pred)-weeks_forward
    print '\n last_week_predicted', last_week_predicted

    for i in range(int(curr_week),last_week_predicted+1):
        tmp = {'Week': 0, 'Status': 'Unknown', 'Injury': 'Unknown', 'Prediction_to_play': 'Unknown', 'color': 'Grey'}
        tmp['Week'] = i
        tmp['Status'] = curr_status.capitalize()
        tmp['Injury'] = curr_injury.capitalize()

        print 'tmp', i, dnp_pred
        if i == int(curr_week):
            tmp['Prediction_to_play'] = "{} *".format(dnp_pred)

        pred_table.append(tmp)
    print pred_table
    return sorted(pred_table, key = lambda x: x['Week'],reverse = True)


def full_status_title(status):
    Status = {'P': "Probable", "Q": "Questionable", "D": "Doubtful", "S": "Suspended",
              "PUP": "Physically Unable to Play", "IR": "Injured Reserve", "O": "Out"}
    return "{} ({})".format(Status[status], status)

def full_position_title(position):
    Position = {"WR": "Wide receiver", "QB": "Quarterback", "TE": "Tight end", "DB" : "Defensive back",
                "LB": "Linebacker", "RB": "Running back", "C": "Center", "CB": "Corner back",
                "LG": "Left guard", "G": "Guard", "DT": "Defensive tackle", "OLB": "Outside linebacker"}
    try:
        return "{}".format(Position[position],position)
    except:
        return position

def get_chart_data(position, injury_type, conn):
    df = pd.read_sql_query(""" SELECT  a.injury_type_tot_consec_season as duration, a.dnp as did_not_play, AVG(a.test) as average_per_year FROM
        (SELECT season, injury_type_tot_consec_season, dnp, COUNT (*) as test FROM Injuries
        WHERE position = '{}' AND injury_type = '{}' AND dnp_pre_consec_season IS NULL AND season != '2016'
        GROUP BY season, injury_type_tot_consec_season, dnp) a GROUP BY  a.injury_type_tot_consec_season, a.dnp
        """.format(position, injury_type), conn)

    print '\n Get chart data'
    df['perc_average_per_year'] = df['average_per_year'].div(df['average_per_year'].sum())*100
    df['average_per_year'] = df['perc_average_per_year']
    print df

    p_dict = df[df['did_not_play'] != '1'][['duration', 'average_per_year']]
    p_dict = p_dict.set_index('duration')['average_per_year'].to_dict()

    dnp_dict = df[df['did_not_play'] == '1'][['duration', 'average_per_year']]
    dnp_dict = dnp_dict.set_index('duration')['average_per_year'].to_dict()

    dnp_results = {}
    p_results = {}
    for weeks_off in range(1, 17):
        dnp_results[weeks_off] = dnp_dict.get(weeks_off, 0)
        p_results[weeks_off] = p_dict.get(weeks_off, 0)

    print '\n dnp results', sorted(tuple(dnp_results.items()))
    print '\n p results', p_results

    # dnp_results_cum = cumsum([i[1] for i in tuple(dnp_results.items())])
    # p_results_cum = cumsum([i[1] for i in tuple(p_results.items())])

    Weeks_data = ",".join(map(lambda x: str(x), range(1, 17)))
    Played = ",".join(map(lambda x: str(x), [v for k, v in p_results.items()]))
    Did_not_play = ",".join(map(lambda x: str(x), [v for k, v in dnp_results.items()]))

    # Weeks_data = ",".join(map(lambda x: str(x), range(1, 17)))
    # Played = ",".join(map(lambda x: str(x), dnp_results_cum))
    # Did_not_play = ",".join(map(lambda x: str(x), p_results_cum))

    return [Weeks_data, Played, Did_not_play]

