from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length

class OneWayTripFlightSearchForm(FlaskForm):
    departure_city = StringField("Departure City",
                                      validators=[DataRequired(), Length(min=3, max=30)])
    destination_city = StringField("Destination City",
                                      validators=[DataRequired(), Length(min=3, max=30)])
    adults = SelectField("Adults", choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    children = SelectField("Children", choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    infants = SelectField("Infants", choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    date_from = DateField("Departure date", validators=[DataRequired()])
    currency = SelectField("Currency", choices=[("CAD", "CAD"), ("USD", "USD"), ("EUR", "EUR")],
                           validators=[DataRequired()])
    submit = SubmitField("Submit")


class RoundTripFlightSearchForm(FlaskForm):
    departure_city = StringField("Departure City",
                                      validators=[DataRequired(), Length(min=3, max=30)])
    destination_city = StringField("Destination City",
                                      validators=[DataRequired(), Length(min=3, max=30)])
    adults = SelectField("Adults", choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    children = SelectField("Children", choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    infants = SelectField("Infants", choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
                           validators=[DataRequired()])
    date_from = DateField("Departure date", validators=[DataRequired()])
    date_to = DateField("Return date", validators=[DataRequired()])
    currency = SelectField("Currency", choices=[("CAD", "CAD"), ("USD", "USD"), ("EUR", "EUR")],
                           validators=[DataRequired()])
    submit = SubmitField("Submit")