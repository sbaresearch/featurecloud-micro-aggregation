# FeatureCloud Micro-Aggregation App 

## Description
The FeatureCloud Micro-Aggregation App provides the capability for anonymizing datasets using microaggregation algorithms. The app uses the  [Microaggregation-based Anonymization Tool](https://github.com/CrisesUrv/microaggregation-based_anonymization_tool). For more information on the tool, we refer the reader to [[1]](#Resources).

## Input 
- data.csv - containing the original dataset (columns: features; rows: samples)
- ontologies_folder - folder containing the OWL ontologies for semantic attributes.

## Output
- anom_data.csv - containing the anonymized dataset generated with the given anonymization parameters.

## Workflow
Can be combined with the following apps:
- Post: 
  - Preprocessing apps (e.g. Cross-validation, Normalization ...) 
  - Various analysis apps (e.g. Logistic Regression, Linear Regression ...)

## Config  
Use the config file to set the parameters for the anonymization. Upload it together with your data that will be anonymized. 

```
fc_anonymization_micro:
  local_dataset:
    data: data.txt
    config: properties1Adult.xml 
    ontologies_folder: ontologies #Optional
  result:
    file: anom_data.csv
```
### Config File Options 

#### Local dataset
The input data should include a CSV file containing the dataset to be anonymized, an XML file containing the description of the attributes in the dataset and specifying the anonymization parameters and optionally, it can include an ontologies folder where the OWL ontologies for semantic attributes are located. 

The XML configuration file is the main file for anonymization. The user can specify for each attribute: its name, the attribute type and the data type. Similarly, for each attribute type a protection method has to be assigned with their respective parameters. 

The possible attribute types are identifier, quasi-identifier, confidential and non-confidential.

The possible data types include numeric_discrete, numeric_continuous, date, categoric and semantic. For semactic attributes, please provide the name of the file containing the OWL ontology in the ontologies folder. For instance, consider the attribute 'workclass' with an ontology file "workclass-ontology.owl" inside the folder set in the config.yml for ontologies, then in the XML, it should be included as indicated below:

```xml
<attribute
  name="workclass"
  attribute_type="quasi_identifier"
  data_type="semantic"
  ontology="workclass-ontology.owl">
</attribute>
```

The protection methods include: suppression, k-anonymity and t-closeness. For attributes without protection use not.

The XML file structure provided in the sample folder can be used as an example template. For more information about the XML we refer the reader to the original repository of the [Microaggregation-based Anonymization Tool](https://github.com/CrisesUrv/microaggregation-based_anonymization_tool).

#### Result 
The output data should include a CSV file containing the anonymized data.

## Resources

[1]. David Sánchez, Sergio Martínez, Josep Domingo-Ferrer, Jordi Soria-Comas, Montserrat Batet,
[µ-ANT: Semantic Microaggregation-based Anonymization Tool](https://doi.org/10.1093/bioinformatics/btz792), Bioinformatics, 2019.
