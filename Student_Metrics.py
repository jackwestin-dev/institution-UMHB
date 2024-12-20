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
df_engagement_attendance['time_spent_hrs'] = (pd.to_timedelta(df_engagement_attendance['time_spent']).dt.total_seconds().div(3600).round(1))
df_test_scores = pd.read_csv('./student-data/institution-umhb-test-data.csv',parse_dates=['test_date'])

## Create dashboard filters
student_id = st.selectbox("Choose a student:", list(df_engagement_attendance['student_id'].unique()))

## Transform dataframes
df_engagement_attendance_student_filtered = df_engagement_attendance[df_engagement_attendance['student_id'] == student_id]
df_engagement_attendance_student_filtered['num_attended_large_session_cumsum'] = df_engagement_attendance_student_filtered['num_attended_large_session'].cumsum()
df_engagement_attendance_student_filtered['num_scheduled_large_session_cumsum'] = df_engagement_attendance_student_filtered['num_scheduled_large_session'].cumsum()
df_engagement_attendance_student_filtered['num_attended_small_session_cumsum'] = df_engagement_attendance_student_filtered['num_attended_small_session'].cumsum()
df_engagement_attendance_student_filtered['num_scheduled_small_session_cumsum'] = df_engagement_attendance_student_filtered['num_scheduled_small_session'].cumsum()
df_engagement_attendance_student_filtered['large_session'] = df_engagement_attendance_student_filtered['num_attended_large_session_cumsum'] / df_engagement_attendance_student_filtered['num_scheduled_large_session_cumsum']
df_engagement_attendance_student_filtered['small_session'] = df_engagement_attendance_student_filtered['num_attended_small_session_cumsum'] / df_engagement_attendance_student_filtered['num_scheduled_small_session_cumsum']

df_test_scores['test_date'] = df_test_scores['test_date'].dt.date
df_test_scores_student_filtered = df_test_scores[df_test_scores['student_id'] == student_id]

## Create sections and render dashboard
st.write(' ')
st.write(' ')

st.header('Engagement')
st.subheader('Completed Lessons')

st.write(' ')
st.write(' ')

line_engagement = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
        ['completed_lessons', 'completed_mandatory_lessons'],
        as_=['variable', 'value']
    ).encode(
        x=alt.X(
            'week:O',
            axis=alt.Axis(
                labelAngle=0,
                title='Week'
            )
        ),
        y=alt.Y(
            'value:Q',
            axis=alt.Axis(
                title='Completed Count',
            )
        ),
        tooltip=[
            alt.Tooltip('week:O',title='Week'),
            alt.Tooltip('value:Q',title='Completed Count')
        ],
        color=alt.Color(
            'variable:N',
            legend=alt.Legend(
                title='Type',
                orient='bottom',
                labelExpr="datum.value == 'completed_lessons' ? 'Lessons' : 'Mandatory Lessons'"
            )
        )
)

st.altair_chart(line_engagement,use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Percentage of Mandatory Lessons Completed')

st.write (' ')
st.write (' ')

line_time_pct_mandatory_completed = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'percentage_mandatory_complete',
        axis=alt.Axis(
            title='% Mandatory Lessons Completed',
            format='%'
        )
    ),
    tooltip=[
            alt.Tooltip('week:O',title='Week'),
            alt.Tooltip('percentage_mandatory_complete',title='Pct Mandatory Lessons Complete',format='0.1%')
    ],
)

st.altair_chart(line_time_pct_mandatory_completed, use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Completed Questions Sets')

st.write(' ')
st.write(' ')

line_question_sets = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'total_completed_passages_discrete_sets',
        axis=alt.Axis(
            title='Completed Count'
        )
    ),
    tooltip=[
            alt.Tooltip('week:O',title='Week'),
            alt.Tooltip('total_completed_passages_discrete_sets',title='Completed Count')
    ],
)

st.altair_chart(line_question_sets,use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Time Spent (Hrs)')
st.write('_Includes the time spent on self-paced course video content_')

st.write (' ')
st.write (' ')

line_time_spent = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'time_spent_hrs',
        axis=alt.Axis(
            title='Time Spent (Hrs)'
        )
    ),
    tooltip=[
            alt.Tooltip('week:O',title='Week'),
            alt.Tooltip('time_spent_hrs',title='Time Spent (Hrs)')
    ],
)

st.altair_chart(line_time_spent, use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Attendance')

st.write(' ')
st.write(' ')

line_attendance = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
    fold=['large_session','small_session'],
    as_=['variable','value']
).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Cumulative Attendance Rate',
            format='%'
        )
    ),
    tooltip=[
        alt.Tooltip('week:O',title='Week'),
        alt.Tooltip('value:Q',title='Cumulative Attendance Rate',format='0.1%')
    ],
    color=alt.Color(
        'variable:N',
        legend=alt.Legend(
            title='Session Size',
            orient='bottom',
            labelExpr="datum.value == 'large_session' ? 'Workshop' : 'Office Hours'"
        )
    )
)

st.altair_chart(line_attendance,use_container_width=True)

st.write(' ')
st.write(' ')

st.header('Performance')
st.subheader('Accuracy')
st.write(' ')
st.write(' ')

line_accuracy = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
    fold=['sciences_accuracy', 'cars_accuracy','class_accuracy'], 
    as_=['variable', 'value']
).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Accuracy Score',
            format='%'
        )
    ),
    tooltip=[
        alt.Tooltip('week:O',title='Week'),
        alt.Tooltip('value:Q',title='Accuracy Rate',format='0.1%')
    ],
    color=alt.Color('variable:N',legend=alt.Legend(title='Subject',orient='bottom'))
)

st.altair_chart(line_accuracy,use_container_width=True)

st.write(' ')
st.write(' ')
st.header('Practice Exams')
st.write(' ')
st.write(' ')

st.dataframe(df_test_scores_student_filtered[['test_name','test_date','actual_exam_score','low_predicted_exam_score','high_predicted_exam_score']],use_container_width=True)
st.write(' ')
st.write(' ')

point_exam_scores = alt.Chart(df_test_scores_student_filtered).mark_point().transform_fold(
    fold=['actual_exam_score','low_predicted_exam_score','high_predicted_exam_score'],
    as_=['variable','value']
).encode(
    x=alt.X(
        'yearmonthdate(test_date):O',
        axis=alt.Axis(
            labelAngle=-45,
            title='Test Date'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Exam Score'
        ),
        scale=alt.Scale(domain=[470, 528])
    ),
    color=alt.Color('variable:N',legend=alt.Legend(title='Range',orient='bottom'))
)

st.altair_chart(point_exam_scores,use_container_width=True)