import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np



# DATA LOADING & CLEANING

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]

    df['sales'] = df['Quantity'] * df['Price']
    df['year'] = df['InvoiceDate'].dt.year
    df['month'] = df['InvoiceDate'].dt.month

    return df

# MONTHLY TREND

def plot_monthly_sales(df):

    month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec']

    monthly_sales = df.groupby('month')['sales'].sum()

    plt.figure(figsize=(10,5))
    plt.plot(monthly_sales.index, monthly_sales.values, marker='o')
    plt.xticks(ticks=range(1,13), labels=month_labels)
    plt.xlabel('Month')
    plt.ylabel('Total Sales')
    plt.title('Monthly Sales Trend (UK Retail)')
    plt.tight_layout()
    plt.show()

# YEARLY TREND

def plot_yearly_sales(df):

    yearly_sales = df.groupby('year')['sales'].sum()

    plt.figure(figsize=(8,5))
    yearly_sales.plot(kind='bar')
    plt.xlabel('Year')
    plt.ylabel('Total Sales')
    plt.title('Yearly Sales Trend (UK Retail)')
    plt.tight_layout()
    plt.show()

def monthly_growth(df,yr):
    df10 = df[df['year'] == yr].copy()

    month_sales = df10.groupby('month')['sales'].sum() # grouping sales as per month of selected year
    '''growth_rate = month_sales.pct_change() * 100
    growth_rate = growth_rate.dropna()'''#shorter version but, I like the manual version of it below
    growth_rate = []
    for i in range(1, len(month_sales)):
        pre = month_sales.iloc[i - 1]
        cur = month_sales.iloc[i]
        gr = round((cur - pre) / pre * 100) if pre != 0 else 0
        growth_rate.append(gr)
    for j in range(len(growth_rate)):
        print('month', j + 2, '=', growth_rate[j], '%')

    months = month_sales.index.tolist()

    plt.figure(figsize=(10,5))
    plt.plot(months[1:], growth_rate, color='Black')
    plt.xlabel(f'Month of year-{yr}')
    plt.ylabel('Growth Rate %')
    plt.title(f'Monthly Growth Rate-{yr}')
    plt.tight_layout()
    plt.show()

def detect_demand_acceleration_signal(df,yr):
    df10 = df[df['year'] == yr].copy()
    df10 = df10.sort_values('InvoiceDate')

    df10['MA50'] = df10['sales'].rolling(50, min_periods=50).mean()
    df10['MA200'] = df10['sales'].rolling(200, min_periods=200).mean()

    df10 = df10.dropna(subset=['MA50','MA200'])

    df10['AS'] = (
        (df10['MA50'] > df10['MA200']) &
        (df10['MA50'].shift(1) <= df10['MA200'].shift(1))
    )

    gc_points = df10[df10['AS']]

    # Optional visualization (commented for business relevance)
    '''
    plt.figure(figsize=(12,5))
    plt.plot(df10['InvoiceDate'], df10['MA50'], label='50-Day MA')
    plt.plot(df10['InvoiceDate'], df10['MA200'], label='200-Day MA')

    plt.scatter(gc_points['InvoiceDate'], gc_points['MA50'], label='Demand Acceleration Signal')

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.xticks(rotation=45)
    plt.legend()
    plt.title(f'Demand_Acceleration_Signal-{yr}')
    plt.tight_layout()
    plt.show()'''

    return gc_points[['InvoiceDate','MA50','MA200']]

def country_sales(df):
    country_sale=df.groupby('Country')['sales'].sum().sort_values(ascending=False).head(10)
    country_sale=np.log10(country_sale+1)# adding 1 to avoid any log 0 crash
    print(country_sale)
    country_sale.plot(kind='bar',color='Black')
    plt.xlabel('Country')
    plt.ylabel('Sales (log10)')
    plt.title('Top 10 Country Sales')
    plt.show()

def top_product(df):
    #removing description which are not products
    remove_words=['manual','amazon fee','adjust bad debt','postage']
    df = df[~df['Description'].str.lower().str.contains('|'.join(remove_words), na=False)]
    df=df.dropna(subset=['Customer ID'])

    product_sales = df.groupby('Description')['sales'].sum().sort_values(ascending=False)
    product_volume=df.groupby('Description')['Quantity'].sum().sort_values(ascending=False)
    print('Top 10 revenue products are\n')
    print(product_sales.head(10))
    print('\n\nTop 10 no of product sold are')
    print(product_volume.head(10))
    top_pr = product_sales.index[0]
    top_sales = product_sales.iloc[0]
    total_top10 = product_sales.head(10).sum()

    contribution = (top_sales / total_top10) * 100

    print(f"\n{top_pr} contributes {round(contribution)}% of Top 10 product revenue")

def main():
    file_path = 'online_retail_II.csv'

    df = load_and_clean_data(file_path)
    st=('Enter\n '
        '1 for Monthly Sales Trend\n '
        '2 for Yearly Sales Trend\n '
        '3 for Top 10 Products and etc\n '
        '4 for Demand Acceleration Signal\n '
        '5 for Monthly Growth Rate\n '
        '6 for Country sales info\n '
        )

    try:
        choice = int(input(st))
    except ValueError:
        print("Please enter a valid number.")
        return
    if choice == 1:
        plot_monthly_sales(df)

    elif choice == 2:
        plot_yearly_sales(df)

    elif choice == 3:
        top_product(df)

    elif choice == 4:
        year=int(input('Enter year 2010 or 2011\n'))
        if (year==2010) or (year==2011):
            gc = detect_demand_acceleration_signal(df,year)
            print("\nDemand Acceleration Events:")
            print(gc)
            print(len(gc), 'number of events')

        else:
            print('Enter valid year')


    elif choice == 5:
        year = int(input('Enter year 2010 or 2011\n'))
        if (year == 2010) or (year == 2011):
            monthly_growth(df,year)

        else:
            print('Enter valid year')

    elif choice == 6:
        country_sales(df)

    else:
        print('Invalid choice')


if __name__ == "__main__":
    main()

