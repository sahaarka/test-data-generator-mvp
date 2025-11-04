import pandas as pd
import numpy as np
import string
import random
import os
from decimal import Decimal
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, InvalidOperation

class DataGenerator:
  def __init__(self, column_name, datatype, no_of_records, constraint):
    self.column_name = column_name
    self.datatype = datatype
    self.no_of_records = no_of_records
    self.constraint = constraint

  def extract_string_in_parentheses(self, text):
    start_index = text.find('(')
    end_index = text.find(')')
    if start_index != -1 and end_index != -1:
        return text[start_index + 1:end_index]
    else:
        return None

  def date_format_check(self, text):
    formats_to_check = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%d-%b-%Y', '%b-%d-%Y', '%Y-%b-%d', '%Y.%m.%d', '%d.%m.%Y', '%y-%m-%d', '%d-%m-%y', '%m-%d-%y', '%d-%b-%y', '%b-%d-%y', '%y-%b-%d']

    for date_format in formats_to_check:
        try:
            datetime.strptime(text, date_format)
            return date_format
        except ValueError:
            pass

    return None  # If no matching format is found

  def timestamp_format_check(self, text):
    formats_to_check = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M', '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S.%f', '%d-%m-%Y %H:%M', '%m-%d-%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S.%f', '%m-%d-%Y %H:%M', '%d-%b-%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S.%f', '%d-%b-%Y %H:%M', '%b-%d-%Y %H:%M:%S', '%b-%d-%Y %H:%M:%S.%f', '%b-%d-%Y %H:%M']

    for timestamp_format in formats_to_check:
        try:
            datetime.strptime(text, timestamp_format)
            return timestamp_format
        except ValueError:
            pass

    return None  # If no matching format is found

  def generate_random_datetime(self, start_date, end_date, date_format):

    start_timestamp = start_date.timestamp()
    end_timestamp = end_date.timestamp()
    random_timestamp = random.uniform(start_timestamp, end_timestamp)
    return datetime.fromtimestamp(random_timestamp).strftime(date_format)


  def get_data_type(self, value):

    date_formats_to_check = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%d-%b-%Y', '%b-%d-%Y', '%Y-%b-%d', '%Y.%m.%d', '%d.%m.%Y', '%y-%m-%d', '%d-%m-%y', '%m-%d-%y', '%d-%b-%y', '%b-%d-%y', '%y-%b-%d']
    timestamp_formats_to_check = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M', '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S.%f', '%d-%m-%Y %H:%M', '%m-%d-%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S.%f', '%m-%d-%Y %H:%M', '%d-%b-%Y %H:%M:%S', '%d-%b-%Y %H:%M:%S.%f', '%d-%b-%Y %H:%M', '%b-%d-%Y %H:%M:%S', '%b-%d-%Y %H:%M:%S.%f', '%b-%d-%Y %H:%M']

    for timestamp_format in timestamp_formats_to_check:
      try:
          # Try converting to timestamp
          timestamp_value = datetime.strptime(value, timestamp_format)
          return 'timestamp'
      except ValueError:
          pass

    for date_format in date_formats_to_check:
      try:
          # Try converting to date
          date_value = datetime.strptime(value, date_format)
          return 'date'
      except ValueError:
          pass

    try:
        # Try converting to integer
        int_value = int(value)
        return 'integer'
    except ValueError:
        pass

    try:
        # Try converting to decimal
        decimal_value = Decimal(value)
        return f'decimal({len(decimal_value.as_tuple().digits)}, {decimal_value.as_tuple().exponent * -1})'
    except InvalidOperation:
        pass

    return 'string'

  def generate_string(self, example_value, min_value, max_value, format):

    if format == '':
      format = 'others'

    string_value_type = format

    if not self.datatype.lower().startswith("string"):
      print("You are trying to generate string for a non-string column")
      raise ValueError

    if self.extract_string_in_parentheses(self.datatype):
      char_length = int(self.extract_string_in_parentheses(self.datatype))
    else:
      char_length = 20

    sample_data_list = []

    if example_value == '':
      if string_value_type == 'alpha':
        letters = string.ascii_lowercase
        for _ in range(self.no_of_records):
          sample_data = ''.join(random.choice(letters) for i in range(char_length))
          sample_data_list.append(sample_data)
      elif string_value_type == 'numeric':
        digits = string.digits
        for _ in range(self.no_of_records):
          sample_data = ''.join(random.choice(digits) for i in range(char_length))
          sample_data_list.append(sample_data)
      elif string_value_type == 'alphanumeric':
        alnum_chars = string.ascii_letters + string.digits
        for _ in range(self.no_of_records):
          sample_data = ''.join(random.choice(alnum_chars) for i in range(char_length))
          sample_data_list.append(sample_data)
      elif string_value_type == 'others':
        ascii_chars = string.printable
        for _ in range(self.no_of_records):
          sample_data = ''.join(random.choice(ascii_chars) for i in range(char_length))
          sample_data_list.append(sample_data)
      elif string_value_type == 'first_name':
         sample_data_list = [Faker().first_name() for _ in range(self.no_of_records)]
      elif string_value_type == 'last_name':
         sample_data_list = [Faker().last_name() for _ in range(self.no_of_records)]
      elif string_value_type == 'name':
         sample_data_list = [Faker().name() for _ in range(self.no_of_records)]
      elif string_value_type == 'email':
         sample_data_list = [Faker().email() for _ in range(self.no_of_records)]
      elif string_value_type == 'phone_number':
         sample_data_list = [Faker().phone_number() for _ in range(self.no_of_records)]
      elif string_value_type == 'street_address':
         sample_data_list = [Faker().street_address() for _ in range(self.no_of_records)]
      elif string_value_type == 'city':
         sample_data_list = [Faker().city() for _ in range(self.no_of_records)]
      elif string_value_type == 'postcode':
         sample_data_list = [Faker().postcode() for _ in range(self.no_of_records)]
      elif string_value_type == 'country':
         sample_data_list = [Faker().country() for _ in range(self.no_of_records)]
      elif string_value_type == 'state':
         sample_data_list = [Faker().state() for _ in range(self.no_of_records)]
      elif string_value_type == 'date(%Y-%m-%d)':
         sample_data_list = [Faker().date_time().strftime('%Y-%m-%d') for _ in range(self.no_of_records)]
      elif string_value_type == 'time(%H:%M:%s)':
         sample_data_list = [Faker().date_time().strftime('%H:%M:%s') for _ in range(self.no_of_records)]
      elif string_value_type == 'date_time(%Y-%m-%d %H:%M:%s)':
         sample_data_list = [Faker().date_time().strftime('%Y-%m-%d %H:%M:%s') for _ in range(self.no_of_records)]
      elif string_value_type == 'user_name':
         sample_data_list = [Faker().state() for _ in range(self.no_of_records)]
      elif string_value_type == 'url':
         sample_data_list = [Faker().url() for _ in range(self.no_of_records)]
      elif string_value_type == 'job':
         sample_data_list = [Faker().job() for _ in range(self.no_of_records)]
      elif string_value_type == 'credit_card_number':
         sample_data_list = [Faker().credit_card_number() for _ in range(self.no_of_records)]
      elif string_value_type == 'barcode':
         sample_data_list = [Faker().ean13() for _ in range(self.no_of_records)]
      elif string_value_type == 'vehicle_make':
         sample_data_list = [Faker().vehicle_make() for _ in range(self.no_of_records)]
      elif string_value_type == 'vehicle_model':
         sample_data_list = [Faker().vehicle_model() for _ in range(self.no_of_records)]
      elif string_value_type == 'currency_symbol':
         sample_data_list = [Faker().currency_symbol() for _ in range(self.no_of_records)]
      elif string_value_type == 'currency_code':
         sample_data_list = [Faker().currency_code() for _ in range(self.no_of_records)]
      elif string_value_type == 'currency_name':
         sample_data_list = [Faker().currency_name() for _ in range(self.no_of_records)]
      else:
        raise ValueError

    else:
      if example_value.find(';') != -1:
        example_values_list = example_value.split(';')
        if example_value.endswith(';'):
          example_values_list.pop()

        for _ in range(self.no_of_records):
          sample_data = random.choice(example_values_list)
          sample_data_list.append(sample_data)
      else:
        for _ in range(self.no_of_records):
          sample_data = ''
          for char in example_value:
              if char.isalpha():
                  sample_data += random.choice(string.ascii_letters)
              elif char.isdigit():
                  sample_data += random.choice(string.digits)
              else:
                  sample_data += char
          sample_data_list.append(sample_data)

    return sample_data_list

  def generate_integer(self, example_value, min_value, max_value):

    if min_value == '':
      min_value = 0
    if max_value == '':
      max_value = 999999999
    
    generated_integer = 0

    sample_data_list = []
    if example_value != '':
      if str(example_value).find(';') != -1:
        example_values_list = example_value.split(';')
        if example_value.endswith(';'):
          example_values_list.pop()

        for number in example_values_list:
          if not (isinstance(int(number), int)):
            print("Please pass a valid integer as example value(s)")
            raise ValueError
        for _ in range(self.no_of_records):
          sample_data = int(random.choice(example_values_list))
          sample_data_list.append(sample_data)
        return sample_data_list

      else:
        if not (isinstance(int(example_value), int)):
            print("Please pass a valid integer as example value(s)")
            raise ValueError
        length = len(str(example_value))
        min_value = (10 ** (int(length) - 1))
        max_value = (10 ** int(length)) - 1

    if (not (isinstance(int(max_value), int))) and (not (isinstance(int(min_value), int))):
      print("Please pass a valid integer as minimum and maximum values")
      raise ValueError
    else:
      if int(max_value) < int(min_value):
        print("Please pass a max value which is greater than the min value")
        raise ValueError
      else:
        if self.constraint == 'primary key':
          for i in range(self.no_of_records):
            generated_integer = random.randint(int(min_value), int(max_value))
            if not generated_integer in sample_data_list:
              sample_data_list.append(generated_integer)
            else:
              # trying to check if the value is already generated, if so, it will try 100 times to regenerate the number
              for chance in range(100):
                generated_integer = random.randint(int(min_value), int(max_value))
                if not generated_integer in sample_data_list:
                  sample_data_list.append(generated_integer)
                  break
                if chance == 99:
                   sample_data_list.append(generated_integer)
        else:
          sample_data_list = [random.randint(int(min_value), int(max_value)) for _ in range(self.no_of_records)]
        return sample_data_list

  def generate_decimal(self, example_value, min_value, max_value):

    if min_value == '':
      min_value = 0
    if max_value == '':
      max_value = 99999999.9999

    generated_decimal = 0.00

    if self.extract_string_in_parentheses(self.datatype):
      precision_str_list = self.extract_string_in_parentheses(self.datatype).replace(',',';').split(';')
      precision_list = [int(x) for x in precision_str_list]
      precision = tuple(precision_list)
    else:
      precision = (5,2)

    sample_data_list = []
    if example_value != '':
      if str(example_value).find(';') != -1:
        example_values_list = example_value.split(';')
        if example_value.endswith(';'):
          example_values_list.pop()

        for number in example_values_list:
          if not (isinstance(float(number), float)):
            print("Please pass a valid decimal as example value(s)")
            raise ValueError
        for _ in range(self.no_of_records):
          sample_data = float(random.choice(example_values_list))
          sample_data_list.append(sample_data)
        return sample_data_list

      else:
        precision_list = []
        if not (isinstance(float(example_value), float)):
            print("Please pass a valid decimal as example value(s)")
            raise ValueError
        m = len(str(example_value)) - 1
        n = len(str(example_value)[str(example_value).find('.'):len(str(example_value))]) - 1
        precision_list.append(m)
        precision_list.append(n)
        precision = tuple(precision_list)

        max_integer_part = (10 ** (m - n)) - 1
        max_decimal_part = (10 ** n) - 1
        max_value = float(str(max_integer_part) + '.' + str(max_decimal_part))

        min_integer_part = (10 ** (m - n - 1))
        min_decimal_part = '0'*(n)
        min_value = float(str(min_integer_part) + '.' + str(min_decimal_part))

    if (not (isinstance(float(max_value), float))) and (not (isinstance(float(min_value), float))):
      print("Please pass a valid decimal as minimum and maximum values")
      raise ValueError
    else:
      if float(max_value) < float(min_value):
        print("Please pass a max value which is greater than the min value")
        raise ValueError
      else:
        if self.constraint == 'primary key':
          for i in range(self.no_of_records):
            value = random.uniform(float(min_value), float(max_value))
            value = round(value, precision[1])
            generated_decimal = value
            if not generated_decimal in sample_data_list:
              sample_data_list.append(generated_decimal)
            else:
              # trying to check if the value is already generated, if so, it will try 100 times to regenerate the number
              for chance in range(100):
                value = random.uniform(float(min_value), float(max_value))
                value = round(value, precision[1])
                generated_decimal = value
                if not generated_decimal in sample_data_list:
                  sample_data_list.append(generated_decimal)
                  break
                if chance == 99:
                   sample_data_list.append(generated_decimal)
        else:
          for _ in range(self.no_of_records):
            value = random.uniform(float(min_value), float(max_value))
            value = round(value, precision[1])
            sample_data_list.append(value)
        return sample_data_list

  def generate_date(self, example_value, min_value, max_value, format):

    default_date_format = '%Y-%m-%d'
    derived_date_format = ''
    derived_min_date_format = ''
    derived_max_date_format = ''
    date_format = ''

    sample_data_list = []
    if example_value != '':
      if str(example_value).find(';') != -1:
        example_values_list = example_value.split(';')
        if example_value.endswith(';'):
          example_values_list.pop()

        for _ in range(self.no_of_records):
          try:
            sample_data = random.choice(example_values_list)
            sample_data_list.append(sample_data)
          except ValueError:
            print("the given value is not a date value")
        return sample_data_list
      else:
        derived_date_format = self.date_format_check(example_value)
        if not derived_date_format:
          print("the given example value is not an accepted date format")
          raise TypeError

    if min_value != '':
      derived_min_date_format = self.date_format_check(min_value)
      if not derived_min_date_format:
        print("the given min_value is not an accepted date format")
        raise TypeError
      min_value = datetime.strptime(min_value, derived_min_date_format)
    else:
      min_value = datetime.now() - relativedelta(years=3)

    if max_value != '':
      derived_max_date_format = self.date_format_check(max_value)
      if not derived_max_date_format:
        print("the given max_value is not an accepted date format")
        raise TypeError
      max_value = datetime.strptime(max_value, derived_max_date_format)
    else:
      max_value = datetime.now()

    if not (derived_min_date_format == derived_max_date_format):
      print("Min, Max date formats are not in sync")
      raise ValueError

    if derived_date_format != '' and derived_min_date_format != '' and derived_max_date_format != '':
      if derived_min_date_format == derived_date_format == derived_max_date_format:
        date_format = derived_date_format
      else:
        print("Min, Max and Example Value date formats are not in sync")
        raise ValueError
    elif (derived_date_format != '' or derived_date_format):
      date_format = derived_date_format
    elif derived_min_date_format != '' and derived_max_date_format != '':
      date_format = derived_min_date_format
    elif format != '':
      date_format = format
    else:
      date_format = default_date_format

    if min_value > max_value:
      print("Please pass a max value which is greater than the min value")
      raise ValueError
    else:
      counter = 0
      print(f'for loop is starting at {datetime.now()}')
      for _ in range(self.no_of_records):
        counter += 1
        print(f'{counter} record(s) generated')
        if min_value >= datetime.strptime('1971-01-01', default_date_format):
          random_date = self.generate_random_datetime(min_value, max_value, date_format)
        else:
          random_date = Faker().date_time_between(start_date=min_value, end_date=max_value).strftime(date_format)
        
        sample_data_list.append(random_date)
      print(f'for loop is ending at {datetime.now()}')

    return sample_data_list

  def generate_datetime(self, example_value, min_value, max_value, format):

    default_datetime_format = '%Y-%m-%d %H:%M:%S'
    derived_datetime_format = ''
    derived_min_datetime_format = ''
    derived_max_datetime_format = ''
    datetime_format = ''

    sample_data_list = []
    if example_value != '':
      if str(example_value).find(';') != -1:
        example_values_list = example_value.split(';')
        if example_value.endswith(';'):
          example_values_list.pop()
          
        for _ in range(self.no_of_records):
          try:
            sample_data = random.choice(example_values_list)
            sample_data_list.append(sample_data)
          except ValueError:
            print("the given value is not a datetime value")
        return sample_data_list
      else:
        derived_datetime_format = self.timestamp_format_check(example_value)
        if not derived_datetime_format:
          print("the given example value is not an accepted datetime format")
          raise TypeError

    if min_value != '':
      derived_min_datetime_format = self.timestamp_format_check(min_value)
      if not derived_min_datetime_format:
        print("the given min_value is not an accepted datetime format")
        raise TypeError
      min_value = datetime.strptime(min_value, derived_min_datetime_format)
    else:
      min_value = datetime.now() - relativedelta(years=3)

    if max_value != '':
      derived_max_datetime_format = self.timestamp_format_check(max_value)
      if not derived_max_datetime_format:
        print("the given max_value is not an accepted datetime format")
        raise TypeError
      max_value = datetime.strptime(max_value, derived_max_datetime_format)
    else:
      max_value = datetime.now()

    if not (derived_min_datetime_format == derived_max_datetime_format):
      print("Min, Max datetime formats are not in sync")
      raise ValueError

    if derived_datetime_format != '' and derived_min_datetime_format != '' and derived_max_datetime_format != '':
      if derived_min_datetime_format == derived_datetime_format == derived_max_datetime_format:
        datetime_format = derived_datetime_format
      else:
        print("Min, Max and Example Value datetime formats are not in sync")
        raise ValueError
    elif (derived_datetime_format != '' or derived_datetime_format):
      datetime_format = derived_datetime_format
    elif derived_min_datetime_format != '' and derived_max_datetime_format != '':
      datetime_format = derived_min_datetime_format
    elif format != '':
      datetime_format = format
    else:
      datetime_format = default_datetime_format

    if min_value > max_value:
      print("Please pass a max value which is greater than the min value")
      raise ValueError
    else:
      counter = 0
      print(f'for loop is starting at {datetime.now()}')
      for _ in range(self.no_of_records):
        counter += 1
        print(f'{counter} record(s) generated')
        if min_value >= datetime.strptime('1971-01-01 00:00:00', default_datetime_format):
          random_date = self.generate_random_datetime(min_value, max_value, datetime_format)
        else:
          random_date = Faker().date_time_between(start_date=min_value, end_date=max_value).strftime(datetime_format)
        sample_data_list.append(random_date)
      print(f'for loop is ending at {datetime.now()}')

    return sample_data_list


def generate_test_data(metatdata_file, test_data_file, table_details_file, number_of_records):
    df = pd.read_csv(metatdata_file,on_bad_lines='skip')

    test_data = {}
    df_modified = df.fillna('')
    columns = []
    print(df_modified)

    try:
        number_of_records = int(number_of_records)
    except Exception as ex:
        print("please provide a valid integer value. " + str(ex))
        exit(1)

    for index, row in df_modified.iterrows():
        column_dict = {}

        column_name = row['column_name']
        datatype = row['datatype']
        example_value = row['example_value']
        min_value = row['min_value']
        max_value = row['max_value']
        format = row['format']
        constraint = row['constraint']

        dg = DataGenerator(column_name, datatype, number_of_records, constraint)

        if datatype == '':
            datatype = dg.get_data_type(example_value)
            dg.datatype = datatype

        print(f'{column_name}, datatype = {datatype}')
        column_dict['column_name'] = column_name
        column_dict['datatype'] = datatype
        column_dict['example_value'] = example_value
        column_dict['constraint'] = constraint

        columns.append(column_dict)
        datatype_df = pd.DataFrame(columns)
        datatype_df.to_csv(table_details_file, index=False)

        if 'string' in datatype.lower():
            test_data[column_name] = dg.generate_string(example_value, min_value, max_value, format)

        if 'int' in datatype.lower():
            test_data[column_name] = dg.generate_integer(example_value, min_value, max_value)

        if 'decimal' in datatype.lower():
            test_data[column_name] = dg.generate_decimal(example_value, min_value, max_value)

        if 'date' in datatype.lower():
            test_data[column_name] = dg.generate_date(example_value, min_value, max_value, format)

        if 'timestamp' in datatype.lower():
            test_data[column_name] = dg.generate_datetime(example_value, min_value, max_value, format)

    test_df = pd.DataFrame(test_data)

    # Get the column names where the constraint is "null"
    columns_with_null_constraint = [col for col, constraint in zip(df_modified['column_name'], df_modified['constraint']) if constraint.lower() == '']
    print("Columns with 'null' constraint:", columns_with_null_constraint)

    for column_name in columns_with_null_constraint:
        # Generate random indices to insert NULL values
        num_null_values = random.randint(1, int(number_of_records * 25 / 100)) # Number of NULL values to insert 
        indices_to_nullify = np.random.choice(test_df.index, num_null_values, replace=False)

        # Set NULL values in the corresponding columns
        test_df.loc[indices_to_nullify, column_name] = np.nan

    print(test_df)
    test_df.to_csv(test_data_file, index = False)


def inject_data(primary_data_file, primary_key_column, secondary_data_file, foreign_key_column, log_file_name = '', percent = 75):
  '''This function helps inject data from primary key to foreign key'''
  primary_df = pd.read_csv(primary_data_file,on_bad_lines='skip')
  foreign_df = pd.read_csv(secondary_data_file,on_bad_lines='skip')

  primary_key_values = primary_df[primary_key_column]
  foreign_key_values = foreign_df[foreign_key_column]
   
  total_records_in_secondary_table = len(foreign_key_values)
  primary_key_unique_values = list(set(primary_key_values))
   
  for i in range(int(total_records_in_secondary_table*percent/100)):
    primary_random_index = random.randint(0, (len(primary_key_unique_values) - 1))
    foreign_random_index = random.randint(0, (len(foreign_key_values) - 1))

    foreign_df[foreign_key_column][foreign_random_index] = primary_key_unique_values[primary_random_index]
    log_message = (f"{primary_key_unique_values[primary_random_index]} from {primary_data_file.replace('.csv','').replace('test_data/','')}.{primary_key_column} is overwritten at index {foreign_random_index} of {secondary_data_file.replace('.csv','').replace('test_data/','')}.{foreign_key_column}")
    
    if log_file_name:

      # Check if the file exists
      if not os.path.exists(log_file_name):
          # Create the file if it doesn't exist
          with open(log_file_name, 'w') as f:
              pass  # Do nothing, as we just want to create the file

      # Open the file in append mode ('a' mode) to append new logs
      with open(log_file_name, 'a') as f:
          # Redirect print output to the log file
          print(log_message, file=f)
      
  foreign_df.to_csv(secondary_data_file, index=False)