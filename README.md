# pipeline_config_dict_parser
Script to convert a pipeline_config_file into a better accessible python dictionary.
The pipeline_config_file should be used for training an object_detection model. [Here](https://github.com/tensorflow/models/tree/master/research/object_detection/samples/configs) you can get all the pipeline configuration files and convert them to a dict with this parser.

## Usage
Add this code in your python files and you can work with the created dictionary `config_dict`

```py
from config_dict_parser import config_to_dict
config_dict = config_to_dict(PATH_TO_PIPELINE_CONFIG_FILE)
```
