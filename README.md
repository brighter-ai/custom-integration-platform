# Custom integration platform


<p align="center">
  <img src="docs/logo.png" />
</p>

Custom integration platform is a solution that helps to build a Redact anonymizing application in a fast manner using easy-to-read config files.

Custom integration platform enables the creation of data converter applications that can be easily customized for each use case and any input data format (including raw data). Applications are built by constructing a pipeline, and each element of the pipeline is an object that performs actions on data such as:

- data preprocessing (reading, encoding, etc)
- full anonymization cycle (using Brighter AI's Redact API)
- packing anonymized data into the desired format etc

## Get started

### Cloning

Please be aware that a git lfs install is required for cloning with all dependencies.

### Building and running

Custom integration platform works in the docker environment, in order to build the container locally use [`build.sh`](deployment/build.sh)
```shell
bash build.sh -t production
```
or run the following command
```shell
docker build --target production --progress plain -f ./deployment/Dockerfile -t custom_integration_platform .
```
for production build.

Then replace the Redact URL in the pipeline definition file ([here](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml#L6) and [here](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml#L33)) with an already working Redact's URL , e.g.

```yaml
redact_url: http://192.168.0.1:1234/
```
A [sample video](example/mp4_data_converter/tests/assets/original_video/test_video.mp4) could be used for anonymization tests and the [example integration pipeline](example) for a reference.
To launch the example you need to build a test image using the following command:
```shell
bash build.sh -t testing
```
or
```shell
docker build --target testing --progress plain -f ./deployment/Dockerfile -t custom_integration_platform .
```
and running:

```shell
docker run \
-v <INPUT_DIRECTORY>:/root/custom_integration_platform/data/input/ \
-v <OUTPUT_DIRECTORY>:/root/custom_integration_platform/data/output/ \
-v <LOGS_DIRECTORY>:/root/custom_integration_platform/logs/ \
custom_integration_platform:<TAG> \
python3.10 src/main.py
```

where ```INPUT_DIRECTORY```, ```OUTPUT_DIRECTORY```, ```LOGS_DIRECTORY``` need to be replaced with host system directories' absolute paths. To modify the pipeline or to create a custom one please refer to our [developer guide](#developer-guide). The ```TAG``` is the version from the [build.info](deployment/build.info) file.
## General dataflow

### Orchestrator
The main core component of custom integration platform is [Orchestrator](src/orchestrator/orchestrator.py) - a high-level "pipeline builder and executor", which helps to abstract all element-specific operations. It initializes elements by passing settings from pipeline definition file, and runs each element according to its input and/or output directories (which are also specified in pipeline definition file).

<p align="center">
  <img src="docs/custom_integration_platform-overview.png" />
</p>

### Pipeline elements
The building blocks in a pipeline are elements. Each element has a mandatory parameter - input, and each data processing element has the output. Every pipeline element represents a certain operation with clearly defined logic, as well as inputs and/or outputs, and has no dependencies on other pipeline elements. For flexibility many elements have configurable settings. For example, the Redact element can be specified like:

```yaml
name: "Redactor"
    settings:
      redact_url: http://redact:8787

    inputs:
      tar_files_directory: ./data/tar_files

    outputs:
      anonymized_tar_files_directory: ./data/anonymized_tar_files
```


### Pipeline definition file
To build a pipeline, a set of elements needs to be specified in yaml-format in [pipeline definition file](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml). Modularity and independence of the pipeline elements allow to easily optimize the current solution to any other case, as well as create new elements without difficulties. 


## Developer guide

There's nothing like seeing the work in practice, so we created an [example solution](example) that shows best practices for using and configuring a custom integration platform. 

### Overview

In order to create a custom solution, let's take a look at the internal logic of the application. For better understading please refer to [main function](src/main.py).

1. User can specify elements which need to be used in the pipeline using [pipeline definition file](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml).
2. Orchestrator [calls](src/main.py#L22) a YAML-Parser, which processes the pipeline definition file, and outputs the pipeline structure. 
3. Orchestrator [searchs](src/main.py#L24) for the specified aforementioned elements at the specified path
4. Orchestrator [initializes](src/main.py#L29) them with some settings (which are also specified in the pipeline definition file) and [starts](src/main.py#L31) running the pipeline sequentially

As we can see, the main part of Custom integration platform is the orchestrator, but there is no need to edit it to create a custom solution. On the contrary, we created a [main function](src/main.py) (here we can specify the modules and pipeline definition file paths) and a [pipeline definition file](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml) itself.

### Custom element creation

Every pipeline element should represent a certain operation with clearly defined logic, as well as inputs and/or outputs, and has no dependencies on other pipeline elements. Besides, each element must be formed as a python class and must necessarily have the main method `run` and the method `cleanup`. As example let's take a look at [Data Writer](example/mp4_data_converter/integration_pipeline/data_writer.py) element. If inside the pipeline there are needed some reverse operations several times (in this example - the use of `FFMpeg`), there could be created a helper class (in this case, `FFMPEGExecutor` with method `create_video`). Also every pipeline element can contain some other private function, as well as user-defined settings like here `file_name_format`.
```python
class DataWriter(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings) 

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        input_directory = Path(inputs["some_defined_input"])
        output_directory = Path(outputs["some_defined_output"])
        ffmpeg_executor = FFMPEGExecutor(file_name_format=self._settings["some_defined_setting"]) # a class which calls FFMPEG
        try:
            ffmpeg_executor.create_video(
                frames_directory=input_directory,
                output_directory=output_directory,
                video_metadata=inputs["video_metadata"],
            )
     def cleanup(self, outputs: Dict[str, Any]) -> None:
        ...
```

> Every pipeline element is inherited from base class - [`PipelineElement`](src/integration_pipeline/base/pipeline_element.py) and it is highly recommended to use also the base class [`PipelineElementError`](src/integration_pipeline/base/pipeline_element_exceptions.py).

### Pipeline definition file

Once we've decided which pipeline elements we want to use, we should connect them to each other (in a pipeline-style) using [pipeline definition file](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml), where the output of each element is the input of the next one. Please refer to the structure of the aforementioned example pipeline.

### Collecting everything

For reference please use our [example solution](example/mp4_data_converter/) "MP4 data converter". We created the following elements: 
- Validator
- Data Reader
- Tar Archiver
- Redactor
- Tar Extractor
- Data Writer

We also created helper classes to perform operations on data using FFMPEG and tarfile python module - [FFMPEG Executor](example/mp4_data_converter/utils/ffmpeg_executor.py) (for Data Reader and Data Writer) and [Tar Executor](example/mp4_data_converter/utils/tar_executor.py) (for Tar Archiver and Tar Extractor).

To build a pipeline we created the [pipeline definition file](example/mp4_data_converter/integration_pipeline/pipeline_definition.yml). We pass this file and the path to the source code of the pipeline elements to the [main](src/main.py) function.

## Code Style Reference
A "Best of the Best Practices" [(BOBP) guide to developing in Python](https://gist.github.com/sloria/7001839).
### Formatting
Use [`format.sh`](./scripts/format.sh)  to format and check the code for PEP8 compliance


### Type annotations
We use type annotation for most of our code. 
> **_NOTE:_** We do NOT use `Generics` and `parameterized generics` in annotations.
> We use classical syntax. 
> 

For `numpy` arrays type annotations, please see [numpy.typing](https://numpy.org/devdocs/reference/typing.html)

| do this                            | do NOT do this                     |
|:-----------------------------------|:-----------------------------------|
| `Dict[str, int]`                   | `dict[str, int]`                   |
| `Tuple[List[Dict[str, int]], ...]` | `tuple[list[dict[str, int]], ...]` |
| `npt.NDArray[np.uint8]`            | `np.ndarray`                       |

## TODOs

- Cover with tests all example pipeline elements and Yaml Parser
- Add parallel run to Orchestrator
- Add cycle run to Orchestrator (to remove loop inside pipeline elements)
- Add async run to Orchestrator - running a pipeline element in concurrent manner
