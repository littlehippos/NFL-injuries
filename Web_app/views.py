from flask import render_template
from Web_app import app
import pandas as pd
from flask import request
from Models import Injurymodel, DNPmodel, create_pred_table, get_player_info, full_status_title, get_chart_data,full_position_title
import cPickle, sqlite3


DBNAME = 'Week5.db'


conn = sqlite3.connect('Web_app/models/{}'.format(DBNAME))
last_update = int(pd.read_sql_query("SELECT DISTINCT week_num FROM Injuries WHERE season == '2016' ", conn).max()[0])
pre_selection_week = 6
update_date = 'Oct 12, 2016'
conn.close()


@app.route('/')
def input_page():
    with open('Web_app/models/Players_2016.pkl', 'rb') as fid:
        players_2016 = cPickle.load(fid)
    players_list = sorted(players_2016['name_team_pos'].unique().tolist())
    return render_template("/front/index.html",
                           players_list = players_list,
                           max_available_data = last_update,
                           pre_selection_week = pre_selection_week,
                           last_update=last_update,
                           update_date = update_date)


@app.route('/demo1')
def demo():
    player = "Cam Newton, CAR, QB"
    injury_type = "Concussion"
    curr_week = "6"
    status = "Q"
    return render_template('demo.html',
                           player=player,
                           injury_type=injury_type,
                           curr_week=curr_week,
                           status=status,
                           pre_selection_week=pre_selection_week,
                           last_update=last_update,
                           update_date = update_date)


@app.route('/demo2')
def demo2():
    player = "Eddie Lacy, GNB, RB"
    injury_type = "Ankle"
    curr_week = "6"
    status = "Q"
    return render_template('demo.html',
                           player=player,
                           injury_type=injury_type,
                           curr_week=curr_week,
                           status=status,
                           pre_selection_week=pre_selection_week,
                           last_update = last_update,
                           update_date = update_date)


@app.route('/demo3')
def demo3():
    player = "Dez Bryant, DAL, WR"
    injury_type = "Knee"
    curr_week = "5"
    status = "D"
    return render_template('demo.html',
                           player=player,
                           injury_type=injury_type,
                           curr_week=curr_week,
                           status=status,
                           pre_selection_week=pre_selection_week,
                           last_update = last_update,
                           update_date = update_date)


@app.route('/demo4')
def demo4():
    player = "Carson Palmer, CRD, QB"
    injury_type = "Concussion"
    curr_week = "5"
    status = "D"
    return render_template('demo.html',
                           player=player,
                           injury_type=injury_type,
                           curr_week=curr_week,
                           status=status,
                           pre_selection_week=pre_selection_week,
                           last_update = last_update,
                           update_date = update_date)


@app.route('/demo5')
def demo5():
    player = "NaVorro Bowman, SFO, LB"
    injury_type = "Achilles"
    curr_week = "5"
    status = "O"
    return render_template('demo.html',
                           player=player,
                           injury_type=injury_type,
                           curr_week=curr_week,
                           status=status,
                           pre_selection_week=pre_selection_week,
                           last_update = last_update,
                           update_date = update_date)


@app.route('/output', methods=['GET', 'POST'])
def cesareans_output():
    conn = sqlite3.connect('Web_app/models/{}'.format(DBNAME))
    max_available_data2 = pd.read_sql_query("SELECT DISTINCT week_num FROM Injuries WHERE season == '2016' ", conn).max()

    player_info = request.form['player_info']
    injury_type = request.form['injury_type'].lower()
    curr_week = request.form['week']
    status = request.form['status'].capitalize()

    player_name = player_info.split(',')[0]
    position, team, season_stats = get_player_info(conn, player_name, curr_week, max_available_data2)

    # DNPmodel
    dnp_pred,prediction_prob = DNPmodel(injury_type, position, status)

    # Number of weeks off model: If dnp = 0, that means the player is predicted to play
    weeks_off_pred = Injurymodel(injury_type, position, status, dnp=1)

    if dnp_pred == 0:
        will_play = 'Yes'
        color='green'
    else:
        will_play = 'No'
        color='red'

    # Create table of status and predictions
    pred_table = create_pred_table(curr_week, status, injury_type, will_play, weeks_off_pred, season_stats)
    print '\n Prediction table'
    print pred_table

    # Create bar chart data
    chart_data = get_chart_data(position, injury_type, conn)
    status = full_status_title(status)
    position = full_position_title(position)

    conn.close()

    return render_template(
        "results/output.html",
        Chart_weeks = chart_data[0],
        Chart_played = chart_data[1],
        Chart_did_not_play = chart_data[2],
        player_info = player_info,
        curr_week = int(curr_week),
        injury = injury_type.capitalize(),
        name = player_name,
        position = position,
        weeks_off = weeks_off_pred,
        will_play = will_play,
        status = status,
        pred_table = pred_table,
        prediction_prob = int(prediction_prob),
        color=color,
        max_available_data = max_available_data2,
        last_update=last_update,
         update_date = update_date
    )


@app.route('/slides')
def slides():
    return render_template('front/slides.html')


