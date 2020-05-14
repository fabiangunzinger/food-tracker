import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_database():
    def str_to_numeric(df):
        cols = ['fat', 'carbs', 'sugar', 'fiber', 'protein']
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        return df

    def str_to_lower(df):
        cols = df.columns[df.dtypes.eq('object')]
        df[cols] = df[cols].applymap(str.lower)
        return df

    columns = {
        'Name': 'ingredient',
        'Category': 'category',
        # 'Matrix unit': 'units',
        'Fat, total (g)': 'fat',
        'Carbohydrates, available (g)': 'carbs',
        'Protein (g)': 'protein',
        'Sugars (g)': 'sugar',
        'Dietary fibres (g)': 'fiber',
    }

    path = './data/Swiss-food-composition-database-V6.1.xlsx'

    foods = (
        pd.read_excel(path, skiprows=2, usecols=columns)
        .rename(columns=columns)
        .pipe(str_to_numeric)
        .pipe(str_to_lower)
    )

    return foods


def find_item(regex, data, cat=False):
    if not cat:
        subset = data.ingredient.str.contains(regex)
    else:
        subset = data.category.str.contains(regex)
    return data[subset]


def get_meal_data(meal, data):
    """Extract grams and calories data for single meal."""
    # Grams data
    data = (data[data.ingredient.isin(meal)].copy()
            .set_index('ingredient')
            .drop(['category', 'sugar'], axis=1))
    portion = data.index.map(meal)
    grams = data.multiply(portion, axis=0)
    grams = grams[['fat', 'protein', 'fiber', 'carbs']]

    # Calories data
    calories = grams.copy()
    calories['fat'] = calories.fat * 9
    calories['carbs'] = calories.carbs * 4
    calories['protein'] = calories.protein * 4
    calories['fiber'] = calories.fiber * 2

    return {'grams': grams, 'cals': calories}


def make_data(meal_dict, data):
    """Return grams and cals data for each meal and for total."""
    meal_data = {meal: get_meal_data(meal_dict[meal], data) for meal in meal_dict}

    # Add gram and calorie totals
    totals = {}
    for measure in ['cals', 'grams']:
        pieces = []
        for meal in meal_data.keys():
            pieces.append(meal_data[meal][measure])
        total = pd.concat(pieces).groupby(level=0).sum()
        totals[measure] = total

    meal_data['Total'] = totals

    return meal_data


def meal_plots(meal_data, figsize=(14, 7)):

    def meals_autopct(values):
        def pct_labels(pct):
            if measure == 'cals':
                out =  f'{pct:.0f}%' if pct > 3 else ''
            else:
                grams = pct * total / 100
                out = f'{grams:.0f}g' if grams > 3 else ''
            return out
        return pct_labels


    num_meals = len(meal_data)
    axsize = 20

    fig, ax = plt.subplots(2, num_meals, figsize=figsize)

    ax[0, 0].set_ylabel('Grams', fontsize=axsize)
    ax[1, 0].set_ylabel('Calories', fontsize=axsize)

    for col, meal in enumerate(meal_data):
        for row, measure in enumerate(['grams', 'cals']):

            data = meal_data[meal][measure].sum()
            total = data.sum()

            ax[row, col].pie(data, autopct=meals_autopct(data),
                             wedgeprops=dict(width=0.7),
                             textprops=dict(color='white'))
            ax[row, col].set_xlabel(f'Total: {total:.0f} {measure}')
            ax[0, col].set_title(meal, fontsize=axsize)

    fig.legend(['Fat', 'Protein', 'Fiber', 'Carbs'], framealpha=0, bbox_to_anchor=(1, 1),
           bbox_transform=plt.gcf().transFigure, ncol=1, fontsize=15)


def nuts_plots(meal_data, figsize=(14, 7)):

    def nuts_autopct(values):
        def pct_labels(pct):
            grams = pct * total / 100
            return  f'{grams:.0f}g\n({pct:.0f}%)'
        return pct_labels

    fig, ax = plt.subplots(1, 4, figsize=figsize)

    axsize = 20

    df = meal_data['Total']['grams']

    for idx, nut in enumerate(df.columns):
        total = df[nut].sum()
        data = df[nut].nlargest(5) / total
        ax[idx].pie(data, autopct=nuts_autopct(data),
                    wedgeprops=dict(width=0.7),
                    textprops=dict(color='white'))
        ax[idx].set_title(nut.title(), fontsize=axsize)
        labels = [i[:25] for i in data.index]
        ax[idx].legend(labels, loc='lower center',
                       framealpha=0, borderaxespad=-7)
        ax[0].set_ylabel('Grams', fontsize=axsize)
