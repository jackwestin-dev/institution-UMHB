import pandas as pd
import streamlit as st
from datetime import datetime, date
import hmac
import altair as alt

st.set_page_config(page_title='Institution UMHB Student Dashboard',layout='wide')

st.title('Institution UMHB - Student Dashboard')

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

## Read data from CSV files
df_engagement_attendance = pd.read_csv('./student-data/institution-umhb-engagement-data.csv',parse_dates=['start_date','end_date'])
df_engagement_attendance.rename(
    columns={
        'total_completed_passages_discrete_sets': 'completed_question_sets'
    },
    inplace=True
)
df_engagement_attendance['time_spent_hrs'] = (pd.to_timedelta(df_engagement_attendance['time_spent']).dt.total_seconds().div(3600).round(1))
df_engagement_attendance['attendance'] = df_engagement_attendance['num_attended_large_session'] / df_engagement_attendance['num_scheduled_large_session']


## Performance Class Average - Data Prep
df_engagement_attendance_weekly = df_engagement_attendance.groupby(['week']).agg(
    {
        'cars_accuracy':'mean',
        'sciences_accuracy':'mean',
        'class_accuracy':'mean',
        'attendance':'mean',
        'completed_lessons':'mean',
        'completed_question_sets':'mean',
        'time_spent_hrs':'mean'
    }
)

week_total = df_engagement_attendance_weekly.reset_index()['week'].max()
sciences_accuracy_latest_week = df_engagement_attendance_weekly.loc[week_total]['sciences_accuracy']
sciences_accuracy_first_week = df_engagement_attendance_weekly.loc[1]['sciences_accuracy']
sciences_accuracy_magnitude_change = sciences_accuracy_latest_week - sciences_accuracy_first_week


if sciences_accuracy_magnitude_change > 0:
    sciences_accuracy_directional_change = 'increased'
else:
    sciences_accuracy_directional_change = 'decreased'

cars_accuracy_latest_week = df_engagement_attendance_weekly.loc[week_total]['cars_accuracy']
cars_accuracy_first_week = df_engagement_attendance_weekly.loc[1]['cars_accuracy']
cars_accuracy_magnitude_change = cars_accuracy_latest_week - cars_accuracy_first_week

if cars_accuracy_magnitude_change > 0:
    cars_accuracy_directional_change = 'increased'
else:
    cars_accuracy_directional_change = 'decreased'
    
class_accuracy_weekly_min = df_engagement_attendance_weekly['class_accuracy'].min()
class_accuracy_weekly_max = df_engagement_attendance_weekly['class_accuracy'].max()

## Engagement - Attendance - Data Prep
attendance_weekly_min = df_engagement_attendance_weekly['attendance'].min()
attendance_weekly_max = df_engagement_attendance_weekly['attendance'].max()


## Create sections and render dashboard
st.write(' ')
st.write(' ')
st.header('Performance Class Average')
st.write(
    f'''
    Over the course of {week_total} weeks:
    * The scholar’s accuracy rates on their science questions (passage or discrete questions) {sciences_accuracy_directional_change} by {sciences_accuracy_magnitude_change:.0%} from {sciences_accuracy_first_week:.0%} to {sciences_accuracy_latest_week:.0%}.
    * The scholar’s accuracy rates on their CARS passages {cars_accuracy_directional_change} by {cars_accuracy_magnitude_change:.0%} from  {cars_accuracy_first_week:.0%} to {cars_accuracy_latest_week:.0%}.
    '''
)
st.write(' ')
st.write(' ')
st.dataframe(
    df_engagement_attendance_weekly[['cars_accuracy','sciences_accuracy','class_accuracy']].sort_values(by='week',ascending=False).style.format(
    {
        'cars_accuracy' : '{:.1%}',
        'sciences_accuracy' : '{:.1%}',
        'class_accuracy' : '{:.1%}'
    }
),
use_container_width=True
)

st.write(' ')
st.write(' ')
st.header('Average Participation Class Data')
st.write(' ')
st.write(' ')
st.subheader('Attendance')
st.write(' ')
st.write(' ')
st.dataframe(
    df_engagement_attendance_weekly[['attendance']].sort_values(by='week',ascending=False).style.format(
    {
        'attendance' : '{:.1%}'
    }
),
use_container_width=True
)
st.write(' ')
st.write(' ')
st.subheader('Engagement')
st.write(' ')
st.write(' ')
st.dataframe(df_engagement_attendance_weekly[['completed_lessons','completed_question_sets','time_spent_hrs']].sort_values(by='week',ascending=False).style.format(
    {
        'completed_lessons' : '{:,.1f}',
        'completed_question_sets' : '{:,.1f}',
        'time_spent_hrs' : '{:,.1f}'
    }
),
use_container_width=True
)
