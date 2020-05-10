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
        'Name': 'name',
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
        .pipe(str_to_lower, ['name', 'category'])
        .pipe(strip_strings, ['name'])
        .dropna(how='any'))
    return df


def find_food(data, item, cat=False):
    if not cat:
        out = data[data.name.str.contains(item)]
    else:
        out = data[data.category.str.contains(item)]
    return out
