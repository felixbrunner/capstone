### IMPORTS ###
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import contextily as ctx

from sklearn.metrics import confusion_matrix

### EDA ###

def make_countplot(df):
    '''Plots the evolution of search counts and success rate over time.'''
    # prepare data
    df_counts = df[['date','type']]\
                    .reset_index()\
                    .groupby(['date','type']).count()\
                    .unstack()\
                    .resample('W').count()
    df_rate = df.set_index('date')\
                    [['success']]\
                    .resample('W').mean()
#     df_success = df.set_index(['date','type'])['success']\
#                 .groupby(['date','type']).agg(['sum', 'count'])\
#                 .fillna(0)\
#                 .unstack()\
#                 .resample('W').sum()\
#                 .stack()
#     df_success = (df_success['sum']/df_success['count']).unstack()
    
    # plot
    fig, ax = plt.subplots(1, 1, figsize=(17, 8))
    ax.set_title('Evolution of search counts and success rate over time')
    
    # search counts
    ax.plot(df_counts.iloc[1:-1,0], label='Person & Vehicle')
    ax.plot(df_counts.iloc[1:-1,1], label='only Person')
    ax.plot(df_counts.iloc[1:-1,2], label='only Vehicle')
    ax.set_ylim([-50, 6000])
    ax.legend(loc='upper left', title='Left axis: Total searches')
    ax.set_ylabel('Weekly number of searches')
    
    # success rates
    ax2=ax.twinx()
    ax2.plot(df_rate, label='Sucess rate', c='k', linestyle='--', linewidth=2)
#     ax2.plot(df_success.iloc[1:-1,0], label='Person & Vehicle', linestyle='--', linewidth=2)
#     ax2.plot(df_success.iloc[1:-1,1], label='only Person', linestyle='--', linewidth=2)
#     ax2.plot(df_success.iloc[1:-1,2], label='only Vehicle', linestyle='--', linewidth=2)
    ax2.grid(False)
    ax2.set_ylim([-0.0025, 0.3])
    ax2.legend(loc='upper right', title='Right axis: Search success rates')
    ax2.set_ylabel('Fraction of successful searches')
    
    fig.savefig('../reports/figures/timeseriesplot.jpg', dpi=300, bbox_inches='tight')
    
def make_geoplot(df):
    '''Plots the geographical locations of searches.'''
    # prepare data
    df_geo = gpd.GeoDataFrame(df.set_index('station')[['long','lat', 'success', 'stripped']],
                          geometry=gpd.points_from_xy(x=df.long, y=df.lat))
    df_geo = df_geo.set_crs(epsg=4326)
    #data_hit = df_geo[df_geo.success]
    #data_nohit = df_geo[~df_geo.success]
    
    # make plot
    fig, ax = plt.subplots(1, 1, figsize=(17, 12))
    ax.set_title('Geography of searches')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    #ax.set_xlim([-7, 2])
    #ax.set_ylim([49, 57])
    
    # plot observations
    ax.scatter(x=df_geo.long[~df_geo.success], y=df_geo.lat[~df_geo.success], label='Unsuccessful searches', s=5, marker='o', alpha=0.5)
    ax.scatter(x=df_geo.long[df_geo.success], y=df_geo.lat[df_geo.success], label='Successful searches', s=1, marker='o', alpha=0.8)
#     ax.scatter(x=df_geo.long[~df_geo.success], y=df_geo.lat[~df_geo.success], color='b', label='Unsuccessful searches', s=5, marker='o', alpha=0.5)
#     ax.scatter(x=df_geo.long[df_geo.success], y=df_geo.lat[df_geo.success], color='r', label='Successful searches', s=1, marker='o', alpha=0.8)
        
    # add map
    ctx.add_basemap(ax, crs=df_geo.crs.to_string(), alpha=1) #, source=ctx.providers.Stamen.TonerLite)
    
    # finalise
    ax.legend(loc='upper right')
    fig.savefig('../reports/figures/geoplot.jpg', dpi=300, bbox_inches='tight')
    
def make_confusion_heatmap(df):
    '''Creates a confusion matrix with self-defined ethnicity vs officer-ascribed ethnicity.'''
    # prepare data
    ethnicity_map = {'White - English/Welsh/Scottish/Northern Irish/British': 'White',
                 'Black/African/Caribbean/Black British - Any other Black/African/Caribbean background': 'Black',
                 'Asian/Asian British - Pakistani': 'Asian',
                 'Mixed/Multiple ethnic groups - White and Black Caribbean': 'Mixed',
                 'Asian/Asian British - Any other Asian background': 'Asian',
                 'White - Any other White background': 'White',
                 'Black/African/Caribbean/Black British - African': 'Black',
                 'Black/African/Caribbean/Black British - Caribbean': 'Black',
                 'Other ethnic group - Not stated': np.nan,
                 'Asian/Asian British - Indian': 'Asian',
                 'White - Irish': 'White',
                 'Mixed/Multiple ethnic groups - Any other Mixed/Multiple ethnic background': 'Mixed',
                 'Asian/Asian British - Bangladeshi': 'Asian',
                 'Other ethnic group - Any other ethnic group': 'Other',
                 'nan': np.nan,
                 'Mixed/Multiple ethnic groups - White and Asian': 'Mixed',
                 'Asian/Asian British - Chinese': 'Asian',
                 'White - Gypsy or Irish Traveller': 'White',
                 'Mixed/Multiple ethnic groups - White and Black African': 'Mixed',
                 'Other ethnic group - Arab': 'Other'}
    df_ethnicity = df[['ethnicity_self', 'ethnicity_officer']].rename(columns={'ethnicity_self': 'self', 'ethnicity_officer': 'officer'})
    df_ethnicity['self_'] = df.ethnicity_self.map(ethnicity_map)
    df_ethnicity['match'] = df_ethnicity.officer == df_ethnicity.self_
    
    # make confusion matrix
    labels = ['Asian', 'Black', 'White', 'Mixed', 'Other']
    confusion = pd.DataFrame(data=confusion_matrix(df_ethnicity.self_.astype(str), \
                                                   df_ethnicity.officer, labels=labels, normalize='true'),
                                               index=labels, columns=labels)
    
    # make plot
    fig, ax = plt.subplots(1, 1, figsize=[6, 4.5])
    ax.set_title('Ethnicity confusion matrix (%)')
    sns.heatmap(confusion.round(4), annot=True, cmap='PuBu', ax=ax, linewidths=1)
    ax.set_xlabel('Officer-ascribed ethnicity')
    ax.set_ylabel('Self-defined ethnicity')
    plt.yticks(rotation=0)
    
    fig.savefig('../reports/figures/heatmap.jpg', dpi=300, bbox_inches='tight')
    
def make_barplot(df, group_var, outcome_var):
    ''''''
    # prepare data
    data = df.groupby(group_var)[outcome_var].agg(['mean', 'std', 'count'])
    data['se'] = data['std']/np.sqrt(data['count'])*1.96
    
    # plot parameters
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    fig.suptitle('Hit rate differences with regards to "{}"'.format(group_var))
    ax.set_xlabel('Hit rate')
    ax.set_xlim([0, 1])
    ax.invert_yaxis()  # labels read top-to-bottom
    
    # overall mean
    ax.axvline(df[outcome_var].mean(), color='k', linestyle='--', linewidth=2, label='Overall rate')
    ax.legend(loc='upper right')
    
    # barplot
    ax.barh(np.arange(len(data)), width=data['mean'], height=0.7, xerr=data.se, align='center', error_kw={'capthick': 2, 'capsize': 5})
    ax.set_yticks(np.arange(len(data)))
    ax.set_yticklabels(data.index)
    ax.set_ylabel(group_var)
    
def make_barplot_success(df, group_vars):
    ''''''
    # plot parameters
    fig, axes = plt.subplots(len(group_vars), 2, figsize=(15, 6), gridspec_kw={'height_ratios': [df[group_var].nunique() for group_var in group_vars]})
    
    for ax, group_var in zip(axes[:, 0], group_vars):
        # prepare data
        data = df.groupby(group_var)['success'].agg(['mean', 'std', 'count'])
        data['se'] = data['std']/np.sqrt(data['count'])
        
        # ax parameters
        ax.set_title('Success rate by "{}"'.format(group_var))
        #ax.set_xlabel('Hit rate')
        ax.set_xlim([0, 0.4])
        ax.invert_yaxis()  # labels read top-to-bottom
    
        # overall mean
        ax.axvline(df['success'].mean(), color='k', linestyle='--', linewidth=2, label='Overall success rate')
        if group_var == group_vars[0]:
            ax.legend(loc='upper right')
    
        # barplot
        ax.barh(np.arange(len(data)), width=data['mean'], height=0.7, xerr=data.se*1.96, align='center', error_kw={'capthick': 2, 'capsize': 4})
        ax.set_yticks(np.arange(len(data)))
        ax.set_yticklabels(data.index)
        if group_var != group_vars[-1]:
            ax.set_xticklabels([])
        #ax.set_ylabel(group_var)
        
    for ax, group_var in zip(axes[:, 1], group_vars):
        # prepare data
        data = df.groupby(group_var)['stripped'].agg(['mean', 'std', 'count'])
        data['se'] = data['std']/np.sqrt(data['count'])
        
        # ax parameters
        ax.set_title('Clothes removal rate by "{}"'.format(group_var))
        #ax.set_xlabel('Hit rate')
        ax.set_xlim([0, 0.15])
        ax.invert_yaxis()  # labels read top-to-bottom
    
        # overall mean
        ax.axvline(df['stripped'].mean(), color='k', linestyle='--', linewidth=2, label='Overall removal rate')
        if group_var == group_vars[0]:
            ax.legend(loc='upper right')
    
        # barplot
        ax.barh([], [])
        ax.barh(np.arange(len(data)), width=data['mean'], height=0.7, xerr=data.se*1.96, align='center', error_kw={'capthick': 2, 'capsize': 4})
        ax.set_yticks(np.arange(len(data)))
        ax.set_yticklabels([])
        if group_var != group_vars[-1]:
            ax.set_xticklabels([])
        
        fig.savefig('../reports/figures/success_rates.jpg', dpi=300, bbox_inches='tight')
        
def make_evaluation_plot(df=None):
    '''Creates a summarising plot of model perfomances.'''
    # set up
    if df is not None:
        df_plain_models = df
    else:
        df_plain_models = pd.read_pickle('../data/df_plain_models.pickle')
    labels = df_plain_models.index.to_list()
    x = np.arange(len(labels)-1)
    fig, axes = plt.subplots(4, 1, figsize=(17,10))
    
    # precision
    ax = axes[0]
    ax.set_xticklabels([])
    ax.set_title('Search precision')
    ax.bar(x=x-0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('train', 'precision')], label='Training', width=0.2)
    ax.bar(x=x+0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('val', 'precision')], label='Validation', width=0.2)
    ax.axhline(df_plain_models.loc['Benchmark', ('all', 'precision')], c='k', linewidth=2, linestyle='--', label='Benchmark')
    ax.axhline(0, c='k', linewidth=4, linestyle='-')
    ax.set_ylim([0, 1])
    
    # within station
    ax = axes[1]
    ax.set_xticklabels([])
    ax.set_title('Maximum discrimination within station between ethnicity-gender-subgroups')
    ax.bar(x=x-0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('train', 'within_station')], label='Training', width=0.2)
    ax.bar(x=x+0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('val', 'within_station')], label='Validation', width=0.2)
    ax.axhline(df_plain_models.loc['Benchmark', ('all', 'within_station')], c='k', linewidth=2, linestyle='--', label='Benchmark')
    ax.axhline(0.05, c='k', linewidth=2, linestyle=':', label='Target')
    ax.axhline(0, c='k', linewidth=4, linestyle='-')
    ax.set_ylim([0, None])
    
    # across station
    ax = axes[2]
    ax.set_xticklabels([])
    ax.set_title('Maximum precision discrepancy between stations overall')
    ax.bar(x=x-0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('train', 'across_station')], label='Training', width=0.2)
    ax.bar(x=x+0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('val', 'across_station')], label='Validation', width=0.2)
    ax.axhline(df_plain_models.loc['Benchmark', ('all', 'across_station')], c='k', linewidth=2, linestyle='--', label='Benchmark')
    ax.axhline(0.1, c='k', linewidth=2, linestyle=':', label='Target')
    ax.axhline(0, c='k', linewidth=4, linestyle='-')
    ax.set_ylim([0, None])
    
    # across subgroups
    ax = axes[3]
    ax.set_title('Maximum discrimination between ethnicity-gender-subgroups')
    ax.bar(x=x-0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('train', 'across_group')], label='Training', width=0.2)
    ax.bar(x=x+0.1, height=df_plain_models.loc[df_plain_models.index!='Benchmark', ('val', 'across_group')], label='Validation', width=0.2)
    ax.axhline(df_plain_models.loc['Benchmark', ('all', 'across_group')], c='k', linewidth=2, linestyle='--', label='Benchmark')
    ax.axhline(0.05, c='k', linewidth=2, linestyle=':', label='Target')
    ax.axhline(0, c='k', linewidth=4, linestyle='-')
    ax.set_xticklabels(labels)
    ax.set_ylim([0, None])
    ax.legend(loc='upper right', bbox_to_anchor=(0.7, -0.1), ncol=4)
    
    fig.savefig('../reports/figures/evaluation.jpg', dpi=300, bbox_inches='tight')
    
def make_station_barplot(df):
    '''Creates a stacked barplot to show station observation counts.'''
    fig, ax = plt.subplots(1, 1, figsize=(15,4))
    
    df[df.index != 'metropolitan'].plot.bar(stacked=True, ax=ax)
    ax.set_title('Observation count per station and dataset')
    
    fig.savefig('../reports/figures/station_obs.jpg', dpi=300, bbox_inches='tight')
    
def make_distribution_plots(X_0, X_1, X_2, X_3):
    '''Creates grouped barplots to compare discrete dataset distributions.'''
    fig, axes = plt.subplots(7, 1, figsize=(5, 30))

    columns = ['type', 'operation', 'sex', 'age', 'ethnicity_officer', 'legislation', 'search_target']
    titles = ['Type', 'Part of policing operation', 'Gender', 'Age group', 'Officer-defined ethnicity', 'Legislation', 'Object of search']

    for col, title, ax in zip(columns, titles, axes):
        counts = (X_0[col].value_counts()/len(X_0))\
                    .rename('Training data')\
                    .to_frame()\
                    .join((X_1[col].value_counts()/len(X_1)).rename('Test set 1'))\
                    .join((X_2[col].value_counts()/len(X_2)).rename('Test set 2'))\
                    .join((X_3[col].value_counts()/len(X_3)).rename('Training data (same stations)'))
        counts.index = counts.index.add_categories(['NA'])
        counts.loc['NA',:] = [X[col].isna().sum()/len(X) for X in [X_0, X_1, X_2, X_3]]
    
        counts.plot.bar(ax=ax, legend=False)
        ax.set_xlabel(title)
        if col == 'type':
            ax.set_xticklabels(['Person', 'Person & Vehicle', 'Vehicle', 'NA'], rotation=0)
        elif col in ['legislation', 'search_target']:
            ax.set_xticklabels([label[0:3]+'.' for label in counts.index], rotation=90)
        else:
            ax.set_xticklabels(counts.index, rotation=0)
        
        if col == 'search_target':
            ax.legend(bbox_to_anchor=(0.5, -0.6), ncol=3, loc='lower center')
        
        plt.subplots_adjust(hspace = 0.4)
    
    fig.savefig('../reports/figures/distribution_comparison.jpg', dpi=300, bbox_inches='tight')