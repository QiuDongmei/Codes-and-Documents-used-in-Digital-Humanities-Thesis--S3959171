#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import datetime as dt
from bokeh.plotting import figure, show, output_file
from bokeh.models import CategoricalColorMapper, ColumnDataSource, Slider, Select, CDSView, GroupFilter, RangeSlider, CheckboxGroup
import seaborn as sns
from bokeh.layouts import column, row
from bokeh.io import curdoc




def get_dataset(path):
  data = pd.read_csv(path, sep=',', index_col = False, parse_dates=['dt'])
  data.rename(columns={'dt':'date'}, inplace=True) 
  data['month'] = data.date.dt.month
  data['day'] = data.date.dt.day
  return data




def map_colors(data, sns_palette, n_colors):
	pal = sns.color_palette(sns_palette, n_colors) 
	colors = pal.as_hex() 
	colormap = CategoricalColorMapper(palette=colors, factors=data['media'].unique())
	return colormap, colors




data = get_dataset('all.csv')
colormap, colors = map_colors(data, "hls", len(list(data.media.unique())))
source = ColumnDataSource(data={ 
    'month' : data.month,
    'day' : data.day,
    'count' : data['count'],
    'media' : data.media,
    'date':data.date
})


p = figure(title = "Post Timelines of State Media and Business Media during the Outbreak of COVID-19 in China Based on three Case Studies",x_axis_type="datetime",
	plot_width=900, plot_height=400,
	tools="hover, save, pan, box_zoom, reset, wheel_zoom", # here we add the interactive tools that we want our plot to have (these are the simple ones)
	tooltips = [('media', '@media'), ('count', '@count')]) # here we can assign which values to show on the hover tool




p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Count'



p.circle(x = 'date', y = 'count', source = source, # here we assign the data
         color={'field': 'media', 'transform': colormap}, # assign the colors: this is a dictionary with the keys field and transform, transform has to be a mapper object
         fill_alpha=0.2, size=10) # transparency and size of the circles


slider_month = Slider(start = 1, end =5, 
                     step = 1, value = 1, title = 'Months to plot')

checkbox_selection = CheckboxGroup(labels=list(data.media.unique()), 
                                  active = [0, 1])





def update(attrname, old, new):
    k = slider_month.value
    checkbox_to_plot = [checkbox_selection.labels[i] for i in checkbox_selection.active]
    source.data = {
    	'date' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].date,
    	'month' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].month,
    	'count' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))]['count'],
    	'media' : data[(data.month == k) & (data.media.isin(checkbox_to_plot))].media
	}

slider_month.on_change('value', update)
checkbox_selection.on_change('active', update)




show(p)



layout = column (p, row(checkbox_selection, slider_month))  # we create the layout in a column and row shape

output_file = ('circle.html') 

curdoc().add_root(layout) 

