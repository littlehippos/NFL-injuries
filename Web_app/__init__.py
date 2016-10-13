from flask import Flask
app = Flask(__name__)
from Web_app import views

# dnp_model=None
# dnp_features=None
# with open('Web_app/models/injury_class_model_play_or_no.pkl', 'rb') as fid:
#     dnp_model = cPickle.load(fid)
# with open('Web_app/models/injury_class_features_play_or_no.pkl', 'rb') as fid:
#     dnp_features = cPickle.load(fid)