import re
from object_detection.utils import config_util
import tensorflow as tf
from functools import reduce

def isfloat(value):
    """Returns if a given value can be converted to a float or not.

    Args:
      value: Input value of each type

    Returns:
      bool: Boolean if the input value can be parsed to a float"""

    try:
        float(value)
        return True
    except:
        return False

def config_to_dict(pipeline_config_path):
    """Convert pipeline_config_file from object_detection training to a better accessible dictionary.

    Args:
      pipeline_config_path: Path to pipeline_config_file (.config)

    Returns:
      config_dict: Dictionary for the pipeline_config_file to access with subscripts like config_dict['train_config']"""

    f = open(pipeline_config_path, "r")
    config_str = f.read()

    # Make some preprocessing to access and convert easier
    all_elems = config_str.split('\n')

    # delete all characters which are after # and in the same line (the comments are deleted)
    all_elems_no_comments = [elem if '#' not in elem else elem[:elem.index('#')] for elem in all_elems]

    # separate the elements by blanks
    all_elems_no_blanks = re.split('\s|\t', str(reduce(lambda x, y: x+' '+y, all_elems_no_comments, '')))

    # add the start and end {} for the whole dict
    all_real_elems = ['{']
    all_real_elems.extend(list(filter(lambda x: x != '' and x != '\n', all_elems_no_blanks)))
    all_real_elems.append('}')

    # Information if you got a key, to know, that you need a comma after the next value
    # to separate it from other key-value pairs
    start_attr = False

    # Information if you have just a key-value pair or a key-subdict pair, so you don't
    # need a , after the next elem (it will be a {)
    start_subdict = False
    depth = 0

    # Save the last attribute and the position in the string
    # to convert two or more same arguments into a list (otherwise not correctly parsed to dict)
    last_attr = dict()
    opened_list = dict()
    dict_str = ''

    # Each key and each values is saved in one listelement
    # There are a lot more elements filled with '', '{' or '}'
    for elem in all_real_elems:
        # ignore the elems without keys/values or which are quoted
        if '"' in elem or elem == '' or isfloat(elem):
            dict_str += elem
        elif '{' in elem:
            # going one step deeper
            depth += 1
            start_subdict = False
            start_attr = False
            dict_str += elem
        elif '}' in elem:
            # going one step up, so it's not important any more which key was the last
            # at the previous depth. Otherwise the key can occur later in another context
            # and another parent attribute, but my code thinks, that these two attributes
            # must be saved together in a list, even if they are in completely different contexts
            if depth in last_attr: del last_attr[depth]
            if depth in opened_list:
                # maybe the list is opened, so it should be closed
                if opened_list[depth]:
                    dict_str += "],"
                    del opened_list[depth]
            depth -= 1
            dict_str += elem + ','

        # adjust false and true correctly to Python syntax
        elif elem == 'false':
            dict_str += 'False'
        elif elem == 'true':
            dict_str += 'True'

        # if there is a ':' in the element, this is a key
        # making start_attr = True so you know, that the next elem will be the value
        # and after the value you must add the delimiter ',' to get a correct dict

        # Some key arguments does not have a ':' inside, but the { is in the next elem
        elif elem[-1] == ':' or '{' in all_real_elems[all_real_elems.index(elem)+1]:
            if elem[-1] != ':':
                elem += ':'
                start_subdict = True

            # test if the key value occurs not the first time
            if depth in last_attr and last_attr[depth][0] == elem[:-1]:
                # if it the second time and the list is not started with [
                if depth not in opened_list or not opened_list[depth]:
                    # go back into the string and add some [, for signalizing the list started
                    rest_dict = dict_str[last_attr[depth][1]:]
                    rest_dict_key = rest_dict.split(':')[0]
                    rest_values = rest_dict[len(rest_dict_key)+1:]
                    dict_str = dict_str[:last_attr[depth][1]]
                    dict_str += '"' + elem[:-1] + '":[' + rest_values

                    # safe the information that you opened a list
                    opened_list[depth] = True
                else:
                    # otherwise the key occured a third time (or more often)
                    # so there is no need to add the key, only the value should be added to the list
                    pass
            else:
                # if a list is opened and you have no other attribute to add to this list
                if depth in opened_list and opened_list[depth]:
                    # just close the list
                    dict_str += "],"
                    opened_list[depth] = False
                last_attr[depth] = (elem[:-1], len(dict_str))
                dict_str += '"' + elem[:-1] + '":'
            start_attr = True
        else:
            dict_str += '"' + elem + '"'

        # adding the ',' if the key-value-pair is finished to set apart from other pairs
        if not start_subdict and start_attr and elem[-1] != ':':
            start_attr = False
            dict_str += ','

    # after getting the dict in a correct string format, just convert it to a dict
    config_dict = eval(dict_str)
    return config_dict[0]

def recursive_dict_to_str(sub_dict, depth=0):
    """Convert dictionary recursively to a string, so that it is pretty, when you write it to a file.

    Args:
      sub_dict: Sub dictionary which should be converted to a string
      depth: Depth of the actual dictionary in the initial dictionary

    Returns:
      dict_str: Dictionary string formatted for looking good in a config file"""

    # if there is no dict just return the value
    if type(sub_dict) != dict:
        return str(sub_dict)
    keys = list(sub_dict.keys())
    dict_str = ''
    for key in keys:
        # Starting the sub_dict with enough indent
        dict_str += ' '*2*depth

        # if there is no sub_dict in sub_dict[key], just add the key-value-pair pretty
        if isfloat(sub_dict[key]):
            dict_str += key + ': ' + str(sub_dict[key]) + '\n'
        elif type(sub_dict[key]) == str:
            dict_str += key + ': "' + sub_dict[key] + '"\n'

        # otherwise add recursively the pretty string from the sub_dict[key]-sub_dict
        else:
            dict_str += key + ' {\n'
            dict_str += recursive_dict_to_str(sub_dict[key], depth+1)
            dict_str += ' '*2*depth + '}\n'
    return dict_str

def dict_to_config(config_dict, new_pipeline_path):
    """Convert dictionary to a string and write the result readable (and pretty) to a pipeline_config_file.

    Args:
      config_dict: Dictionary which should be written to the config file
      new_pipeline_path: Path of the new pipeline_config_file where the dict will be written to

    Returns:
      dict_str: The string which is written to the pipeline_config_file"""

    dict_str = recursive_dict_to_str(config_dict)
    with tf.gfile.Open(new_pipeline_path, "wb") as f:
        f.write(dict_str)
    return dict_str
