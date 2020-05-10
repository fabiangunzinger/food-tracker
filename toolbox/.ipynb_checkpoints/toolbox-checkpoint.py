import pandas as pd
import matplotlib.pyplot as plt

def read(file):
    df = ((pd.read_excel(file, skiprows=2, usecols=columns))
          .rename(columns, axis=1)
          .pipe(str_to_numeric, ['fat', 'carbs', 'fiber', 'protein'])
          .pipe(str_to_lower, ['name', 'category'])
          .pipe(strip_strings, ['name'])
          .assign(net_carbs = lambda df: df.carbs - df.fiber)
          .dropna(how='any'))
    return df


columns = {
    'Name': 'name',
    'Kategorie': 'category',
    'Bezugseinheit': 'units',
    'Energie, Kalorien': 'calories',
    'Fett, total (g)': 'fat',
    'Kohlenhydrate, verfügbar (g)': 'carbs',
    'Nahrungsfasern (g)': 'fiber',
    'Protein (g)': 'protein'
}


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


def find_item(data, item):
    return data[data.name.str.contains(item)]


def make_myfoods(data, foods):
    df = data.copy()
    df = df.loc[data.name.isin(foods)]
    df['name'] = df['name'].map(foods)
    return df


def calc_nutrients(foods, portions):
    """
    Calculate nutrients for portions.
    """
    pieces = []
    nutrients = ['calories', 'fat', 'protein', 'net_carbs']
    for ingredient, portion in portions.items():
        nuts = foods.loc[foods.name == ingredient, nutrients] * portion
        pieces.append(nuts)
        
    nutrients = pd.concat(pieces)
    nutrients[nutrients < 0] = 0
    return nutrients.sum()


def make_doughnut(data, title, axis):
    """
    Create a piechart based on nutrition data.
    """
    calories = data[0]
    macros = data[1:]
    
    def func(pct, allvals):
        absolute = int(pct / 100 * sum(allvals))
        return f"{pct:.1f}%\n({absolute:.1f} g)"

    wedges, _, _ = ax[axis].pie(macros, wedgeprops=dict(width=0.7),
                          textprops=dict(color='white', size=15),
                          autopct=lambda pct: func(pct, macros))
    ax[axis].legend(wedges, macros.index,
              bbox_to_anchor=(.3, -1, .5, 1),
              fontsize=15)
    ax[axis].set_title(f'{title}\nTotal calories: {calories}',
                 fontdict=dict(size=18));