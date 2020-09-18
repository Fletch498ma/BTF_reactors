'''
Created on 10/03/2020

@author: Fletcher Gilbertson
'''
#function for appending csv
def append_list_as_row(file_name, list_of_elem):
    from csv import writer
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)