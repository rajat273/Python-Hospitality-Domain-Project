#!/usr/bin/env python
# coding: utf-8

# # Hospitality Domain Data Analysis
# 

# In[1]:


import pandas as pd
from datetime import date
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


d_date=pd.read_csv(r"C:\Users\RaJat sharma\Downloads\64101194a2364\source-code\3_project_hospitality_analysis\datasets\dim_date.csv")
d_hotel=pd.read_csv(r"C:\Users\RaJat sharma\Downloads\64101194a2364\source-code\3_project_hospitality_analysis\datasets\dim_hotels.csv")
d_room=pd.read_csv(r"C:\Users\RaJat sharma\Downloads\64101194a2364\source-code\3_project_hospitality_analysis\datasets\dim_rooms.csv")
fact_aggregate_booking=pd.read_csv(r"C:\Users\RaJat sharma\Downloads\64101194a2364\source-code\3_project_hospitality_analysis\datasets\fact_aggregated_bookings.csv")
fact_booking=pd.read_csv(r"C:\Users\RaJat sharma\Downloads\64101194a2364\source-code\3_project_hospitality_analysis\datasets\fact_bookings.csv")



# Data Exploration

# In[3]:


fact_booking.head(3)


# In[4]:


fact_aggregate_booking.head(3)


# In[5]:


d_date.head(3)


# In[6]:


d_hotel.head(3)


# In[7]:


d_room.head(3)


# Data Cleaning

# In[8]:


fact_booking.describe(),fact_aggregate_booking.describe()


# In[9]:


#removing negative number of Guest(data cleaning)


# In[10]:


fact_booking=fact_booking[fact_booking.no_guests>0]


# In[11]:


#removing outlier from revenue generated


# In[12]:


avg=fact_booking.revenue_generated.mean()
std=fact_booking.revenue_generated.std()


# In[13]:


fact_booking[fact_booking.revenue_generated>avg+3*std]


# In[14]:


fact_booking=fact_booking[fact_booking.revenue_generated<avg+3*std]


# In[15]:


fact_booking.isna().sum(),fact_aggregate_booking.isna().sum(),d_hotel.isna().sum(),d_room.isna().sum()


# In[16]:


# replacing na in capacity with mean


# In[17]:


fact_aggregate_booking.capacity.fillna(fact_aggregate_booking.capacity.mean(), inplace=True)


# In[18]:


#changing date to datetime type


# In[19]:


fact_booking['check_in_date'] = pd.to_datetime(fact_booking['check_in_date'],format='mixed')
d_date['date']=pd.to_datetime(d_date['date'],format='mixed')
fact_aggregate_booking['check_in_date'] = pd.to_datetime(fact_aggregate_booking['check_in_date'],format='mixed')


# In[20]:


# merging table


# In[21]:


df=pd.merge(fact_booking,fact_aggregate_booking,on=['check_in_date','property_id','room_category'])
df=pd.merge(df,d_date,left_on='check_in_date',right_on='date')
df.drop(['date'], axis=1,inplace=True)# drop date col
df.drop(['day_type'], axis=1,inplace=True)# drop old date type
def f(x):
    if x.weekday()==4 or x.weekday()==5:
        val = "weekend"
    else:
        val="weekday"
    return val

df['day_type']=df['check_in_date'].apply(f)


# In[22]:


def g(x):
    list=x.split()
    return list[1]
    
df['n_week_no']=df['week no'].apply(g)



# In[23]:


df=pd.merge(df,d_hotel,on='property_id')
df=pd.merge(df,d_room,left_on='room_category',right_on='room_id')
df.drop(['room_id'], axis=1,inplace=True)
df['c_capacity']=df.groupby(['property_id','check_in_date','room_category'])['capacity'].transform('count')
df['c_suc_book']=df.groupby(['property_id','check_in_date','room_category'])['successful_bookings'].transform('count')


# In[24]:


def ADR(df):
    r=df.revenue_realized.sum()
    c=df.booking_id.count()
    return round(r/c,1)

def Realisation_PER(df):
    s=df[df.booking_status=='Checked Out'].booking_id.count()
    c=df.booking_id.count()
    return round((s/c)*100,1)
def AVG_rating(df):
     return round(df.ratings_given.mean(),1)

def can_PER(df):
    s=df[df.booking_status=='Cancelled'].booking_id.count()
    c=df.booking_id.count()
    return round((s/c)*100,1)
        
def REVPAR(df):
    r=df.revenue_realized.sum()
    cap=(df.capacity/df.c_capacity).sum()
    return round(r/cap,1)

def Revenue(df):
    return df.revenue_realized.sum()

def OOC_PER(df):
    r=(df.successful_bookings/df.capacity).mean()
    return round(r*100,1)

def DBRN(df):
    c_suc_book=(df.successful_bookings/df.c_suc_book).sum()
    d=len(df['check_in_date'].unique())
    return round(c_suc_book/d,1)

def DSRN(df):
    cap=(df.capacity/df.c_capacity).sum()
    d=len(df['check_in_date'].unique())
    return round(cap/d,1)

def DURN(df):
    s=df[df.booking_status=='Checked Out'].booking_id.count()
    d=len(df['check_in_date'].unique())
    return round(s/d,1)


# In[25]:


Revenue(df),ADR(df),REVPAR(df),Realisation_PER(df)


# In[26]:


AVG_rating(df)


# In[27]:


grp_platform=fact_booking.groupby('booking_platform')
booking_platform=grp_platform.apply(ADR).reset_index()
booking_platform.rename(columns={0:"ADR"},inplace=True)
booking_platform_r=grp_platform.apply(Realisation_PER).reset_index()
booking_platform_r.rename(columns={0:"Realisation%"},inplace=True)
booking_platform=pd.merge(booking_platform,booking_platform_r)
plt.figure(figsize=(8,3)) 
plt.xlabel('booking_platform')
plt.xticks(rotation=45, ha='right')
plt.bar(booking_platform['booking_platform'], booking_platform["Realisation%"], color='green', label='Realisation%')
plt.ylabel('Realisation%')
plt.ylim(60, 80)
plt.title('ADR and Realisation% by booking_platform')
plt.legend(loc='upper right')
ax2 = plt.twinx()
ax2.plot(booking_platform['booking_platform'], booking_platform["ADR"], color='red', marker='o', label='ADR')
ax2.set_ylabel('ADR')
ax2.legend(loc='upper left')
plt.show()


# In[28]:


revenue_by_cat=df.groupby('category')
a=revenue_by_cat.apply(Revenue).reset_index()
plt.figure(figsize=(8,3))
plt.title('Revenue by Category')
plt.pie(a[0],labels=a['category'],autopct='%1.1f%%')
plt.show()


# In[29]:


g_week=df.groupby('week no')

g_week.apply(OOC_PER).plot(marker='o')
plt.xlabel('Week')
plt.ylabel('Occupancy %')
plt.title('Occupancy % by Week')
plt.show()


# In[30]:


g=g_week.apply(REVPAR).reset_index()
g1=g_week.apply(ADR).reset_index()
gf=pd.merge(g,g1,on='week no')
plt.figure(figsize=(8,3))
plt.plot(gf['week no'],gf["0_x"], color='red',marker='o', label='REVPAR')
plt.ylabel('REVPAR')
plt.ylim(5000,10000)
plt.legend(loc='upper left')
ax2 = plt.twinx()
ax2.plot(gf['week no'],gf["0_y"], color='green',marker='o', label='ADR')
ax2.set_ylabel('ADR')
ax2.set_ylim(12000,13000)
plt.title('REVPAR and ADR by Week')
ax2.legend(loc='upper right')
plt.show()


# In[31]:


grp_day_type=df.groupby('day_type')
a=grp_day_type.apply(ADR).reset_index()
a.rename(columns={0:"ADR"},inplace=True)
a1=grp_day_type.apply(REVPAR).reset_index()
a1.rename(columns={0:"REVPAR"},inplace=True)
a2=grp_day_type.apply(Realisation_PER).reset_index()
a2.rename(columns={0:"Realisation%"},inplace=True)
a3=grp_day_type.apply(OOC_PER).reset_index()
a3.rename(columns={0:"OOC_PER"},inplace=True)
a=pd.merge(a,a1,on='day_type')
a=pd.merge(a,a2,on='day_type')
a=pd.merge(a,a3,on='day_type')
a


# In[32]:


grp_property=df.groupby(['property_id','property_name'])
a=grp_property.apply(Revenue).reset_index()
a.rename(columns={0:"Revenue"},inplace=True)
a1=grp_property.apply(ADR).reset_index()
a1.rename(columns={0:"ADR"},inplace=True)
a2=grp_property.apply(REVPAR).reset_index()
a2.rename(columns={0:"REVPAR"},inplace=True)
a3=grp_property.apply(DBRN).reset_index()
a3.rename(columns={0:"DBRN"},inplace=True)
a4=grp_property.apply(DSRN).reset_index()
a4.rename(columns={0:"DSRN"},inplace=True)
a5=grp_property.apply(DURN).reset_index()
a5.rename(columns={0:"DURN"},inplace=True)
a6=grp_property.apply(AVG_rating).reset_index()
a6.rename(columns={0:"AVG_rating"},inplace=True)
a7=grp_property.apply(Realisation_PER).reset_index()
a7.rename(columns={0:"Realisation%"},inplace=True)
a8=grp_property.apply(can_PER).reset_index()
a8.rename(columns={0:"Cancellation%"},inplace=True)
a=pd.merge(a,a1,on=['property_id','property_name'])
a=pd.merge(a,a2,on=['property_id','property_name'])
a=pd.merge(a,a3,on=['property_id','property_name'])
a=pd.merge(a,a4,on=['property_id','property_name'])
a=pd.merge(a,a5,on=['property_id','property_name'])
a=pd.merge(a,a6,on=['property_id','property_name'])
a=pd.merge(a,a7,on=['property_id','property_name'])
a=pd.merge(a,a8,on=['property_id','property_name'])
a


# In[33]:


revenue_by_cat=df.groupby('room_class')
a=revenue_by_cat.apply(Revenue).reset_index()
plt.figure(figsize=(8,3))
plt.title('Revenue by Room Class')
plt.pie(a[0],labels=a['room_class'],autopct='%1.1f%%')
plt.show()


# In[34]:


revenue_by_city=df.groupby('city')
a=revenue_by_city.apply(Revenue).reset_index()
plt.figure(figsize=(8,3))
plt.title('Revenue by city')
plt.bar(a['city'],a[0])
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:




