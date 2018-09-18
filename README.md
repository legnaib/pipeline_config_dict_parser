# pipeline_config_dict_parser
Script to convert a pipeline_config_file into a better accessible python dictionary.
The pipeline_config_file should be used for training an object_detection model. [Here](https://github.com/tensorflow/models/tree/master/research/object_detection/samples/configs) you can get all the pipeline configuration files and convert them to a dict with this parser.

## Usage
### Convert config_file to dictionary
Add this code in your python files and you can work with the created dictionary `config_dict`

```py
from pipeline_config_dict_parser import config_to_dict
config_dict = config_to_dict(PATH_TO_PIPELINE_CONFIG_FILE)
```

### Save dictionary into config file
Add this code in your python files if you want to save a changed dictionary `config_dict` into a pipeline_config_file, which is readable like the other pipeline_config_files

```py
from pipeline_config_dict_parser import dict_to_config
config_str = dict_to_config(config_dict, PATH_TO_NEW_PIPELINE_CONFIG_FILE)
```

Excerpt from the new_pipeline_config_file:

```
model {
  faster_rcnn {
    num_classes: 2
    image_resizer {
      keep_aspect_ratio_resizer {
        min_dimension: 600
        max_dimension: 1024
      }
    }
  ...
  }
}
```

## Explanations
The pipeline_config_file looks like this:
```
model {
  faster_rcnn {
    num_classes: 2
    image_resizer {
      keep_aspect_ratio_resizer {
        min_dimension: 600
        max_dimension: 1024
      }
    }
  }
}
```
But Python doesn't accept this syntax for a dictionary. It must look like this:
```
{
  "model": {
    "faster_rcnn": {
      "num_classes": 2,
      "image_resizer": {
        "keep_aspect_ratio_resizer": {
          "min_dimension": 600,
          "max_dimension": 1024
        }
      }
    }
  }
}
```
With my code, I add the missing " and : and ,

For converting in the other direction the " and : and , must be removed at specific places.
