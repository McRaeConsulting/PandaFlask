import re
import os
import gviz_api
import pandas as pd

ons_source_data_file = pd.ExcelFile(f'{os.getenv("DATA_FOLDER")}/publishedweek392020.xlsx')

age_group_table_desc = [('desc', 'string', 'Desc'), ('age0_1', 'number', 'Age <1'),
                        ('age1_4', 'number', 'Age 1-4'), ('age5_9', 'number', 'Age 5-9'),
                        ('age_10_14', 'number', 'Age 10-14'), ('age15_19', 'number', 'Age 15-19'),
                        ('age_20_24', 'number', 'Age 20-24'), ('age25_29', 'number', 'Age 25-29'),
                        ('age_30_34', 'number', 'Age 30-34'), ('age35_39', 'number', 'Age 35-39'),
                        ('age_40_44', 'number', 'Age 40-44'), ('age45_49', 'number', 'Age 45-49'),
                        ('age_50_55', 'number', 'Age 50-55'), ('age55_59', 'number', 'Age 55-59'),
                        ('age_60_64', 'number', 'Age 60-64'), ('age65_69', 'number', 'Age 65-69'),
                        ('age_70_74', 'number', 'Age 70-74'), ('age75_79', 'number', 'Age 75-79'),
                        ('age_80_84', 'number', 'Age 80-84'), ('age85_89', 'number', 'Age 85-89'),
                        ('age_90_plus', 'number', 'Age 90-plus'),
                        ]

age_brackets = ['less1', '1to4', '5to9', '10to14', '15to19', '20to24',
                '25to29', '30to34', '35to39', '40to44', '45to49',
                '50to55', '55to59', '60to64', '65to69', '70to74',
                '75to79', '80to84', '85to89', '90plus']


class InvalidSourceFileException(Exception):
    pass


class WeeklyFiguresModel:
    date_series: pd.Series

    def __init__(self):
        self.weekly_figures_sheet = pd.read_excel(io=ons_source_data_file, sheet_name='Weekly figures 2020')
        self.date_series = pd.Series(data=self.weekly_figures_sheet.iloc[4, 2:])
        self.latest_week = int(re.search(r'\d\d', ons_source_data_file.io).group(0))

    def get_valid_date_series(self):
        return_value = self.date_series.copy().iloc[0:self.latest_week]
        return_value = pd.to_datetime(return_value)
        return return_value.dt.date.to_numpy()

    def total_deaths_averages_json(self):
        ret_frame = pd.DataFrame(data={'date': self.date_series.to_numpy(),
                                       'tot_deaths_all_ages': self.weekly_figures_sheet.iloc[7, 2:].to_numpy(),
                                       'ave_tot_deaths_eng_wales': self.weekly_figures_sheet.iloc[9, 2:].to_numpy(),
                                       'ave_tot_deaths_england': self.weekly_figures_sheet.iloc[11, 2:].to_numpy(),
                                       'ave_tot_deaths_wales': self.weekly_figures_sheet.iloc[13, 2:].to_numpy(),
                                       'deaths_with_resp': self.weekly_figures_sheet.iloc[16, 2:].to_numpy(),
                                       'deaths_with_covid': self.weekly_figures_sheet.iloc[17, 2:].to_numpy(),
                                       })
        ret_frame.dropna(inplace=True)
        table_desc = [('date', 'date', 'Date'),
                      ('tot_deaths_all_ages', 'number', 'Total deaths, all ages'),
                      ('ave_tot_deaths_eng_wales', 'number', 'Total deaths, 5 year average Eng & Wales'),
                      ('ave_tot_deaths_england', 'number', 'Total deaths, 5 year average England'),
                      ('ave_tot_deaths_wales', 'number', 'Total deaths, 5 year average Wales'),
                      ('deaths_with_resp', 'number', 'Deaths with respiratory underlying causes'),
                      ('deaths_with_covid', 'number', 'Deaths with COVID mentioned'),
                      ]
        data_table = gviz_api.DataTable(table_desc)
        data_table.LoadData(data=ret_frame.to_numpy())
        return data_table.ToJSon()

    def total_deaths_by_age_and_sex_at_date_json(self, date=None):
        persons_death_by_age_df = pd.DataFrame(data=self.weekly_figures_sheet.iloc[20:40, 2:].to_numpy(),
                                               index=age_brackets, columns=self.date_series)
        persons_death_by_age_df.dropna(axis=1, inplace=True)

        male_deaths_by_age_df = pd.DataFrame(data=self.weekly_figures_sheet.iloc[42:62, 2:].to_numpy(),
                                             index=age_brackets, columns=self.date_series)
        male_deaths_by_age_df.dropna(axis=1, inplace=True)

        female_deaths_by_age_df = pd.DataFrame(data=self.weekly_figures_sheet.iloc[64:84, 2:].to_numpy(),
                                               index=age_brackets, columns=self.date_series)
        female_deaths_by_age_df.dropna(axis=1, inplace=True)

        if date is not None:
            pdt = persons_death_by_age_df.T
            pdt.index = pd.to_datetime(pdt.index)
            mdt = male_deaths_by_age_df.T
            mdt.index = pd.to_datetime(mdt.index)
            fdt = female_deaths_by_age_df.T
            fdt.index = pd.to_datetime(fdt.index)
            totals_df = pd.DataFrame(data={'person_deaths': pdt.loc[date],
                                           'male_deaths': mdt.loc[date],
                                           'female_deaths': fdt.loc[date]}).T
        else:
            persons_death_by_age_df['total'] = persons_death_by_age_df.sum(axis=1)
            male_deaths_by_age_df['total'] = male_deaths_by_age_df.sum(axis=1)
            female_deaths_by_age_df['total'] = female_deaths_by_age_df.sum(axis=1)
            totals_df = pd.DataFrame(data={'person_deaths': persons_death_by_age_df['total'],
                                           'male_deaths': male_deaths_by_age_df['total'],
                                           'female_deaths': female_deaths_by_age_df['total']}).T

        totals_df.insert(0, 'Desc', ['persons', 'males', 'females'])
        data_table = gviz_api.DataTable(age_group_table_desc)
        data_table.LoadData(totals_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_by_age_at_week_json(self, week):
        table_desc = [('bracket', 'string', 'Age Bracket'), ('ndeaths', 'number', 'Number of Deaths')]
        data_table = gviz_api.DataTable(table_desc)
        persons_death_by_age_df = pd.DataFrame(self.weekly_figures_sheet.iloc[20:40, 2:week + 2].to_numpy(),
                                               columns=self.weekly_figures_sheet.iloc[4, 2:week + 2],
                                               index=age_brackets)
        persons_death_by_age_df['total'] = persons_death_by_age_df.sum(axis=1)
        return_data_frame = pd.DataFrame(data={'age_brackets': age_brackets,
                                               'ndeaths': persons_death_by_age_df['total'].to_numpy()})
        data_table.LoadData(data=return_data_frame.to_numpy())
        return data_table.ToJSon()

    def total_deaths_all_ages_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'All Deaths')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths_df = pd.DataFrame(data={'date': self.date_series.to_numpy(),
                                             'deaths': self.weekly_figures_sheet.iloc[7, 2:].to_numpy()
                                             })
        data_table.LoadData(data=total_deaths_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_5_year_ave_eng_and_wales_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'Average Deaths England & Wales')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths_df = pd.DataFrame(data={'date': self.date_series,
                                             'deaths': self.weekly_figures_sheet.iloc[9, 2:].to_numpy()})
        data_table.LoadData(total_deaths_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_5_year_ave_england_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'Average Deaths England')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths_df = pd.DataFrame(data={'date': self.date_series,
                                             'deaths': self.weekly_figures_sheet.iloc[11, 2:]})
        data_table.LoadData(total_deaths_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_5_year_ave_wales_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'Average Deaths Wales')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths_df = pd.DataFrame(data={'date': self.date_series,
                                             'deaths': self.weekly_figures_sheet.iloc[13, 2:]})
        data_table.LoadData(total_deaths_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_with_respiratory_causes_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'Deaths with respiratory causes')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths_df = pd.DataFrame(data={'date': self.date_series,
                                             'deaths': self.weekly_figures_sheet.iloc[16, 2:]})
        data_table.LoadData(total_deaths_df.to_numpy())
        return data_table.ToJSon()

    def total_deaths_with_covid_mentioned_df(self):
        return pd.DataFrame(data={'date': self.date_series,
                                  'deaths': self.weekly_figures_sheet.iloc[17, 2:]})

    def total_deaths_with_covid_mentioned_json(self):
        table_desc = [('date', 'date', 'Date'), ('deaths', 'number', 'Deaths with covid mentioned')]
        data_table = gviz_api.DataTable(table_desc)
        total_deaths = pd.DataFrame(data={'date': self.date_series,
                                          'deaths': self.weekly_figures_sheet.iloc[17, 2:]})
        data_table.LoadData(total_deaths.to_numpy())
        return data_table.ToJSon()

    def deaths_by_region_on_date_json(self, date):
        table_desc = [('region', 'string', 'Region'), ('deaths', 'number', 'Deaths per region')]
        data_table = gviz_api.DataTable(table_desc)
        df = pd.DataFrame(data=self.weekly_figures_sheet.iloc[85:95, 2:].T.to_numpy(),
                          index=self.date_series, columns=self.weekly_figures_sheet.iloc[85:95, 1])
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)
        regions_series = pd.Series(df.columns)
        deaths_series = pd.Series(data=df.loc[df.index.strftime('%Y-%m-%d') == date].to_numpy()[0])
        ret_frame = pd.DataFrame(data={'region': regions_series.to_numpy(),
                                       'deaths': deaths_series.to_numpy()})
        data_table.LoadData(ret_frame.to_numpy())
        return data_table.ToJSon()

    def total_deaths_by_region_at_date_json(self, date=None):
        table_desc = [('region', 'string', 'Region'), ('deaths', 'number', 'Total deaths per region')]
        data_table = gviz_api.DataTable(table_desc)
        df = pd.DataFrame(data=self.weekly_figures_sheet.iloc[85:95, 2:].T.to_numpy(),
                          index=self.date_series, columns=self.weekly_figures_sheet.iloc[85:95, 1])
        df.dropna(axis=0, inplace=True)
        if date is not None:
            wanted_frame = df.loc['2020-01-03':date]
        else:
            wanted_frame = df
        df_trans = wanted_frame.T
        df_trans['totals'] = df_trans.sum(axis=1)
        return_frame = pd.DataFrame(data={'region': df_trans.index, 'total_deaths': df_trans.totals})
        data_table.LoadData(return_frame.to_numpy())
        return data_table.ToJSon()
