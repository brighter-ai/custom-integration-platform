# MP4 data converter

## Overview
For a better understanding of the development principles, we created this sample pipeline as a reference, which consists of following elements:

- Validator - making sure that there is a input video
- Data Reader - splitting the video into frames
- Tar Archiver - packing frames into tar-archives
- Redactor - anonymizing packed in archives frames using Redact
- Tar Extractor - extracting anonymized frames from the archives
- Data Writer - creating anonymized video from anonymized frames


This example pipeline could be illustrated as follows:



```mermaid
sequenceDiagram
    participant input
    participant Validation
    participant DataReader
    participant TarArchiver
    participant Redactor
    participant TarExtractor
    participant DataWriter
    participant output
    
    Note over TarArchiver:settings: number_of_files_in_tar
    Note over Redactor:settings: redact_url
    
    input->>Validation:input a directory with a video file
    Note left of Validation:inputs: directory_data_video
    Validation->>Validation:check if directory structure is correct, check if redact is online
    
    input->>DataReader:input a directory with video file
    Note left of DataReader:inputs: directory_data_video
    Note right of DataReader:outputs: directory_extracted_frames
    DataReader->>TarArchiver:ffmpeg - extract frames from a video
    
    Note left of TarArchiver:inputs: directory_extracted_frames
    Note right of TarArchiver:outputs: tar_files_directory
    TarArchiver->>Redactor:packs frames into tar-archives by 100 in each
    
    Note left of Redactor:inputs: tar_files_directory
    Note right of Redactor:outputs: anonymized_tar_files_directory
    Redactor->>TarExtractor:send tar-archives to redact to anonymize, retrieve tar-file with anonymized frames
    
    Note left of TarExtractor:inputs: anonymized_tar_files_directory
    Note right of TarExtractor:outputs: directory_anonymized_frames
    TarExtractor->>DataWriter:extract anonymized frames
    
    Note left of DataWriter:inputs: directory_anonymized_frames
    Note right of DataWriter:outputs: directory_anonymized_data_video
    DataWriter->>output:ffmpeg - create anonymized video, output directory with the video file

```
or as picture:
<p align="center">
  <img src="../../docs/example_pipeline.png" />
</p>

We also created a helper classes to perform operations on data using FFMPEG and tarfile python module - [FFMPEG Executor](utils/ffmpeg_executor.py) (for Data Reader and Data Writer) and [Tar Executor](utils/tar_executor.py) (for Tar Archiver and Tar Extractor).

## Developer guide

If the pipeline structure needs to be changed, or new pipeline elements are needed, please refer to [our developer guide](../../README.md#developer-guide).

## Code Style Reference
A "Best of the Best Practices" [(BOBP) guide to developing in Python](https://gist.github.com/sloria/7001839).
### Formatting
Use [`format.sh`](../../scripts/format.sh)  to format and check the code for PEP8 compliance


### Type annotations
We use type annotation for most of our code. 
> **_NOTE:_** We do NOT use `Generics` and `parameterized generics` in annotations.
> We use classical syntax. 
For `numpy` arrays type annotations, please see [numpy.typing](https://numpy.org/devdocs/reference/typing.html)

| do this                            | do NOT do this                     |
|:-----------------------------------|:-----------------------------------|
| `Dict[str, int]`                   | `dict[str, int]`                   |
| `Tuple[List[Dict[str, int]], ...]` | `tuple[list[dict[str, int]], ...]` |
| `npt.NDArray[np.uint8]`            | `np.ndarray`                       |
