import pandas as pd
import xlsxwriter, random

"""
    Notes to Self
    
    We'll  use this file to create a dict with some attributes broken down by school district
    
    We'll use one of those attributes to create a proportional stratified sample 

    Sample groups should be broken up by # schools meeting these bounds:
    Small 0 - 10
    Medium 10 - 30
    Large 30+

    Some cities are coming up missing in the cross-reference, which is soooo annoying
        - For the Bastrop example, it shows up for the first district and then not for the other...fuck.
        - For the Jourdanton example, it doesn't show up for the first but it shows up for the second and third...double fuck
"""

"""
    sheet       description
    0           List of schools with city and district information
    1           List of cities and their demographics (includes city-population data)
    2           Working document; Simple names of cities & their population
"""

sample_size = 30
bounds = [10, 30]

chosen_districts_output_file = open("Chosen Districts.txt", "w")

file_name = "Schools_2022_to_2023.xlsx"
sheet = 0
df = pd.read_excel(io=file_name, sheet_name=sheet)

# Create a new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('district_population.xlsx')
worksheet = workbook.add_worksheet()

"""
    This will use a list of schools to build a list of cities that are associated with each school district
    
    dict = {
                schoolDistrict1: {
                    cities: [city1, city2]
                }
            }
"""

# create a dict; key - school district; value - list of cities that are in-district
all_districts = df["USER_District_Name"].unique().tolist()
district_data_dict = {}

# sanity check - we should have around 1,207 school districts in Texas (source: Texas Edu Agency)
print("We should have a little over 1200 school districts; we found {}\n".format(len(all_districts)))


"""
    uses df row to aggregate attributes from google sheet into the dict
    
    could've used iloc or something but this seems clearer for some reason
"""
def aggregate_and_add_School_Attributes(dict, row, attribute_column):
    dict_value = row[attribute_column]

    if dict_value == "":
        return

    district = row['USER_District_Name']

    if district not in dict.keys():
        dict[district] = {}

    if attribute_column in dict[district].keys():
        attribute_values = dict[district][attribute_column]
    else:
        attribute_values = []

    if dict_value not in attribute_values:
        attribute_values.append(dict_value)
        dict[district][attribute_column] = attribute_values


# iterate through rows of schools
for index, row in df.iterrows():
    aggregate_and_add_School_Attributes(district_data_dict, row, 'City')
    aggregate_and_add_School_Attributes(district_data_dict, row, 'USER_School_Name')

num_schools = []
for district in district_data_dict.keys():
    num = len(district_data_dict[district]["USER_School_Name"])
    num_schools.append(num)

avg = sum(num_schools) // len(num_schools)

num_schools.sort()
mid = len(num_schools) // 2
median = int((num_schools[mid] + num_schools[~mid]) / 2)

min = num_schools[0]
max = num_schools[-1]

print("***Based on Num Schools Per District***")
print("Average: {}".format(avg))
print("Minimum: {}".format(min))
print("Maximum: {}".format(max))
print("Median: {}".format(median))
print("***************************************\n")

small_cohort_population = 0
medium_cohort_population = 0
large_cohort_population = 0
for num in num_schools:
    if num <= bounds[0]:
        small_cohort_population += 1
    elif num <= bounds[1]:
        medium_cohort_population += 1
    else:
        large_cohort_population += 1

print("Small_Cohort_Population: {} \t Medium_Cohort_Population: {} \t Large_Cohort_Population: {}".format(small_cohort_population, medium_cohort_population, large_cohort_population))

total = small_cohort_population + medium_cohort_population + large_cohort_population
sample_size_small = small_cohort_population * sample_size // total
sample_size_medium = round(medium_cohort_population / total * sample_size)
sample_size_large = round(large_cohort_population / total * sample_size)
print("Small_Cohort_Sample_Size: {} \t Medium_Cohort_Sample_Size: {} \t Large_Cohort_Sample_Size: {}".format(sample_size_small, sample_size_medium, sample_size_large))

"""
Next steps
    Create a list of districts in each cohort
    Randomly select indices from the list of district in each cohort
    
    Publish a document with the names of districts that will be included in each cohort sample
"""
small_cohort = []
medium_cohort = []
large_cohort = []

for district in district_data_dict.keys():
    if len(district_data_dict[district]["USER_School_Name"]) <= bounds[0]:
        small_cohort.append(district)
    elif len(district_data_dict[district]["USER_School_Name"]) <= bounds[1]:
        medium_cohort.append(district)
    else:
        large_cohort.append(district)

print("\nSelecting Districts for Small Cohort...")
chosen_districts_output_file.write("*****Small Cohort*****\n")
for small_cohort_district in range(sample_size_small):
    index = random.randint(0, small_cohort_population)
    chosen_districts_output_file.write(small_cohort[index] + "\n")


print("Selecting Districts for Medium Cohort...")
chosen_districts_output_file.write("\n*****Medium Cohort*****\n")
for medium_cohort_district in range(sample_size_medium):
    index = random.randint(0, medium_cohort_population)
    chosen_districts_output_file.write(medium_cohort[index] + "\n")


print("Selecting Districts for Large Cohort...")
chosen_districts_output_file.write("\n*****Large Cohort*****\n")
for large_cohort_district in range(sample_size_large):
    index = random.randint(0, large_cohort_population)
    chosen_districts_output_file.write(large_cohort[index] + "\n")

chosen_districts_output_file.close()
"""
    This will use the above dict and the city-population sheet to add a population attribute to the dict
    
    dict = {
                schoolDistrict1: {
                    cities: [city1, city2],
                    population: <INT>
                }
            }
"""

# Code for above
"""


sheet = 1
df = pd.read_excel(io=file_name, sheet_name=sheet)

# used for debugging
for index, row in df.iterrows():
    city = row["Geography"]
    if str(city) == "nan":
        continue
    print(str(city).lower())

for district in district_data_dict.keys():
    print(district)
    associated_cities = district_data_dict[district]["City"]
    missing_cities = associated_cities
    print("******* {}: {} *******".format(district, " ".join(associated_cities)))
    for associated_city in associated_cities:
        for index, row in df.iterrows():
            city = row["Geography"]

            # Skip rows with missing data
            if str(city) == "nan":
                continue

            if str(associated_city).lower() in str(city).lower():
                try:
                    missing_cities.remove(associated_city)
                except:
                    print("tried removing something that doesn't exist")
                city_pop = int(str(row["Best Population Estimate"]).replace(",",""))
                #print(associated_city, city, city_pop)

    try:
        if len(missing_cities) > 0:
            print("\nMissing Cities: {}\n\n\n".format(' '.join(missing_cities)))
    except:
        print("something weird happened for {}".format(district))
"""



