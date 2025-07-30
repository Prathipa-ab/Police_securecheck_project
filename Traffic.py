#import the required libraries
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, inspect

#Load the CSV file
traffic_df=pd.read_csv('D:/Police_Securecheck_project/traffic_stops - traffic_stops_with_vehicle_number.csv',low_memory=False)

# Object to Datetime data type conversion
traffic_df['stop_date'] = pd.to_datetime(traffic_df['stop_date'])
traffic_df['stop_time'] = pd.to_datetime(traffic_df['stop_time'],format='%H:%M:%S')

# Replaced NaN rows in Search_type with unknown 
traffic_df['search_type'].fillna('Unknown',inplace=True)

#Removed the redundant column
traffic_df.drop(['driver_age_raw', 'violation_raw'], axis=1, inplace=True)


#Create connection between python and SQL 
# Load the cleaned dataframe to the table traffic_stops in Police_securecheck_project database
user='postgres'
password='Prathipa%40123'
host='localhost'
database='Police_securecheck_project'
port='5432'
db_url=f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine=create_engine(db_url)
traffic_df.to_sql('traffic_stops',engine,index=False,if_exists='replace')

#title for the dashboard
st.title("🚨SecureCheck: Police Stop Dashboard")
st.markdown("Real-time analytics for vehicle stops and violations")

#summary 
st.subheader("📊 Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Stops", len(traffic_df))
col2.metric("Total Arrests", (traffic_df['is_arrested']==True).sum())
col3.metric("Drug-related Stops", (traffic_df['drugs_related_stop']==True).sum())

#values loaded into the selection box or sliders
st.header('Add new police log and Predict violation and Outcome')
date_options = ['--select--'] + [str(d) for d in traffic_df['stop_date'].dt.date.unique()]
stopdate = st.selectbox('Select the stop date:', date_options)

# slider for stop time 
traffic_df['stop_hour'] = pd.to_datetime(traffic_df['stop_time'], format='%H:%M %S').dt.hour
min_hour, max_hour = int(traffic_df['stop_hour'].min()), int(traffic_df['stop_hour'].max())
time_range = st.slider("Select stop time range (24 Hour):", min_hour, max_hour, (min_hour, max_hour))

countryname=st.selectbox('Select the countryname:',['--select--']+list(traffic_df['country_name'].unique()))
drivergender=st.selectbox('Select the gender:',['--select--']+list(traffic_df['driver_gender'].unique()))
driverrace=st.selectbox('Select the race:',['--select--']+list(traffic_df['driver_race'].unique()))

# slider for driver age
min_age, max_age = int(traffic_df['driver_age'].min()), int(traffic_df['driver_age'].max())  
age_range = st.slider("Select driver age range:", min_age, max_age, (min_age, max_age))

searchconducted = st.selectbox("Was search conducted?",['--select--']+list(['True', 'False']))
searchtypes = st.selectbox("Select search type:",['--select--']+list(traffic_df['search_type'].unique()))
drugrelated = st.selectbox("Is it a drug related stop?",['--select--']+list(['True', 'False']))
stopdurations = st.selectbox("Select stop duration:", ['--select--']+list(traffic_df['stop_duration'].unique()))
vehicles = st.selectbox("Select vehicle number:", ['--select--']+list(traffic_df['vehicle_number'].unique()))

#filter
filtered_df=traffic_df

if stopdate != '--select--':
    stopdate_obj = pd.to_datetime(stopdate).date()
    filtered_df = filtered_df[filtered_df['stop_date'].dt.date == stopdate_obj]

filtered_df=filtered_df[(traffic_df['stop_hour'] >= time_range[0]) &(traffic_df['stop_hour'] <= time_range[1])]
filtered_df=filtered_df[(traffic_df['driver_age'] >= age_range[0]) & (traffic_df['driver_age'] <= age_range[1])]
if countryname != '--select--':
    filtered_df=filtered_df[filtered_df['country_name']==(countryname)]
if driverrace != '--select--':
    filtered_df = filtered_df[filtered_df['driver_race']==(driverrace)]
if drivergender != '--select--':
    filtered_df = filtered_df[filtered_df['driver_gender']==(drivergender)]
if searchconducted != '--select--':
    val = True if searchconducted == 'True' else False
    filtered_df = filtered_df[filtered_df['search_conducted'] == val]
if drugrelated != '--select--':
    val = True if drugrelated == 'True' else False
    filtered_df = filtered_df[filtered_df['drugs_related_stop'] == val]
if searchtypes != '--select--':
    filtered_df = filtered_df[filtered_df['search_type']==(searchtypes)]
if stopdurations != '--select--':
    filtered_df = filtered_df[filtered_df['stop_duration']==(stopdurations)]
if vehicles != '--select--':
    filtered_df = filtered_df[filtered_df['vehicle_number']==(vehicles)]

#Prediction and Outcome
if st.button("Predict violation and outcome"):
    if len(filtered_df) == 0:
        st.warning("No data after filtering. Please adjust filters.")
    else:
        pred_violation = filtered_df['violation'].value_counts().idxmax()
        pred_outcome = filtered_df['stop_outcome'].value_counts().idxmax()

        st.success(f"Predicted Violation: {pred_violation}")
        st.success(f"Predicted Stop Outcome: {pred_outcome}")

st.write("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)


st.header("🚓 Police Stop Summary Report")
# Load vehicle number and create selectionbox:

selected_vehicle = st.selectbox("Select a vehicle number to view summary:", ['--select--']+ list(traffic_df['vehicle_number']))
if selected_vehicle!='--select--':
    query = f"""SELECT driver_age, driver_gender, stop_time, violation, search_conducted, stop_outcome, stop_duration, drugs_related_stop
    FROM traffic_stops WHERE vehicle_number = '{selected_vehicle}';"""
    df = pd.read_sql(query, engine)

    if not df.empty:
        row = df.iloc[0]
        age = row['driver_age']
        gender_raw = row['driver_gender']
        gender = "male" if gender_raw == "M" else "female"
        time = row['stop_time'].strftime('%I %p').lstrip('0')
        violation = row['violation']
        search = "search was conducted" if row['search_conducted'] else "no search was conducted"
        outcome = row['stop_outcome']
        duration = row['stop_duration']
        drug = "drug_related_stop" if row['drugs_related_stop'] else "not drug_related_stop"
        sentence = f"A {age}-year-old {gender} driver was stopped for {violation} at {time}. {search.capitalize()}, and he received {outcome}. The stop lasted {duration} and was {drug}."
        st.markdown(f"📝 **Summary:** {sentence}")
    else:
        st.warning("No record found for this vehicle.")
else:
    st.info("Please select a vehicle number.")

st.header('Advance Insights')

# SQL questions and its queries as Dict keys:values
questions={'Top 10 vehicle_Number involved in drug-related stops':'''SELECT vehicle_number
            FROM traffic_stops WHERE drugs_related_stop=True LIMIT 10;'''
           ,'Most frequently searched vehicles':'''SELECT vehicle_number 
            FROM traffic_stops WHERE search_conducted=True;''','Highest arrest rate driver age group':'''SELECT 
CASE
    WHEN driver_age < 25 THEN '<25'
    WHEN driver_age BETWEEN 25 AND 40 THEN '25–40'
    WHEN driver_age BETWEEN 41 AND 60 THEN '41–60'
    ELSE '>60'
  END AS age_group,
  ROUND( (SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::decimal / COUNT(*)) * 100, 2) AS arrest_rate_percentage
FROM traffic_stops
GROUP BY age_group
ORDER BY arrest_rate_percentage DESC limit 1;''','Gender distribution of drivers stopped in each country':'''SELECT country_name,
round((sum(case when driver_gender='M'then 1 Else 0 End)::decimal/count(*))*100,2) as male_percentage, round((sum(case when driver_gender='F'then 1 Else 0 End)::decimal/count(*))*100,2) as female_percentage
from traffic_stops
group by country_name;''', 'Highest search rate  race and gender combination':'''select driver_race, driver_gender,
round(((sum(case when search_conducted='True' then 1 else 0 end))::decimal/count(*))*100,2) as search_rate
from traffic_stops
group by driver_race, driver_gender
Order by search_rate limit 1;''','Time of day sees the most traffic stops':'''select  TO_CHAR(stop_time, 'HH12 AM') as Time
from traffic_stops
group by Time
order by count(*) desc limit 1;''', 'Average stop duration for different violations':'''select violation, round(avg(case stop_duration when '0-15 Min' then 7 when '16-30 Min' then 23 else 35 end),0) as average_stop_duration_mins
from traffic_stops
group by violation;''','Stops during the night more likely to lead to arrests':'''Select  Case
When night_arrest_rate > day_arrest_rate Then 'Yes'
else 'No'end as are_night_stops_more_likely_to_lead_to_arrests
from(Select
sum(case when time_period='Night' and is_arrested=True then 1 else 0 end) as night_arrest, 
sum(case when time_period='Day' and is_arrested=True then 1 else 0 end) as day_arrest,
round((sum(case when time_period='Night' and is_arrested= True then 1 else 0 end))::decimal/sum(case when time_period='Night' 
then 1 else 0 end)*100, 
0) as night_arrest_rate,
round((sum(case when time_period='Day' and is_arrested= True then 1 else 0 end))::decimal/sum(case when time_period='Day' 
then 1 else 0 end)*100
,0) as day_arrest_rate
from (Select *,
case
when extract(hour from stop_time)>= 20 or extract(hour from stop_time)<= 05 then 'Night' else 'Day' end as time_period
from traffic_stops))
''','Violations most associated with searches or arrests':'''
Select violation
from traffic_stops
where search_conducted=true or is_arrested=true
group by violation
order by count(*) desc limit 1;''', 'Violations most common among younger drivers (<25)':'''Select violation
from traffic_stops
where driver_age <25
group by violation
order by count(*)  desc limit 1;''','violation that rarely results in search or arrest':'''Select violation
from traffic_stops
group by violation
order by round((sum(case when search_conducted=true or is_arrested=true then 1 else 0 end)::decimal/count(*))*100,2)
 limit 1;''','Countries report the highest rate of drug-related stops':'''Select country_name, 
round((sum(case when drugs_related_stop=true then 1 else 0 end)::decimal/count(*))*100,2) as drugs_related_stop_rate
from traffic_stops
group by country_name
order by drugs_related_stop_rate desc limit 1;''','Arrest rate by country and violation':
'''Select country_name, violation,
round((sum(case when is_arrested=true then 1 else 0 end)::decimal/count(*))*100,2) as arrest_rate
from traffic_stops
group by country_name, violation
order by country_name, violation, arrest_rate desc;''','Which country has the most stops with search conducted':'''Select country_name, count(*) as Search_conducted_stops
from traffic_stops
where search_conducted=true
group by country_name
order by Search_conducted_stops desc limit 1;''' ,'Yearly Breakdown of Stops and Arrests by Country':'''Select *, rank() over(order by total_arrest desc)as rank_by_arrest
from (
SELECT  date_part('year',stop_date) as Year, country_name, count(*)as total_stops,
sum(case when is_arrested=true then 1 else 0 end) as total_arrest
from traffic_stops
group by  Year,country_name) as Yearly_data;''','Driver Violation Trends Based on Age and Race':'''
select age_details.age_group, ts.driver_race, ts.violation,
count(*) as Total_violation from traffic_stops ts join (select 
case  when driver_age <25 then '<25' 
when driver_age between 25 and 40 then '25-40'
when driver_age between 40 and 60 then '40-60'
else '>60' end as age_group, vehicle_number
from traffic_stops) as age_details on ts.vehicle_number = age_details.vehicle_number
group by age_details.age_group, ts.driver_race, ts.violation
order by Total_violation desc;''','Time Period Analysis of Stops':'''Select date_fn.Year, date_fn.Month, date_fn.Hour,count(*) as total_stops from traffic_stops ts join
(select date_part('year',stop_date) as Year, date_part('month',stop_date)as Month, 
to_char(stop_time, 'HH12 AM') AS Hour, vehicle_number
from traffic_stops)as date_fn on ts.vehicle_number= date_fn.vehicle_number
group by date_fn.Year, date_fn.Month, date_fn.Hour
order by total_stops desc;''','Violations with High Search and Arrest Rates':'''select 
max(case when search_rate_rank =1 then violation end) as High_search_rate_violation, 
max(case when arrest_rate_rank =1 then violation end) as High_arrest_rate_violation from (select violation,
round((sum(case when search_conducted=true then 1 else 0 end)::decimal/count(*))*100,2)as search_rate,
round((sum(case when is_arrested=true then 1 else 0 end)::decimal/count(*))*100,2)as arrest_rate,
rank() over (order by((sum(case when search_conducted=true then 1 else 0 end)::decimal/count(*))*100)desc) as search_rate_rank,
rank() over(order by((sum(case when is_arrested=true then 1 else 0 end)::decimal/count(*))*100)desc) as arrest_rate_rank
from traffic_stops
group by violation);''','Driver Demographics by Country':'''select country_name,
case  when driver_age <25 then '<25' 
when driver_age between 25 and 40 then '25-40'
when driver_age between 40 and 60 then '40-60'
else '>60' end as age_group,  driver_gender, driver_race, count(*)as total_stops
from traffic_stops
group by country_name, age_group,driver_race, driver_gender
order by total_stops desc;''','Top 5 Violations with Highest Arrest Rates': '''select violation,
round((sum(case when is_arrested=true then 1 else 0 end)::decimal/count(*))*100,2)as arrest_rate
from traffic_stops
group by violation
order by arrest_rate desc;'''
}

# questions dropdown
selected_question = st.selectbox('Select a query to run:',['--select--'] +list(questions.keys()))
if selected_question!='--select--':
    query = questions[selected_question]
    
    if st.button("Run Query"):
        df = pd.read_sql(query, engine)
        df=df.reset_index(drop=True)
        st.dataframe(df)
else:
    st.warning('Please select the question')