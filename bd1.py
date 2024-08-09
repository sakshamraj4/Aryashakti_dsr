import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
from sqlalchemy import create_engine

# Database configuration
db_config = {
    'dbname': 'testdb',
    'user': 'avijeet@indiabounds',
    'password': '23;ZcV$NAC',
    'host': 'indiabounds.postgres.database.azure.com',
    'port': 5432
}

def create_db_engine():
    return create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

@st.cache_data
def load_data():
    try:
        engine = create_db_engine()
        query = "SELECT * FROM dsr_activity"
        data = pd.read_sql(query, engine)
        return data
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return pd.DataFrame()

data = load_data()

data['date'] = pd.to_datetime(data['date'], errors='coerce')
data['follow_up_date'] = pd.to_datetime(data['follow_up_date'], errors='coerce')
data['ah_review_date'] = pd.to_datetime(data['ah_review_date'], errors='coerce')

users = {
    'bdview': {'password': 'bd@arya', 'role': 'view'},
    'adminview': {'password': 'admin@arya', 'role': 'admin'}
}

def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return users[username]['role']
    return None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.role = None

def handle_login():
    role = authenticate(st.session_state.username, st.session_state.password)
    if role:
        st.session_state.logged_in = True
        st.session_state.role = role
        st.session_state.username = ""
        st.session_state.password = ""
        st.rerun()  # Refresh the page to reflect the new state

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.role = None
    st.rerun()  # Refresh the page to reflect the new state

if st.session_state.logged_in:
    role = st.session_state.role
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    st.title('DSR Activity Dashboard')

    view_type = st.sidebar.radio("Select View", ["Summary View", "Detailed Data View"])

    if view_type == "Summary View":
        st.header("Summary View")
        today = pd.Timestamp.today().normalize()
        yesterday = today - pd.Timedelta(days=1)
        last_week = today - pd.Timedelta(days=7)
        first_day_of_month = today.replace(day=1)
        last_month = first_day_of_month - pd.Timedelta(days=1)
        first_day_of_last_month = last_month.replace(day=1)
        today_data = data[data['date'] == today]
        yesterday_data = data[data['date'] == yesterday]
        last_week_data = data[(data['date'] >= last_week) & (data['date'] <= today)]
        this_month_data = data[(data['date'] >= first_day_of_month) & (data['date'] <= today)]
        last_month_data = data[(data['date'] >= first_day_of_last_month) & (data['date'] <= last_month)]
        st.subheader("DSR Activity Summary")
        st.write(f"**DSR Activity Done Today:** {len(today_data)}")
        st.write(f"**DSR Activity Done Yesterday:** {len(yesterday_data)}")
        st.write(f"**DSR Activity Done Last Week:** {len(last_week_data)}")
        st.write(f"**DSR Activity Done This Month:** {len(this_month_data)}")
        st.write(f"**DSR Activity Done Last Month:** {len(last_month_data)}")
        st.subheader("Status of Case Distribution")
        status_counts = data['status_of_case'].value_counts().reset_index()
        status_counts.columns = ['status_of_case', 'count']
        status_pie_chart = px.pie(status_counts, names='status_of_case', values='count', title='Status of Case', hole=0)
        st.plotly_chart(status_pie_chart)
        st.subheader("Type of Meeting Distribution")
        meeting_type_counts = data['type_of_meeting'].value_counts().reset_index()
        meeting_type_counts.columns = ['type_of_meeting', 'count']
        meeting_type_pie_chart = px.pie(meeting_type_counts, names='type_of_meeting', values='count', title='Type of Meeting', hole=0)
        st.plotly_chart(meeting_type_pie_chart)
        st.subheader("Product Distribution")
        product_counts = data['product'].value_counts().reset_index()
        product_counts.columns = ['product', 'count']
        product_pie_chart = px.pie(product_counts, names='product', values='count', title='Product', hole=0)
        st.plotly_chart(product_pie_chart)
        st.subheader("Commodity Distribution")
        commodity_counts = data['commodity'].value_counts().reset_index()
        commodity_counts.columns = ['commodity', 'count']
        commodity_bar_chart = px.bar(commodity_counts, x='commodity', y='count', title='Commodity Distribution')
        commodity_bar_chart.update_xaxes(title_text='Commodity')
        commodity_bar_chart.update_yaxes(title_text='Count')
        st.plotly_chart(commodity_bar_chart)

    else:
        st.header("Detailed Data View")
        st.sidebar.subheader('Filters')
        state_filter = st.sidebar.multiselect(
            'Select State', 
            options=['All'] + list(data['state'].unique()), 
            default=['All']
        )
        bd_name_filter = st.sidebar.multiselect(
            'Select BD Name', 
            options=['All'] + list(data['bd_name'].unique()), 
            default=['All']
        )
        month_filter = st.sidebar.multiselect(
            'Select Month', 
            options=['All'] + list(data['month'].unique()), 
            default=['All']
        )
        client_filter = st.sidebar.multiselect(
            'Select Client Name', 
            options=['All'] + list(data['client_name'].unique()), 
            default=['All']
        )
        designation_filter = st.sidebar.multiselect(
            'Select Designation of Person Met', 
            options=['All'] + list(data['designation_of_person_met'].unique()), 
            default=['All']
        )
        processor_type_filter = st.sidebar.multiselect(
            'Select If Processor, Type', 
            options=['All'] + list(data['if_processor_type'].unique()), 
            default=['All']
        )
        commodity_filter = st.sidebar.multiselect(
            'Select Commodity', 
            options=['All'] + list(data['commodity'].unique()), 
            default=['All']
        )
        product_filter = st.sidebar.multiselect(
            'Select Product', 
            options=['All'] + list(data['product'].unique()), 
            default=['All']
        )
        status_of_case_filter = st.sidebar.multiselect(
            'Select Status of Case', 
            options=['All'] + list(data['status_of_case'].unique()), 
            default=['All']
        )

        def apply_filters(df):
            filtered_df = df.copy()
            if 'All' not in state_filter:
                filtered_df = filtered_df[filtered_df['state'].isin(state_filter)]
            if 'All' not in bd_name_filter:
                filtered_df = filtered_df[filtered_df['bd_name'].isin(bd_name_filter)]
            if 'All' not in month_filter:
                filtered_df = filtered_df[filtered_df['month'].isin(month_filter)]
            if 'All' not in client_filter:
                filtered_df = filtered_df[filtered_df['client_name'].isin(client_filter)]
            if 'All' not in designation_filter:
                filtered_df = filtered_df[filtered_df['designation_of_person_met'].isin(designation_filter)]
            if 'All' not in processor_type_filter:
                filtered_df = filtered_df[filtered_df['if_processor_type'].isin(processor_type_filter)]
            if 'All' not in commodity_filter:
                filtered_df = filtered_df[filtered_df['commodity'].isin(commodity_filter)]
            if 'All' not in product_filter:
                filtered_df = filtered_df[filtered_df['product'].isin(product_filter)]
            if 'All' not in status_of_case_filter:
                filtered_df = filtered_df[filtered_df['status_of_case'].isin(status_of_case_filter)]
            return filtered_df

        st.subheader('Filtered Data')
        filtered_data = apply_filters(data)
        if filtered_data.empty:
            st.write("No records found for the selected filters.")
        else:
            for index, row in filtered_data.iterrows():
                summary_header = f"{row['product']} | {row['client_name']} | {row['sh_ah_name']} | {row['bd_name']}"

                with st.expander(summary_header):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**State:** {row['state']}")
                        st.markdown(f"**SH/AH Name:** {row['sh_ah_name']}")
                        st.markdown(f"**BD Name:** {row['bd_name']}")
                        st.markdown(f"**Month:** {row['month']}")
                        st.markdown(f"**Date:** {row['date'].date()}")
                        st.markdown(f"**Client Name:** {row['client_name']}")
                        st.markdown(f"**Name of Person Met:** {row['name_of_person_met']}")
                        st.markdown(f"**Designation of Person Met:** {row['designation_of_person_met']}")
                        st.markdown(f"**Profile:** {row['profile']}")
                        st.markdown(f"**If Processor, Type:** {row['if_processor_type']}")
                        st.markdown(f"**Customer Location:** {row['customer_location']}")
                        st.markdown(f"**Existing/New:** {row['existing_new']}")
                        st.markdown(f"**Phone:** {row['phone']}")
                    with col2:
                        st.markdown(f"**Commodity:** {row['commodity']}")
                        st.markdown(f"**Product:** {row['product']}")
                        st.markdown(f"**Type of Meeting:** {row['type_of_meeting']}")
                        st.markdown(f"**Meeting Brief:** {row['meeting_brief']}")
                        st.markdown(f"**Status of Case:** {row['status_of_case']}")
                        st.markdown(f"**Follow Up Date:** {row['follow_up_date']}")
                        if pd.notna(row['image_url']):
                            st.image(row['image_url'], use_column_width=True)
                    if role == 'admin':
                        ah_review_remark = st.text_area('AH Review/Remark', value=row['ah_review_remark'], key=f'remark_{index}')
                        if pd.notna(row['ah_review_date']):
                            ah_review_date = st.date_input('AH Review Date', value=row['ah_review_date'].date(), key=f'date_{index}')
                        else:
                            ah_review_date = st.date_input('AH Review Date', value=dt.date.today(), key=f'date_{index}')                        
                        if st.button('Update Record', key=f'update_{index}'):
                            engine = create_db_engine()
                            data.loc[index, 'ah_review_remark'] = ah_review_remark
                            data.loc[index, 'ah_review_date'] = pd.to_datetime(ah_review_date)
                            data.to_sql('dsr_activity', engine, if_exists='replace', index=False)
                            st.success('Record updated successfully!')

            if role == 'admin':
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv_data,
                    file_name='filtered_data.csv',
                    mime='text/csv'
                )

    if st.sidebar.button('Logout'):
       handle_logout()

else:
    st.title('Login')
    st.write("Please log in to continue.")   
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state.username = st.text_input('Username', value=st.session_state.username)
        st.session_state.password = st.text_input('Password', type='password', value=st.session_state.password)
        
        if st.button('Login'):
            handle_login()

