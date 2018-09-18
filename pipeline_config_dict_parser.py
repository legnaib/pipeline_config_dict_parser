import re
from object_detection.utils import config_util

def isfloat(value):
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

    # Create an object_detection.proto.pipeline_pb2.TrainEvalPipelineConfig object
    pipeline_config = config_util.get_configs_from_pipeline_file(pipeline_config_path)
    config = config_util.create_pipeline_proto_from_configs(pipeline_config)

    # Make some preprocessing to access and convert easier
    config_str = str(config)
    config_str_better = config_str.replace('{', ':{')
    all_elems = re.split('\s|\n', config_str_better)
    all_real_elems = list(filter(lambda x: x != '' and x != '\n', all_elems))
    start_attr = False
    dict_str = '{'

    # Each key and each values is saved in one listelement
    # There are a lot more elements filled with '', '{' or '}'
    for elem in all_real_elems:
        # ignore the elems without keys/values or which are quoted
        if '"' in elem or '{' in elem or \
            elem == '' or \
            isfloat(elem):
            dict_str += elem
        elif '}' in elem:
            dict_str += elem + ','

        # adjust false and true correctly to Python syntax
        elif elem == 'false':
            dict_str += 'False'
        elif elem == 'true':
            dict_str += 'True'

        # if there is a ':' in the element, this is a key
        # making start_attr = True so you know, that the next elem will be the value
        # and after the value you must add the delimiter ',' to get a correct dict
        elif elem[-1] == ':':
            start_attr = True
            dict_str += '"' + elem[:-1] + '":'
        else:
            dict_str += '"' + elem + '"'

        # adding the ',' if the key-value-pair is finished to set apart from other pairs
        if start_attr and elem[-1] != ':':
            start_attr = False
            dict_str += ','
    dict_str += '}'

    # after getting the dict in a correct string format, just convert it to a dict
    config_dict = eval(dict_str)
    return config_dict

def recursive_dict_to_str(sub_dict, depth=0):
    if type(sub_dict) != dict:
        return str(sub_dict)
    keys = list(sub_dict.keys())
    dict_str = ' '*2*depth
    for key in keys:
        if isfloat(sub_dict[key]):
            dict_str += key + ': ' + str(sub_dict[key]) + '\n'
        elif type(sub_dict[key]) == str:
            dict_str += key + ': "' + sub_dict[key] + '"\n'
        else:
            dict_str += key + ' {\n'
            dict_str += recursive_dict_to_str(sub_dict[key], depth+1)
            dict_str += '}\n'
    return dict_str

def dict_to_config(config_dict, new_pipeline_path):
    dict_str = recursive_dict_to_str(config_dict)
    with tf.gfile.Open(new_pipeline_path, "wb") as f:
        f.write(dict_str)
    #config_start_str = str(config_dict)[1:-1]
