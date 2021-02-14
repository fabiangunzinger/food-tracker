import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

my_foods = {
    # fat, carbs, sugar, fiber, protein
    'almond butter': ['pip & nut almond butter', 'added', 54, 7.5, 4.6, np.nan , 27],
    'macadamias': ['macadamia nuts', 'added', 75.3, 6.2, 3.8, 6.3, 9.0],
    'chicory coffee': ['chicory coffee', 'added', 0.5, 73.2, 28.2, 15.3, 3.5],
    'spirulina': ['spirulina', 'added', 8, 24, 3.1, 3.6, 57],
    'cheddar': ['cheddar', 'added', 34.9, 0.1, 0.1, 0, 25.4],
    'kallo chicken stock': ['kallo chicken stock cube (1 cube)', 'added', 2.5, 3, 0.5, np.nan, 0.5],
    'heck chicken sausages': ['heck chicken sausages', 'added', 3.9, 1.6, 0.6, np.nan, 21.5],
    'tesco bacon': ['tesco bacon', 'added', 15.9, 1, 0.2, 0.7, 19], 
    'marigold veg bouillon': ['marigold veg bouillon', 'added', 8.5, 30.1, 10.5, np.nan, 10.1],
    'tesco wild salmon': ['tesco wild salmon', 'added', 2.7, 1.1, 0, 0, 20],
    'beef mince (tesco finest)': ['beef mince (tesco finest)', 'added', 14.5, 0, 0, 0, 19.7],
    'pride coconut milk': ['pride coconut milk', 'added', 15, 1.6, 1.6, np.nan, 1],
    'alpro coconut milk': ['alpro coconut milk', 'added', 1.2, 0, 0, 0.1, 0.1],
    'tesco coconut cream': ['tesco coconut cream', 'added', 20, 1.5, 1.5, 1.5, 1.3],
    'tesco chicken thighs and drummsticks': ['tesco chicken thighs and drummsticks', 'added', 14, 0, 0, 0, 17],
    'tesco chia seeds': ['tesco chia seeds', 'added', 27.7, 2.4, 0.6, 33.8, 23.9],
    'tesco milled flax, pumpkin, chia seed mix': ['tesco milled flax, pumpkin, chia seed mix', 'added', 44.8, 6.4, 2.8, 16.4, 26.4],
    'tesco organic chicken thigh fillet': ['tesco organic chicken thigh fillet', 'added', 9.8, 0, 0, 0, 18.3],
    'tesco fat free cottage cheese': ['tesco fat free cottage cheese', 'added', 0.3, 4.7, 4.7, 0, 10.1],
    'myprotein whey isolate': ['myprotein whey isolate', 'added', 0, 0, 0, 0, 90],
    'myprotein eggwhite powder': ['myprotein eggwhite powder', 'added', 0.3, 5.3, 0, 0, 78],
    'tesco organic broccoli': ['tesco organic broccoli', 'added', 0.7, 3.3, 1.8, 4, 4.4],
    'engevita yeast flakes': ['engevita yeast flakes', 'added', 4, 36.9, 12.4, 22, 51],
}


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
#         'Matrix unit': 'units',
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
    
    cols = foods.columns
    new_foods_df = pd.DataFrame(my_foods.values(), columns=cols)
    foods = foods.append(new_foods_df, ignore_index=True)
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
                             textprops=dict(color='white', fontsize=15))
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
