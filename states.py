from FeatureCloud.app.engine.app import AppState, app_state, Role, LogLevel
from FeatureCloud.app.engine.app import State as op_state
import subprocess
import pandas as pd
import bios
from bs4 import BeautifulSoup

INPUT_DIR = 'mnt/input'
OUTPUT_DIR = 'mnt/output'

INITIAL_STATE = 'initial'
WRITE_STATE = 'Microaggregation'
TERMINAL_STATE = 'terminal'

# App name
app_name="fc_anonymization_micro"

# FeatureCloud requires that apps define the at least the 'initial' state.
# This state is executed after the app instance is started.
@app_state(INITIAL_STATE)
class InitialState(AppState):

    def register(self):
        self.register_transition(WRITE_STATE)  

    def run(self):
        print('Loading config...')
        self.read_config()
        print('Loading data and XML config...')
        data_file, config_file= self.read_data()
        print(config_file)
        df_anom=self.anonymized_data(data_file, config_file)
        output_file= f"{OUTPUT_DIR}/{self.config['result']['file']}"
        self.store('output_file', output_file)
        self.store('anonymized_data', df_anom)
        return 'Microaggregation'  
    
    def read_config(self):
        print(bios.read(f'{INPUT_DIR}/config.yml'))
        self.config = bios.read(f'{INPUT_DIR}/config.yml')[app_name]

    def read_data(self):
        data_file = f"{INPUT_DIR}/{self.config['local_dataset']['data']}"
        format = data_file.split('.')[-1].strip()
        self.store('format_data', format)
        ontologies_folder="/"
        formats=['txt','csv']
        if format not in formats:
            self.log(f"The file format {format} is not supported", LogLevel.ERROR)
            self.update(state=op_state.ERROR)
        if "ontologies_folder" in self.config['local_dataset']:
            ontologies_folder = f"{INPUT_DIR}/{self.config['local_dataset']['ontologies_folder']}"
        config_file = f"{INPUT_DIR}/{self.config['local_dataset']['config']}"
        config_file = self.modify_xml(config_file,ontologies_folder)
        return data_file, config_file
        
        
    def modify_xml(self,config_file,ontologies_folder):
        with open(config_file, 'r') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, 'xml')

        for tag in bs_data.find_all('attribute'):
            ontology_path= tag.get('ontology')
            if ontology_path != None:
                tag['ontology']= f"{ontologies_folder}/{ontology_path.split('/')[-1]}"

        config_file="./config.xml"

        with open(config_file, "w", encoding='utf-8') as file:
            file.write(bs_data.prettify())
        
        return config_file

    def anonymized_data(self,data_file,config_file):
        output = subprocess.getoutput(f"java --add-opens=java.base/java.lang=ALL-UNNAMED -jar -Xmx1024m -Xms1024m mAnt1.jar {data_file} {config_file} ")
        print(output)
        file = data_file.split('/')[-1]
        file_name= file.split('.')[0] 
        format_data=self.load('format_data')
        df_anonymized= pd.read_csv(f'{file_name}_anom.{format_data}')
        return df_anonymized


@app_state(name=WRITE_STATE, role=Role.BOTH)
class Microaggregation(AppState):
    def register(self):
        self.register_transition(TERMINAL_STATE, Role.BOTH)

    def run(self):
        output_file=self.load('output_file')
        df_anom=self.load('anonymized_data')
        df_anom.to_csv(output_file, index=False)
        print("Anonymized Data Successfully Created!")
        print(df_anom.head(10))
        return TERMINAL_STATE