from src.core.database import db
from src.core.board.issue import Issue
from src.core.board.label import Label
from src.core.board.musician import Musician
from flask import request, jsonify, render_template
from marshmallow import Schema, fields


class MusicianSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    updated_at = fields.Date()
    inserted_at = fields.Date()
    
def list_issues():
    return Issue.query.all()


def create_issue(**kwargs):
    issue = Issue(**kwargs)
    db.session.add(issue)
    db.session.commit()

    return issue


def assign(issue, user):
    issue.user = user
    db.session.add(issue)
    db.session.commit()

    return issue


def assing_labels(issue, labels):
    issue.labels.extend(labels)
    db.session.add(issue)
    db.session.commit()

    return issue


def list_labels():
    return Label.query.all()


def create_label(**kwargs):
    label = Label(**kwargs)
    db.session.add(label)
    db.session.commit()

    return label

def list_musicians():
    schema = MusicianSchema(many=True)
    return jsonify(musician = schema.dump(Musician.query.all()))

def create_musician(**kwargs):
    musician = Musician(**kwargs)
    db.session.add(musician)
    db.session.commit()

    return musician

def find_musician_xss():
    params = request.args  
    if 'buscar' not in params:
        musician = Musician.query.filter(Musician.name == 'xss').first()
        schema = MusicianSchema()
        return render_template('xss.html', musician=schema.dump(musician))
    else:
        return render_template('xss.html', buscar=params['buscar'])

def find_musician_by_name():
    params = request.args
    schema = MusicianSchema()
    return jsonify(musician = schema.dump(Musician.query.filter(Musician.name.like(params['name']+'%')).first()))