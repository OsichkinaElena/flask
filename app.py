import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

engine = create_engine('postgresql://postgres:rossiyanka@127.0.0.1:5432/flask')
Base = declarative_base()
Session = sessionmaker(bind=engine)

app = Flask('app')

class HTTPError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

@app.errorhandler(HTTPError)
def hendle_error(error):
    response = jsonify({
        'message': error.message
    })
    response.status_code = error.status_code
    return response

def validate(inout_model, output_model):
    try:
        return output_model(**inout_model).dict()
    except pydantic.error_wrappers.ValidationError as er:
        raise HTTPError(400, er.errors())


class Ads(Base):
    __tablename__ = 'Ads'
    id = Column(Integer, primary_key=True)
    header = Column(String)
    description = Column(String)
    create_date = Column(DateTime, server_default=func.now())
    owner = Column(String)

    def to_dict(self):
        return {
            'header': self.header,
            'deccription': self.description,
            'owner': self.owner,
            'create_date': int(self.create_date.timestamp())
        }

Base.metadata.create_all(engine)


class AdsModel(pydantic.BaseModel):
    header: str
    description: str
    owner: str

class AdsView(MethodView):
    def get(self, id):
        with Session() as session:
            advt = session.query(Ads).get(id)
            if advt is None:
                raise HTTPError(404, 'advt not found')
            return jsonify(advt.to_dict())


    def post(self):
        advt_date = validate(request.json, AdsModel)
        with Session() as session:
            new_advt = Ads(**advt_date)
            session.add(new_advt)
            session.commit()
            return jsonify(new_advt.to_dict())

    def delete(self, id):
        with Session() as session:
            advt = session.query(Ads).get(id)
            if advt is None:
                raise HTTPError(404, 'advt not found')
            session.delete(advt)
            session.commit()
            return jsonify(advt.to_dict())
        

app.add_url_rule('/ads/', methods=['POST'], view_func=AdsView.as_view('create_advt'))
app.add_url_rule('/ads/<int:id>/', methods=['GET'], view_func=AdsView.as_view('get_advt'))
app.add_url_rule('/ads/<int:id>/', methods=['DELETE'], view_func=AdsView.as_view('delete_advt'))
app.run()

