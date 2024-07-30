### DataSegment Form
  
The datasegment format is used by all of our transforms prior to feature extractors as a method for storing data. A datasegment refers to a region of time series sensor data that has been labeled as a segment. The datasegment. The datasegment code can be found in datamanager/datasegments.py.

A single datasegment has the following properties

```
 {
        "columns": <list of columns>,
        "metadata": <dicionary of metadata {name: value}>,
        "statistics": <dictionary of statistcs about the segment>,
        "data": <numpy array of data>,
    }
```
  
Multiple datasegments are stored in a list. This allows us to easily store the datasegments into pickle files and read them out as well. 

There are several helper functions associated with the datasegments format. Specifically, a DataSegments class that takes the datasegments list and has a number of APIs to make converting and applying transforms to it easier. 

Notably, the functions

```python
# Instantiated DataSegments object from the list of datasegments
D = DataSegments(datasegments)

# converst the datasegments to a dataframe
D.to_dataframe() 

# Applies the function to each segment in the datasegment object and returns the feature vector
D.apply( func, **kwargs) 

# generates the summary statistics for the DataSgements stored in the cache as metadata and used by the WebUI to display summary charts. 
D.summary() 
```
