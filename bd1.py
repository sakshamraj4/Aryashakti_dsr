import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px

# Load data
data_path = '/home/az-134/Downloads/bd.csv'
data = pd.read_csv(data_path)

# Convert DATE and FOLLOW UP DATE to datetime
data['DATE'] = pd.to_datetime(data['DATE'], format='%d %b %Y', errors='coerce')
data['FOLLOW UP DATE'] = pd.to_datetime(data['FOLLOW UP DATE'], format='%d %b %Y', errors='coerce')

# Convert AH REVIEW DATE to datetime
data['AH review date'] = pd.to_datetime(data['AH review date'], errors='coerce')

# User credentials and roles
users = {
    'bdview': {'password': 'bd@arya', 'role': 'view'},
    'adminview': {'password': 'admin@arya', 'role': 'admin'}
}

# Function to check credentials
def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return users[username]['role']
    return None

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    role = st.session_state.role
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    st.title('DSR Activity Dashboard')

    # Option to switch between detailed data view and summary view
    view_type = st.sidebar.radio("Select View", ["Summary View", "Detailed Data View"])

    if view_type == "Summary View":
        st.header("Summary View")

        # Calculate summary metrics
        today = pd.Timestamp.today()
        yesterday = today - pd.Timedelta(days=1)
        last_week = today - pd.Timedelta(days=7)
        first_day_of_month = today.replace(day=1)
        last_month = first_day_of_month - pd.Timedelta(days=1)
        first_day_of_last_month = last_month.replace(day=1)

        today_data = data[data['DATE'] == today]
        yesterday_data = data[data['DATE'] == yesterday]
        last_week_data = data[(data['DATE'] >= last_week) & (data['DATE'] <= today)]
        this_month_data = data[(data['DATE'] >= first_day_of_month) & (data['DATE'] <= today)]
        last_month_data = data[(data['DATE'] >= first_day_of_last_month) & (data['DATE'] <= last_month)]

        # Display summary metrics
        st.subheader("DSR Activity Summary")
        st.write(f"**DSR Activity Done Today:** {len(today_data)}")
        st.write(f"**DSR Activity Done Yesterday:** {len(yesterday_data)}")
        st.write(f"**DSR Activity Done Last Week:** {len(last_week_data)}")
        st.write(f"**DSR Activity Done This Month:** {len(this_month_data)}")
        st.write(f"**DSR Activity Done Last Month:** {len(last_month_data)}")

        # Pie chart: Status of Case
        st.subheader("Status of Case Distribution")
        status_counts = data['STATUS OF CASE'].value_counts().reset_index()
        status_counts.columns = ['STATUS OF CASE', 'count']
        status_pie_chart = px.pie(status_counts, names='STATUS OF CASE', values='count', title='Status of Case', hole=0)
        st.plotly_chart(status_pie_chart)

        # Pie chart: Type of Meeting
        st.subheader("Type of Meeting Distribution")
        meeting_type_counts = data['TYPE OF MEETING'].value_counts().reset_index()
        meeting_type_counts.columns = ['TYPE OF MEETING', 'count']
        meeting_type_pie_chart = px.pie(meeting_type_counts, names='TYPE OF MEETING', values='count', title='Type of Meeting', hole=0)
        st.plotly_chart(meeting_type_pie_chart)

        # Pie chart: Product Distribution
        st.subheader("Product Distribution")
        product_counts = data['PRODUCT'].value_counts().reset_index()
        product_counts.columns = ['PRODUCT', 'count']
        product_pie_chart = px.pie(product_counts, names='PRODUCT', values='count', title='Product', hole=0)
        st.plotly_chart(product_pie_chart)

        # Bar chart: Commodity Distribution
        st.subheader("Commodity Distribution")
        commodity_counts = data['COMMODITY'].value_counts().reset_index()
        commodity_counts.columns = ['COMMODITY', 'count']
        commodity_bar_chart = px.bar(commodity_counts, x='COMMODITY', y='count', title='Commodity Distribution')
        commodity_bar_chart.update_xaxes(title_text='Commodity')
        commodity_bar_chart.update_yaxes(title_text='Count')
        st.plotly_chart(commodity_bar_chart)

    else:
        st.header("Detailed Data View")

        # Sidebar filters
        st.sidebar.subheader('Filters')

        state_filter = st.sidebar.multiselect(
            'Select State', 
            options=['All'] + list(data['STATE'].unique()), 
            default=['All']
        )
        bd_name_filter = st.sidebar.multiselect(
            'Select BD Name', 
            options=['All'] + list(data['BD NAME'].unique()), 
            default=['All']
        )
        month_filter = st.sidebar.multiselect(
            'Select Month', 
            options=['All'] + list(data['MONTH'].unique()), 
            default=['All']
        )
        client_filter = st.sidebar.multiselect(
            'Select Client Name', 
            options=['All'] + list(data['CLIENT NAME'].unique()), 
            default=['All']
        )
        designation_filter = st.sidebar.multiselect(
            'Select Designation of Person Met', 
            options=['All'] + list(data['Designation of Person Met'].unique()), 
            default=['All']
        )
        processor_type_filter = st.sidebar.multiselect(
            'Select If Processor, Type', 
            options=['All'] + list(data['IF PROCESSOR, TYPE'].unique()), 
            default=['All']
        )
        commodity_filter = st.sidebar.multiselect(
            'Select Commodity', 
            options=['All'] + list(data['COMMODITY'].unique()), 
            default=['All']
        )
        product_filter = st.sidebar.multiselect(
            'Select Product', 
            options=['All'] + list(data['PRODUCT'].unique()), 
            default=['All']
        )
        status_of_case_filter = st.sidebar.multiselect(
            'Select Status of Case', 
            options=['All'] + list(data['STATUS OF CASE'].unique()), 
            default=['All']
        )

        # Apply filters
        def apply_filters(df):
            filtered_df = df.copy()

            if 'All' not in state_filter:
                filtered_df = filtered_df[filtered_df['STATE'].isin(state_filter)]

            if 'All' not in bd_name_filter:
                filtered_df = filtered_df[filtered_df['BD NAME'].isin(bd_name_filter)]

            if 'All' not in month_filter:
                filtered_df = filtered_df[filtered_df['MONTH'].isin(month_filter)]

            if 'All' not in client_filter:
                filtered_df = filtered_df[filtered_df['CLIENT NAME'].isin(client_filter)]

            if 'All' not in designation_filter:
                filtered_df = filtered_df[filtered_df['Designation of Person Met'].isin(designation_filter)]

            if 'All' not in processor_type_filter:
                filtered_df = filtered_df[filtered_df['IF PROCESSOR, TYPE'].isin(processor_type_filter)]

            if 'All' not in commodity_filter:
                filtered_df = filtered_df[filtered_df['COMMODITY'].isin(commodity_filter)]

            if 'All' not in product_filter:
                filtered_df = filtered_df[filtered_df['PRODUCT'].isin(product_filter)]

            if 'All' not in status_of_case_filter:
                filtered_df = filtered_df[filtered_df['STATUS OF CASE'].isin(status_of_case_filter)]

            return filtered_df

        # Display filtered data
        st.subheader('Filtered Data')
        filtered_data = apply_filters(data)

        if filtered_data.empty:
            st.write("No records found for the selected filters.")
        else:
            for index, row in filtered_data.iterrows():
                # Create a summary header for each card
                summary_header = f"{row['PRODUCT']} | {row['CLIENT NAME']} | {row['SH/ AH NAME']} | {row['BD NAME']}"

                with st.expander(summary_header):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**State:** {row['STATE']}")
                        st.markdown(f"**SH/AH Name:** {row['SH/ AH NAME']}")
                        st.markdown(f"**BD Name:** {row['BD NAME']}")
                        st.markdown(f"**Month:** {row['MONTH']}")
                        st.markdown(f"**Date:** {row['DATE'].date()}")
                        st.markdown(f"**Client Name:** {row['CLIENT NAME']}")
                        st.markdown(f"**Name of Person Met:** {row['Name of Person Met']}")
                        st.markdown(f"**Designation of Person Met:** {row['Designation of Person Met']}")
                        st.markdown(f"**Profile:** {row['PROFILE']}")
                        st.markdown(f"**If Processor, Type:** {row['IF PROCESSOR, TYPE']}")
                        st.markdown(f"**Customer Location:** {row['CUSTOMER LOCATION']}")
                        st.markdown(f"**Existing/New:** {row['EXISTING/ NEW']}")
                        st.markdown(f"**Phone:** {row['PHONE']}")
                    with col2:
                        st.markdown(f"**Commodity:** {row['COMMODITY']}")
                        st.markdown(f"**Product:** {row['PRODUCT']}")
                        st.markdown(f"**Type of Meeting:** {row['TYPE OF MEETING']}")
                        st.markdown(f"**Meeting Brief:** {row['MEETING BRIEF']}")
                        st.markdown(f"**Status of Case:** {row['STATUS OF CASE']}")
                        st.markdown(f"**Follow Up Date:** {row['FOLLOW UP DATE']}")

                        # Display image
                        if pd.notna(row['image_url']):
                            st.image(row['image_url'], use_column_width=True)

                    # For admins: Add fields for updating AH Review/Remark and AH Review Date
                    if role == 'admin':
                        ah_review_remark = st.text_area('AH Review/Remark', value=row['AH review/remark'], key=f'remark_{index}')

                        # Ensure AH review date is a datetime object before using .date()
                        if pd.notna(row['AH review date']):
                            ah_review_date = st.date_input('AH Review Date', value=row['AH review date'].date(), key=f'date_{index}')
                        else:
                            ah_review_date = st.date_input('AH Review Date', value=dt.date.today(), key=f'date_{index}')
                        
                        if st.button('Update Record', key=f'update_{index}'):
                            data.loc[index, 'AH review/remark'] = ah_review_remark
                            data.loc[index, 'AH review date'] = pd.to_datetime(ah_review_date)
                            data.to_csv(data_path, index=False)
                            st.success('Record updated successfully!')

            # Admin-only: Download filtered data as CSV
            if role == 'admin':
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv_data,
                    file_name='filtered_data.csv',
                    mime='text/csv'
                )

    if st.sidebar.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

else:
    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error('Invalid username or password')

