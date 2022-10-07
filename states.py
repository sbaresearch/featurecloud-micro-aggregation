from FeatureCloud.app.engine.app import AppState, app_state, Role, LogLevel
from FeatureCloud.app.engine.app import State as op_state
from CustomStates import ConfigState
import subprocess
import pandas as pd
from bs4 import BeautifulSoup

# App name
name="fc_anonymization_micro"

# FeatureCloud requires that apps define the at least the 'initial' state.
# This state is executed after the app instance is started.
@app_state('initial', role=Role.BOTH, app_name=name)
class LoadData(ConfigState.State):

    def register(self):
        self.register_transition('WriteAnonymizedData')  

    def run(self):
        self.lazy_init()
        self.read_config()
        self.finalize_config()
        data_file, config_file= self.read_data()
        df_anom=self.anonymized_data(data_file, config_file)
        output_file= f"{self.output_dir}/{self.config['result']['file']}"
        self.store('output_file', output_file)
        self.store('anonymized_data', df_anom)
        return 'WriteAnonymizedData'  

    def read_data(self):
        input_files = self.load('input_files')
        data_file = input_files['data'][0]
        format = data_file.split('.')[-1].strip()
        ontologies_folder="/"
        if format != 'txt':
            self.log(f"The file format {format} is not supported", LogLevel.ERROR)
            self.update(state=op_state.ERROR)
        if "ontologies_folder" in input_files:
            ontologies_folder = input_files['ontologies_folder'][0]
            print(ontologies_folder)
        config_file= input_files['config'][0]
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
        output = subprocess.getoutput(f"java -jar -Xmx1024m -Xms1024m mAnt1.jar {data_file} {config_file} ")
        print(output)
        file = data_file.split('/')[-1]
        file_name= file.split('.')[0] 
        df_anonymized= pd.read_csv(f'{file_name}_anom.txt')
        return df_anonymized
        
@app_state(name='WriteAnonymizedData', role=Role.BOTH)
class WriteResults(AppState):
    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self):
        output_file=self.load('output_file')
        df_anom=self.load('anonymized_data')
        df_anom.to_csv(output_file, index=False)
        print(df_anom.head())
        return 'terminal'