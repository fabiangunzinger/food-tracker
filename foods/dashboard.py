import pandas as pd


def read_raw():

    def strip_strings(df, columns):
        """
        Remove leading and trailing whitespace from strings.
        """
        df = df.copy()
        def strip(col):
            return col.str.strip()

        df[columns] = df[columns].apply(strip)
        return df

    def str_to_numeric(df, columns):
        """
        Convert string columns to numeric.
        """
        df = df.copy()
        def converter(col):
            return pd.to_numeric(col, errors='coerce')

        df[columns] = df[columns].apply(converter)
        return df

    def str_to_lower(df, columns):
        """
        Convert string columns to lower-case.
        """
        df = df.copy()
        def converter(col):
            return col.str.lower()

        df[columns] = df[columns].apply(converter)
        return df

    columns = {
        'Name': 'ingredient',
        'Category': 'category',
        'Matrix unit': 'units',
        'Energy, kilocalories (kcal)': 'calories',
        'Fat, total (g)': 'fat',
        'Carbohydrates, available (g)': 'carbs',
        'Sugars (g)': 'sugar',
        'Dietary fibres (g)': 'fiber',
        'Protein (g)': 'protein',
    }

    file = './data/Swiss-food-composition-database-V6.1.xlsx'

    df = (
        pd.read_excel(file, skiprows=2, usecols=columns)
        .rename(columns, axis=1)
        .pipe(str_to_numeric, ['fat', 'carbs', 'fiber', 'protein'])
        .pipe(str_to_lower, ['ingredient', 'category'])
        .pipe(strip_strings, ['ingredient'])
        .dropna(how='any')
    )
    return df


def find_food(data, item, cat=False):
    if not cat:
        out = data[data.ingredient.str.contains(item)]
    else:
        out = data[data.category.str.contains(item)]
    return out


def calc_nuts(meals, include_total=True):
    """Calculate nutrient content for each meal and for daily total."""

    def calc_meal_nuts(meal_dic, data=myfoods):
        """Calculate nutrient content for a meal."""
        columns = ['fat', 'protein', 'carbs', 'fiber']
        cals_per_g = {'fat': 9, 'carbs': 4, 'protein': 4, 'fiber': 2}

        def calc_share(group):
            group['share'] = group.value / group.value.sum()
            return group

        df = (data
              .loc[data.index.isin(meal_dic), columns]
              .reset_index()
              .melt(id_vars='ingredient', var_name='nutrient', value_name='grams')
              .assign(portion = lambda x: x.ingredient.map(meal_dic))
              .assign(grams = lambda x: x.grams * x.portion)
              .assign(cals_per_gram = lambda x: x.nutrient.map(cals_per_g))
              .assign(cals = lambda x: x.grams * x.cals_per_gram)
              .drop(['cals_per_gram', 'portion'], axis=1)
              .melt(id_vars=['ingredient', 'nutrient'],
                    var_name='measure')
              .groupby('measure')
              .apply(calc_share)
              .assign(nutrient = lambda df: pd.Categorical(df.nutrient, ['fat', 'protein', 'carbs', 'fiber']))
             )

        return df

    def add_total(data):
        total = data.copy()
        total['share'] = total.share / total.meal.nunique()
        total = data.groupby(['ingredient', 'nutrient', 'measure']).sum()
        total['meal'] = 'Day total'
        total.reset_index(inplace=True)
        df = pd.concat([data, total], ignore_index=True)

        meal_order = list(meals.keys())
        meal_order.append('Day total')
        df['meal'] = pd.Categorical(df.meal, meal_order)
        df = df.sort_values(['measure', 'meal', 'nutrient'])

        return df

    def make_meals_plot_data(data):
        return data.groupby(['measure', 'meal', 'nutrient'], as_index=False).sum()

    pieces = []
    for meal in meals:
        df = calc_meal_nuts(meals[meal])
        df['meal'] = meal
        pieces.append(df)
    data = pd.concat(pieces)

    if include_total:
        data = add_total(data)

    data_table = data
    meals_plot_data = make_meals_plot_data(data)

    return data_table, meals_plot_data


def make_dashboard(data):

    title_size = 25
    label_size = 20
    nrows = data.measure.nunique()
    ncols = data.meal.nunique()


    def pct_labels(pct, df, measure):
        if measure == 'cals':
            return f'{pct:.0f}%' if pct > 3 else ''
        elif measure == 'grams':
            grams = pct / 100 * df.value.sum()
            return f'{grams:.0f}g' if grams > 5 else ''


    fig, ax = plt.subplots(nrows, ncols, figsize=(19, 9))

    for row, measure in enumerate(data.measure.unique()):
        for col, meal in enumerate(data.meal.unique()):
            df = data.loc[(data.measure == measure) & (data.meal == meal)]
            ax[row, col].pie(df.share,
                             labels=df.nutrient,
                             textprops=dict(color='white', size=label_size),
                             wedgeprops=dict(width=.7),
                             autopct=lambda pct: pct_labels(pct, df, measure)
                            )
            ax[row, col].set_xlabel(f'Total: {df.value.sum():.0f}')

    # Set column and row labels
    ax[0, 0].set_ylabel('Calories', fontsize=title_size)
    ax[1, 0].set_ylabel('Grams', fontsize=title_size)
    for col, name in enumerate(data.meal.unique()):
        ax[0, col].set_title(name, fontsize=title_size)

    legend_labs = [n.capitalize().replace('_', ' ') for n in data.nutrient.unique()]
    fig.legend(legend_labs, loc='lower center', ncol=4, fontsize=title_size,
               framealpha=0, borderaxespad=-0.3)
    fig.tight_layout();


def make_nutrient_graphs(data):

    title_size = 25
    label_size = 20

    def get_top(group, n):
        return group.sort_values('share', ascending=False)[:n]

    def calc_share(group):
        group['share'] = group.value / group.value.sum()
        return group

    data = data.groupby(['measure', 'meal', 'nutrient']).apply(calc_share)
    conds = (data.measure == 'cals') & (data.meal == 'Day total')
    data = data.loc[conds].groupby(['meal', 'nutrient']).apply(get_top, 5)

    fig, ax = plt.subplots(1, len(data.nutrient.unique()), figsize=(19, 9))

    for col, nutrient in enumerate(data.nutrient.unique()):
        df = data.loc[data.nutrient == nutrient]
        ax[col].pie(df.share,
                 labels=df.ingredient,
                 textprops=dict(color='white', size=label_size),
                 wedgeprops=dict(width=.7),
                 autopct='%1.1f%%'
                )
        ax[col].set_title(nutrient, fontsize=title_size)
        ax[col].legend(loc='lower center', ncol=1, fontsize=15,
                   framealpha=0, borderaxespad=-7)


