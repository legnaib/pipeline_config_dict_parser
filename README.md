# pipeline_config_dict_parser
Script to convert a pipeline_config_file into a better accessible python dictionary.
The pipeline_config_file should be used for training an object_detection model. [Here](https://github.com/tensorflow/models/tree/master/research/object_detection/samples/configs) you can get all the pipeline configuration files and convert them to a dict with this parser.  
Other .config files can be converted too, if they have the correct syntax (for more detail see [below](https://github.com/legnaib/pipeline_config_dict_parser/blob/master/README.md#requirements) and you can find some examples [here](https://github.com/legnaib/pipeline_config_dict_parser/blob/master/README.md#pretty) or [here](https://github.com/legnaib/pipeline_config_dict_parser/blob/master/README.md#easy-part))

## Requirements
1. Your config_file must have at least one space (or new line) between arguments, values and brackets {, }
2. No space between key and :
3. After # only comments, nothing else (only in the same line)
4. If you have multiple keys with the same name in the same depth, they must occur exactly after each other. No other argument can be between (at this depth)
5. General syntax of config_file is correct

### Examples
#### Pretty
```
train_config {
  num_steps: 8000
  data_augmentation_options {
    # Flip horizontal with random value 50%
    random_horizontal_flip {
    }
  }
  data_augmentation_options { # Another option
    random_jitter_boxes {
    }
  }
}
```
#### Ok but allowed
```
train_config
{ num_steps:   8000 data_augmentation_options {
random_horizontal_flip {#Fliphorizontal with random value 50%
  }   }   # Another option
data_augmentation_options   {   random_jitter_boxes {
} }
}
```
#### Not allowed
```
train_config{
  data_augmentation_options {
    #Fliphorizontal with random value 50%random_horizontal_flip {
}}
    num_steps   :8000data_augmentation_options#Another option {
    random_jitter_boxes {
  }}}
```

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

## Explanations
### Easy part
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
```py
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
### Lists
It is much more complex to convert multiple keys with the same name, but different values (maybe the values are sub_dicts, too).
In the pipeline_config_file it looks like this:
```
train_config {
  num_steps: 8000
  data_augmentation_options {
    random_horizontal_flip {
    }
  }
  data_augmentation_options {
    ssd_random_crop {
    }
  }
  data_augmentation_options {
    random_jitter_boxes {
    }
  }
}
```
But if you convert this exactly like above, you will get three `data_augmentation_options`-keys and this is not allowed in a Python-dict. So Python will only take one value, but this is not what you want. It should look like this:
```py
{
  "train_config": {
    "num_steps": 8000,
    "data_augmentation_options": [
      {
        "random_horizontal_flip": {}
      },
      {
        "ssd_random_crop": {}
      },
      {
        "random_jitter_boxes": {}
      }
    ]
  }
}
```
Therefore I added a lot of variables and if-elif-else-clauses for handling these things:

* `start_subdict`: _bool_  
  signalize if the next elem will be a sub_dict (so { occurs ) or it will just be a value (int, float or str)
* `last_attr`: _dict of pairs_  
  for each depth, save the last attribute and its position in the whole string to compare with the current one and see if they're the same and a list must be created
* `opened_list`: _dict of bools_  
  for each depth, save if you have just opened a list, so don't forget to close it when you go up in depth
  
[comment]: <> (| name | type | usage |)
[comment]: <> (| --- | --- | --- |)
[comment]: <> (| `start_subdict` | bool | signalize if the next elem will be a sub_dict (so { occurs ] or it will just be a value (int, float or str] |)
[comment]: <> (| `last_attr` | dict of pairs | for each depth, save the last attribute and its position in the whole string to compare with the current one and see if they're the same and a list must be created |)
[comment]: <> (| `opened_list` | dict of bools | for each depth, save if you have just opened a list, so don't forget to close it when you go up in depth |)
