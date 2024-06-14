import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
# Part 1 (mandatory)

## 1.1 Collection of TINs of organizations with Sber's shareholding and information on the authorized capital

# Function for retrieving data from Wikipedia
def get_sber_companies():
    url = "https://ru.wikipedia.org/wiki/Категория:Дочерние_компании_Сбербанка"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    category_groups = soup.find_all("div", class_="mw-category-group")
    companies = []

    for category_group in category_groups:
        category_companies = category_group.find("ul")
        companies_from_group = category_companies.find_all("li")
        for company in companies_from_group:
            company_link = company.find("a")
            if company_link:
                company_name = company_link.text
                # INN search
                search_inn = f"https://www.prima-inform.ru/search/?query={company_name}"

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }

                search_inn_response = requests.get(search_inn, headers=headers)
                search_inn_soup = BeautifulSoup(search_inn_response.content, "html.parser")
                inn = None
                try:
                    inn = search_inn_soup.find("span", class_="result_list_table__req").text.split("\n")[0].split(": ")[1]
                except:
                    continue

                companies.append({"name": company_name, "inn": inn})

    return companies


# Obtaining data and creating a DataFrame
companies = get_sber_companies()
df = pd.DataFrame(companies)
print (df)

## 1.2 Collection of procurement data from zakupki.gov.ru website and analysis

# Function for obtaining procurement data from the website zakupki.gov.ru
def get_procurements_data():
    currency_rates = {
        "$": 89,
        "€": 95,
        "₽": 1
    }

    url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D0%BE%D0%B1%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_100&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=01.01.2021&publishDateTo=31.01.2021&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&okpd2Ids=&okpd2IdsCodes="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    pages=soup.find_all("li",class_="page")[-1].text.replace("\n","")
    result=0
    for i in range(int(pages)):
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D0%BE%D0%B1%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber={i + 1}&sortDirection=false&recordsPerPage=_100&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=01.01.2021&publishDateTo=31.01.2021&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&okpd2Ids=&okpd2IdsCodes="
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        costs=soup.find_all("div",class_="price-block__value")
        for cost in costs:
            cost_text = cost.text.strip()
            cost_value = int(re.sub(r'[^\d]+', '', re.sub(r'[, ]', '', cost_text)))//100
            currency = re.search(r'[^0-9\s,]$', cost_text).group()
            if currency in currency_rates:
                cost_value = cost_value * currency_rates[currency]
                result += cost_value
            else:
                print(f"Неизвестная валюта: {currency}")
    print("Все закупки:" + str(result))
    procurements = []
    for inn in df['inn']:
        result_for_one_company=0
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={inn}&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D0%BE%D0%B1%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_100&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=01.01.2021&publishDateTo=31.01.2021&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&okpd2Ids=&okpd2IdsCodes="
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        costs = soup.find_all("div", class_="price-block__value")
        cost_details=[]
        share_details=[]
        for cost in costs:
            cost_text = cost.text.strip()
            cost_value = int(re.sub(r'[^\d]+', '', re.sub(r'[, ]', '', cost_text))) // 100
            currency = re.search(r'[^0-9\s,]$', cost_text).group()
            if currency in currency_rates:
                cost_value = cost_value * currency_rates[currency]
                result_for_one_company += cost_value
                cost_details.append(cost_value)
                share_details.append(cost_value/result*100)
        share=result_for_one_company/result*100
        procurements.append({"inn": inn, "cost": result_for_one_company, "share":share,"cost_details":cost_details, "share_details":share_details})

    return procurements

# Obtaining procurement data for January 2021
procurements_data = get_procurements_data()
procurements_df = pd.DataFrame(procurements_data)
print(procurements_df)

### 1.2.1 Calculation of the share of purchases for TINs from 1.1.1

# Consolidation of company and procurement data
merged_df = pd.merge(df, procurements_df, on='inn', how='left')
print(merged_df[['name', 'inn', 'cost', 'share', 'cost_details','share_details']])

### 1.2.2 Construction of the graph by all TINs

# Graph creation
G = nx.Graph()

# Adding vertices and edges
for _, row in merged_df.iterrows():
    inn = row['inn']
    cost_details = row['cost_details']
    share_details = row['share_details']

    # Adding a vertex for an organization
    org_node = f"{row['name']} ({inn})"
    G.add_node(org_node, node_color='red', label=row['name'])



    # Adding vertices and edges for purchases
    for cost, share in zip(cost_details, share_details):
        # cost_node = str(cost)
        share_node = f"{share:.5f}"
        # G.add_node(cost_node, node_label=share_node)  # Подписывание вершин закупок долей
        G.add_node(share_node, node_color='blue', label=share_node)
        G.add_edge(org_node, share_node, weight=cost)  # Ребро только между организацией и закупкой

# Graph visualization
pos = nx.kamada_kawai_layout(G)
edge_weights = nx.get_edge_attributes(G, 'weight')
max_weight = max(edge_weights.values())
normalized_weights = {edge: weight / max_weight for edge, weight in edge_weights.items()}

node_colors = nx.get_node_attributes(G, 'node_color')
node_labels = nx.get_node_attributes(G, 'label')
default_node_color = 'lightblue'

fig, ax = plt.subplots(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, labels=node_labels, node_color=[node_colors.get(node, default_node_color) for node in G.nodes()], edge_color="gray", ax=ax)
nx.draw_networkx_edges(G, pos, width=[normalized_weights[edge] * 5 for edge in G.edges()], ax=ax)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_weights, font_size=8, bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), ax=ax)

plt.tight_layout()
plt.show()


# # Part 2 (desirable - to unlock skills)
#
# ## 2.1 Autoclustering of graph by attributes of edges and visualization of clusters
#
# Creating a new DataFrame with share_details statistics
statistic_df = merged_df[['name', 'inn']].copy()
statistic_df['min'] = merged_df['share_details'].apply(lambda x: np.min(x) if len(x) > 0 else np.nan)
statistic_df['max'] = merged_df['share_details'].apply(lambda x: np.max(x) if len(x) > 0 else np.nan)
statistic_df['std'] = merged_df['share_details'].apply(lambda x: np.std(x) if len(x) > 0 else np.nan)
statistic_df['median'] = merged_df['share_details'].apply(lambda x: np.median(x) if len(x) > 0 else np.nan)

print(statistic_df)

# Apply PCA to reduce dimensions to 2
reduced_df = statistic_df.drop(["name","inn"],axis=1)
# Encode NaN values with zeros
reduced_df.fillna(0, inplace=True)

# Perform K-Means clustering
# n_clusters - определели заранее, после чего указали 3 центра
kmeans = KMeans(n_clusters=3, random_state=42)
reduced_df['Cluster'] = kmeans.fit_predict(reduced_df)
pca = PCA(n_components=2)
pca_result = pca.fit_transform(reduced_df.iloc[:, :-1])
reduced_df['PCA1'] = pca_result[:, 0]
reduced_df['PCA2'] = pca_result[:, 1]


# Plot the PCA result
plt.figure(figsize=(10, 6))
plt.scatter(reduced_df['PCA1'], reduced_df['PCA2'], c=reduced_df['Cluster'], cmap='viridis', marker='o')

plt.xlabel('PCA1')
plt.ylabel('PCA2')
plt.title('PCA of Clusters from 4 Features')
plt.show()
