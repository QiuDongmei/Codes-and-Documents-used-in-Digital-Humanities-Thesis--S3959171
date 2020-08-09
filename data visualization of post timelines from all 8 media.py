#!/usr/bin/env python
# coding: utf-8

# In[102]:


import pandas as pd
import datetime as dt
from bokeh.plotting import figure, show, output_file
from bokeh.models import CategoricalColorMapper, ColumnDataSource, Slider, Select, CDSView, GroupFilter, RangeSlider, CheckboxGroup
import seaborn as sns
from bokeh.layouts import column, row
from bokeh.io import curdoc


# In[103]:


def get_dataset(path):
  data = pd.read_csv(path, sep=',', index_col = False, parse_dates=['dt'])
  data.rename(columns={'dt':'date'}, inplace=True) # we do this because we have a package called dt and it could make things confusing
  # the dt package allows us to extract the month and the year from a full date
  data['month'] = data.date.dt.month
  data['day'] = data.date.dt.day
  #countries = ["China", "Australia", "Netherlands (Europe)", "Austria", 'Colombia', 'Comoros']
  #data = data[data.Country.isin(countries)]
  #data = data[data.month == 1]
  return data


# In[104]:


def map_colors(data, sns_palette, n_colors):
	pal = sns.color_palette(sns_palette, n_colors) # 3 is the number of colors to extract from the palette
	colors = pal.as_hex() # get the values of those colors. We could also have written the name/numbers of some colors
	#print(colors) # you can observe that this is just a string of color values
	colormap = CategoricalColorMapper(palette=colors, factors=data['media'].unique())
	return colormap, colors



# In[106]:


# STEP 1: import the data
data = get_dataset('all.csv')
# STEP 2: map the colors to our data
colormap, colors = map_colors(data, "hls", len(list(data.media.unique())))
# STEP 3: create the data source for the interactive graph
source = ColumnDataSource(data={ 
    'month' : data.month,
    'day' : data.day,
    'count' : data['count'],
    'media' : data.media,
    'date':data.date
})


# In[107]:


p = figure(title = "Post Timelines of State Media and Business Media during the Outbreak of COVID-19 in China Based on three Case Studies",x_axis_type="datetime",
	plot_width=900, plot_height=400,
	tools="hover, save, pan, box_zoom, reset, wheel_zoom", # here we add the interactive tools that we want our plot to have (these are the simple ones)
	tooltips = [('media', '@media'), ('count', '@count')]) # here we can assign which values to show on the hover tool


# In[108]:


p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Count'


# In[109]:


# STEP 5: fill it with circles
p.circle(x = 'date', y = 'count', source = source, # here we assign the data
         color={'field': 'media', 'transform': colormap}, # assign the colors: this is a dictionary with the keys field and transform, transform has to be a mapper object
         fill_alpha=0.2, size=10) # transparency and size of the circles


# In[110]:


# STEP 6: add elements to the interactive graph 
# SLIDER ELEMENT
slider_month = Slider(start = 1, end =5, 
                     step = 1, value = 1, title = 'Months to plot')
# CHECKBOX ELEMENT
checkbox_selection = CheckboxGroup(labels=list(data.media.unique()), 
                                  active = [0, 1])


# In[111]:


def update(attrname, old, new):
    # Get the current slider values
    k = slider_month.value
    checkbox_to_plot = [checkbox_selection.labels[i] for i in checkbox_selection.active]
    # Generate the new curve
    source.data = {
    	'date' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].date,
    	'month' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].month,
    	'count' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))]['count'],
    	'media' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].media
	}

slider_month.on_change('value', update)
checkbox_selection.on_change('active', update)


# In[112]:


show(p)


# In[113]:



# STEP 7: design our layout
layout = column (p, row(checkbox_selection, slider_month))  # we create the layout in a column and row shape

output_file = ('scatter.html') # we output the html file

# STEP 8: run the server behind the visualisation!
curdoc().add_root(layout) 

