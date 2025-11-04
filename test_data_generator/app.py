# importing Flask and other modules
from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from os import path
import pandas as pd
import json
import test_data_generator
import shutil
import heapq
import csv
import glob
from datetime import datetime
 
# Flask constructor
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FOLDER = 'data'
app.config['DATA_FOLDER'] = DATA_FOLDER

TEST_DATA_FOLDER = 'test_data'
app.config['TEST_DATA_FOLDER'] = TEST_DATA_FOLDER

METADATA_FOLDER = 'metadata'
app.config['METADATA_FOLDER'] = METADATA_FOLDER

LOG_FOLDER = 'log'
app.config['LOG_FOLDER'] = LOG_FOLDER

def create_folders():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(TEST_DATA_FOLDER):
        os.makedirs(TEST_DATA_FOLDER)
    if not os.path.exists(METADATA_FOLDER):
        os.makedirs(METADATA_FOLDER)
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

def remove_folders():
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    if os.path.exists(DATA_FOLDER):
        shutil.rmtree(DATA_FOLDER)
    if os.path.exists(TEST_DATA_FOLDER):
        shutil.rmtree(TEST_DATA_FOLDER)
    if os.path.exists(METADATA_FOLDER):
        shutil.rmtree(METADATA_FOLDER)
    if os.path.exists(LOG_FOLDER):
        shutil.rmtree(LOG_FOLDER)

def remove_log_folder():
    if os.path.exists(LOG_FOLDER):
        shutil.rmtree(LOG_FOLDER)

def remove_dictionaries():
    if os.path.exists('data/index.json'):
        os.remove('data/index.json')
    if os.path.exists('data/key_combo.json'):
        os.remove('data/key_combo.json')
    if os.path.exists('data/miscellaneous.json'):
        os.remove('data/miscellaneous.json')
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def form():
    success_message = None
    input_table = None
    input_column_list = None
    table_column_combo_dict = None
    primary_table_name = None
    primary_column_name = None
    index_dict = {}
    file_data = {}
    key_combo_dict = {}
    miscellaneous_dict = {}

    create_folders()

    if path.isfile('data/key_combo.json'):
        key_combo_dict = read_json('data/key_combo.json')
    else:
        write_json(key_combo_dict,'data/key_combo.json')

    if path.isfile('data/index.json'):
        index_dict = read_json('data/index.json')
    else:
        write_json(index_dict,'data/index.json')

    if path.isfile('data/miscellaneous.json'):
        miscellaneous_dict = read_json('data/miscellaneous.json')
    else:
        write_json(miscellaneous_dict,'data/miscellaneous.json')

    if os.path.exists(LOG_FOLDER) and len(os.listdir(LOG_FOLDER)) > 0:
        miscellaneous_dict['does_log_exist'] = True
        delete_old_files(LOG_FOLDER)
    else:
        miscellaneous_dict['does_log_exist'] = False
    
    write_json(miscellaneous_dict,'data/miscellaneous.json')

    current_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_name = 'log/log_generated_at_' + current_time_str + '.txt'

    if request.method == "POST":
        #Section of reset
        if request.form.get('resetIndex') == 'ResetIndex':
            remove_dictionaries()
            return redirect(url_for('form'))

        if request.form.get('resetAll') == 'ResetAll':
            remove_folders()
            return redirect(url_for('form'))

        # getting input with name = inputTable in HTML form
        if request.form.get('generateCSV') == 'Generate CSV':
            input_table = request.form.get("inputTable")
            number_of_records = request.form.get("number")
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                filename = file.filename
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                new_filename = input_table + '.csv'
                new_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                test_data_path = os.path.join(app.config['TEST_DATA_FOLDER'], new_filename)
                metadata_path = os.path.join(app.config['METADATA_FOLDER'], new_filename)
                
                # Check if file with the same name exists and delete it
                if os.path.exists(new_upload_path):
                    os.remove(new_upload_path)
                
                file.save(upload_path)
                os.rename(upload_path, new_upload_path)
            success_message = f"Test Data for {input_table} has been generated successfully"


            # This section prepares the table_column_combo dictionary, where all column details against each table is provided
            input_column_list = read_column_from_csv(new_upload_path)
            table_column_combo_dict = {"table_metadata":[{
                        "table_name" : input_table,
                        "list_of_columns" : input_column_list
                        }]}
            if path.isfile('data/table_column_combo.json') is False:
                write_json(table_column_combo_dict)
            else:
                file_data = read_json()
                if len(file_data["table_metadata"]) > 0:
                    file_data = read_json()
                    filtered_data = [item for item in file_data['table_metadata'] if item['table_name'] != input_table]
                    new_data = ({
                            "table_name" : input_table,
                            "list_of_columns" : input_column_list
                            })

                    filtered_data.append(new_data)
                    table_column_combo_dict = {"table_metadata":filtered_data}
                    write_json(table_column_combo_dict)
                else:
                    write_json(table_column_combo_dict)

            test_data_generator.generate_test_data(new_upload_path, test_data_path, metadata_path, number_of_records)

        if request.form.get('chooseRelation') == 'Define Relation':
            miscellaneous_dict['Define Relation'] = 'yes'
            write_json(miscellaneous_dict,'data/miscellaneous.json')
        
        if request.form.get('getColumns') == 'Get Columns':
            primary_table_name = request.form.get('getTable')
            if len(key_combo_dict.keys()) == 0 or len(key_combo_dict['key_combo']) == 0:
                key_combo_dict = {"key_combo":[{
                        "primary_table_name" : primary_table_name,
                        "primary_column_name" : "",
                        "foreign_table_name" : "",
                        "foreign_column_name" : ""
                        }]}
            else:
                if key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['primary_column_name'] == ''\
                or key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['foreign_table_name'] == ''\
                or key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['foreign_column_name'] == '':
                    pass
                else:
                    filtered_data = [item for item in key_combo_dict['key_combo']]
                    new_data = ({
                            "primary_table_name" : primary_table_name,
                            "primary_column_name" : "",
                            "foreign_table_name" : "",
                            "foreign_column_name" : ""
                            })

                    filtered_data.append(new_data)
                    key_combo_dict = {"key_combo":filtered_data}
            serial_adjustment(key_combo_dict)
            write_json(key_combo_dict, 'data/key_combo.json')
            
            if key_combo_dict:
                table_details_dict = read_json()
                for index, item in enumerate(table_details_dict["table_metadata"]):
                    if item['table_name'] == key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['primary_table_name']:
                        read_json('data/index.json')
                        index_dict['pindex'] = index
                        write_json(index_dict, 'data/index.json')
                    
        if request.form.get('primarySelection') == 'Finalize Primary Key':
            if key_combo_dict:
                primary_column_name = request.form.get('getColumn')
                key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['primary_column_name'] = primary_column_name
                serial_adjustment(key_combo_dict)
                write_json(key_combo_dict, 'data/key_combo.json')

        if request.form.get('getFColumns') == 'Get FColumns':
            if key_combo_dict:
                foreign_table_name = request.form.get('getFTable')
                key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['foreign_table_name'] = foreign_table_name
                serial_adjustment(key_combo_dict)
                write_json(key_combo_dict, 'data/key_combo.json')

                table_details_dict = read_json()
                for index, item in enumerate(table_details_dict["table_metadata"]):
                    if item['table_name'] == key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['foreign_table_name']:
                        read_json('data/index.json')
                        index_dict['findex'] = index
                        write_json(index_dict, 'data/index.json')

        if request.form.get('foreignSelection') == 'Finalize Foreign Key':
            if key_combo_dict:    
                foreign_column_name = request.form.get('getFColumn')
                key_combo_dict['key_combo'][len(key_combo_dict['key_combo']) - 1]['foreign_column_name'] = foreign_column_name
                serial_adjustment(key_combo_dict)
                write_json(key_combo_dict, 'data/key_combo.json')

        if request.form.get('applyAll') == 'applyAllRelation':
            if key_combo_dict and len(key_combo_dict["key_combo"])>0:
                for i in range(len(key_combo_dict["key_combo"])):
                    test_data_generator.inject_data('test_data/' + key_combo_dict["key_combo"][i]['primary_table_name'] + '.csv', \
                                                    key_combo_dict["key_combo"][i]['primary_column_name'], \
                                                        'test_data/' + key_combo_dict["key_combo"][i]['foreign_table_name'] + '.csv', \
                                                            key_combo_dict["key_combo"][i]['foreign_column_name'], \
                                                                log_file_name = log_file_name)

                os.remove('data/key_combo.json')
                return redirect(url_for('form'))

        if key_combo_dict:
            for i in range(1,(len(key_combo_dict['key_combo'])+1)):
                if request.form.get('delete'+str(i)) == 'Delete'+str(i):
                    delete_row(i)

    return render_template("form.html", success_message = success_message, table_details_dict = read_json(), \
                        key_combo_dict = read_json('data/key_combo.json'), index_dict = read_json('data/index.json'), \
                            miscellaneous_dict = read_json('data/miscellaneous.json'))


@app.route("/download", methods=["POST", "GET"])
def download():
    miscellaneous_dict = {}
    metadata_dict = {}
    top10_dict = {}

    create_folders()
    
    if path.isfile('data/miscellaneous.json'):
        miscellaneous_dict = read_json('data/miscellaneous.json')
    else:
        write_json(miscellaneous_dict,'data/miscellaneous.json')

    if path.isfile('data/metadata.json'):
        metadata_dict = read_json('data/metadata.json')
    else:
        write_json(metadata_dict,'data/metadata.json')
    
    if path.isfile('data/top10data.json'):
        top10_dict = read_json('data/top10data.json')
    else:
        write_json(top10_dict,'data/top10data.json')

    if os.path.exists(LOG_FOLDER) and len(os.listdir(LOG_FOLDER)) > 0:
        miscellaneous_dict['does_log_exist'] = True
        delete_old_files(LOG_FOLDER)
    else:
        miscellaneous_dict['does_log_exist'] = False

    write_json(miscellaneous_dict,'data/miscellaneous.json')

    if request.method == "POST":
        if request.form.get('getDetails') == 'Get Details':
            input_table = request.form.get('getTable')
            if input_table:
                miscellaneous_dict['table_details_required'] = input_table

                metadata_file_dir = os.path.join(os.getcwd(), app.config['METADATA_FOLDER'])
                metadata_file_name = os.path.join(metadata_file_dir, miscellaneous_dict['table_details_required']+'.csv')
                test_data_file_dir = os.path.join(os.getcwd(), app.config['TEST_DATA_FOLDER'])
                test_data_file_name =  os.path.join(test_data_file_dir, miscellaneous_dict['table_details_required']+'.csv')

                if os.path.exists(metadata_file_name):
                    miscellaneous_dict['metadata_file_present'] = 'yes'
                    miscellaneous_dict['metadata_file_name'] = metadata_file_name
                if os.path.exists(test_data_file_name):
                    miscellaneous_dict['test_data_file_present'] = 'yes'
                    miscellaneous_dict['test_data_file_name'] = test_data_file_name

                metadata_dict = csv_reader(metadata_file_name)
                top10_dict = {}

        if request.form.get('fetchTop10') == 'Top 10 Records':
            input_table = request.form.get('getTable')
            if input_table:
                miscellaneous_dict['table_details_required'] = input_table
                test_data_file_dir = os.path.join(os.getcwd(), app.config['TEST_DATA_FOLDER'])
                test_data_file_name =  os.path.join(test_data_file_dir, miscellaneous_dict['table_details_required']+'.csv')
                
                if os.path.exists(test_data_file_name):
                    miscellaneous_dict['test_data_file_present'] = 'yes'
                    miscellaneous_dict['test_data_file_name'] = test_data_file_name

                top10_dict = csv_reader(test_data_file_name)
                metadata_dict = {}

        write_json(miscellaneous_dict,'data/miscellaneous.json')
        write_json(metadata_dict,'data/metadata.json')    
        write_json(top10_dict,'data/top10data.json')

    return render_template("download.html", table_details_dict = read_json(), \
                           miscellaneous_dict = read_json('data/miscellaneous.json'), \
                            metadata_dict = read_json('data/metadata.json'), \
                             top10_dict = read_json('data/top10data.json'))


@app.route("/log", methods=["POST", "GET"])
def log():

    miscellaneous_dict = {}
    log_content = ''

    if path.isfile('data/miscellaneous.json'):
        miscellaneous_dict = read_json('data/miscellaneous.json')
    else:
        write_json(miscellaneous_dict,'data/miscellaneous.json')

    if os.path.exists(LOG_FOLDER) and len(os.listdir(LOG_FOLDER)) > 0:
        miscellaneous_dict['does_log_exist'] = True
        delete_old_files(LOG_FOLDER)
    else:
        miscellaneous_dict['does_log_exist'] = False

    write_json(miscellaneous_dict,'data/miscellaneous.json')

    log_file_dir = os.path.join(os.getcwd(), app.config['LOG_FOLDER'])
    files = [os.path.join(log_file_dir, os.path.basename(file)) for file in glob.glob(os.path.join(LOG_FOLDER, '*'))]
    latest_file = None
    latest_time = 0
    
    # Iterate through files in the folder
    if os.path.exists(LOG_FOLDER) and len(os.listdir(LOG_FOLDER)) > 0:
        for file_name in os.listdir(LOG_FOLDER):
            file_path = os.path.join(LOG_FOLDER, file_name)
            if os.path.isfile(file_path):  # Check if it's a file
                file_time = os.path.getmtime(file_path)
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path
    
        if latest_file is not None:
            with open(latest_file, 'r') as file:
                log_content = file.read()

        if request.method == "POST":
            if request.form.get('deleteLog') == 'Delete All Logs':
                remove_log_folder()
                return redirect(url_for('form'))
    
    return render_template("log.html", files=files, log_content=log_content, latest_file=latest_file, miscellaneous_dict = read_json('data/miscellaneous.json'))


@app.route('/download_file', methods=['GET'])
def download_file():
    miscellaneous_dict = read_json('data/miscellaneous.json')
    file_path = miscellaneous_dict['test_data_file_name']

    # Send the file as an attachment for download
    return send_file(file_path, as_attachment=True)

@app.route('/download_template', methods=['GET'])
def download_template():
    macro_dir = os.path.join(os.getcwd(), 'macro')
    macro_file_path = os.path.join(macro_dir, 'Metadata_CSV_Creator.xlsm')

    # Send the file as an attachment for download
    return send_file(macro_file_path, as_attachment=True)


@app.route('/download/<filename>')
def download_logfile(filename):
    file_path = f'{filename}'
    print(file_path)
    return send_file(file_path, as_attachment=True)

@app.route("/usermanual", methods=["POST", "GET"])
def usermanual():

    create_folders()
    miscellaneous_dict = {}
    user_instructions_image_dict = {}

    if path.isfile('data/miscellaneous.json'):
        miscellaneous_dict = read_json('data/miscellaneous.json')
    else:
        write_json(miscellaneous_dict,'data/miscellaneous.json')

    if path.isfile('data/user_instructions_image.json'):
        user_instructions_image_dict = read_json('data/user_instructions_image.json')
    else:
        write_json(user_instructions_image_dict,'data/user_instructions_image.json')

    if os.path.exists(LOG_FOLDER) and len(os.listdir(LOG_FOLDER)) > 0:
        miscellaneous_dict['does_log_exist'] = True
        delete_old_files(LOG_FOLDER)
    else:
        miscellaneous_dict['does_log_exist'] = False

    section_1_image_1 = url_for('static', filename='screenshots/section_1_image_1.png')
    section_1_image_2 = url_for('static', filename='screenshots/section_1_image_2.png')
    section_1_image_3 = url_for('static', filename='screenshots/section_1_image_3.png')
    section_1_image_4 = url_for('static', filename='screenshots/section_1_image_4.png')
    section_1_image_5 = url_for('static', filename='screenshots/section_1_image_5.png')
    section_1_image_6 = url_for('static', filename='screenshots/section_1_image_6.png')
    section_1_image_7 = url_for('static', filename='screenshots/section_1_image_7.png')
    section_1_image_8 = url_for('static', filename='screenshots/section_1_image_8.png')
    section_2_image_1 = url_for('static', filename='screenshots/section_2_image_1.png')
    section_2_image_2 = url_for('static', filename='screenshots/section_2_image_2.png')
    section_2_image_3 = url_for('static', filename='screenshots/section_2_image_3.png')
    section_2_image_4 = url_for('static', filename='screenshots/section_2_image_4.png')
    section_2_image_5 = url_for('static', filename='screenshots/section_2_image_5.png')
    section_2_image_6 = url_for('static', filename='screenshots/section_2_image_6.png')
    section_2_image_7 = url_for('static', filename='screenshots/section_2_image_7.png')
    section_2_image_8 = url_for('static', filename='screenshots/section_2_image_8.png')
    section_2_image_9 = url_for('static', filename='screenshots/section_2_image_9.png')
    section_2_image_10 = url_for('static', filename='screenshots/section_2_image_10.png')
    section_2_image_11 = url_for('static', filename='screenshots/section_2_image_11.png')
    section_3_image_1 = url_for('static', filename='screenshots/section_3_image_1.png')
    section_3_image_2 = url_for('static', filename='screenshots/section_3_image_2.png')
    section_3_image_3 = url_for('static', filename='screenshots/section_3_image_3.png')
    section_3_image_4 = url_for('static', filename='screenshots/section_3_image_4.png')
    section_4_image_1 = url_for('static', filename='screenshots/section_4_image_1.png')
    section_4_image_2 = url_for('static', filename='screenshots/section_4_image_2.png')

    user_instructions_image_dict['section_1_image_1'] = section_1_image_1
    user_instructions_image_dict['section_1_image_2'] = section_1_image_2
    user_instructions_image_dict['section_1_image_3'] = section_1_image_3
    user_instructions_image_dict['section_1_image_4'] = section_1_image_4
    user_instructions_image_dict['section_1_image_5'] = section_1_image_5
    user_instructions_image_dict['section_1_image_6'] = section_1_image_6
    user_instructions_image_dict['section_1_image_7'] = section_1_image_7
    user_instructions_image_dict['section_1_image_8'] = section_1_image_8
    user_instructions_image_dict['section_2_image_1'] = section_2_image_1
    user_instructions_image_dict['section_2_image_2'] = section_2_image_2
    user_instructions_image_dict['section_2_image_3'] = section_2_image_3
    user_instructions_image_dict['section_2_image_4'] = section_2_image_4
    user_instructions_image_dict['section_2_image_5'] = section_2_image_5
    user_instructions_image_dict['section_2_image_6'] = section_2_image_6
    user_instructions_image_dict['section_2_image_7'] = section_2_image_7
    user_instructions_image_dict['section_2_image_8'] = section_2_image_8
    user_instructions_image_dict['section_2_image_9'] = section_2_image_9
    user_instructions_image_dict['section_2_image_10'] = section_2_image_10
    user_instructions_image_dict['section_2_image_11'] = section_2_image_11
    user_instructions_image_dict['section_3_image_1'] = section_3_image_1
    user_instructions_image_dict['section_3_image_2'] = section_3_image_2
    user_instructions_image_dict['section_3_image_3'] = section_3_image_3
    user_instructions_image_dict['section_3_image_4'] = section_3_image_4
    user_instructions_image_dict['section_4_image_1'] = section_4_image_1
    user_instructions_image_dict['section_4_image_2'] = section_4_image_2

    write_json(miscellaneous_dict,'data/miscellaneous.json')
    write_json(user_instructions_image_dict,'data/user_instructions_image.json')
    
    return render_template("usermanual.html", miscellaneous_dict = read_json('data/miscellaneous.json'), \
                           user_instructions_image_dict = read_json('data/user_instructions_image.json'))

#### This setion is to find the min value between two numbers given in templates, for Jinja2 to use ####
@app.template_filter('min_value')
def min_value(value, default_min):
    return min(value, default_min)

app.jinja_env.filters['min_value'] = min_value

########## Section ends here ################ 

def read_column_from_csv(filename):
   """This function returns list of column names from a metadata file given as input"""
   metadata_df = pd.read_csv(filename)
   column_name = metadata_df[metadata_df.columns[0]].to_numpy()
   column_name_list = column_name.tolist()

   return column_name_list

def read_json(filename='data/table_column_combo.json'):
    """This function reads json file and returns the content"""
    if path.isfile(filename) is True:
        with open(filename,'r') as file:
            file_data = json.load(file)

        return file_data
    else:
        return None

def write_json(new_data, filename='data/table_column_combo.json'):
    """This function helps write json file in overwrite mode"""
    with open(filename, "w") as outfile:
        json.dump(new_data, outfile, indent=5)

def append_json(new_data, filename='data/table_column_combo.json'):
    """This function helps write json file in append mode"""
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["table_metadata"].append(new_data)

        file.seek(0)
        json.dump(file_data, file, indent = 5)

def delete_row(serial_number):
    """"""
    file_data = read_json('data/key_combo.json')
    del file_data["key_combo"][serial_number - 1]

    write_json(serial_adjustment(file_data), 'data/key_combo.json')

def serial_adjustment(file_data):
    """This àssigns/rearranges the serial no"""
    i = 0
    for item in file_data["key_combo"]:
        i += 1
        item["Serial_No"] = i
    
    return file_data

def csv_reader(csv_file):
    data = []
    with open(csv_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            data = list(csv_reader)
    
    return data

def delete_old_files(folder_path, num_to_keep = 10):
    # Get a list of files in the folder with their modification time
    files_with_time = [(os.path.join(folder_path, file), os.path.getmtime(os.path.join(folder_path, file))) 
                       for file in os.listdir(folder_path)]
    
    # Sort files based on modification time (oldest to newest)
    sorted_files = sorted(files_with_time, key=lambda x: x[1])
    
    # Keep the latest n files using heapq's nlargest function
    latest_files = heapq.nlargest(num_to_keep, sorted_files, key=lambda x: x[1])
    
    # Delete the files that are not in the latest_files list
    for file_path, _ in files_with_time:
        if (file_path, os.path.getmtime(file_path)) not in latest_files:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
 
if __name__=='__main__':
 app.run()