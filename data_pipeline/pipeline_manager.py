class DataPipeline:
    def __init__(self, openweather_manager):
        self.manager = openweather_manager

    def extract(self):
        return self.manager.extract_data()

    def transform(self, data):
        return self.manager.transform_data(data)

    def load_to_datalake(self, data):
        self.manager.load_to_datalake(data)

    def load_to_data_warehouse(self, data):
        if isinstance(data, list):
            for data_transformed in data:
                self.manager.load_to_data_warehouse(data_transformed)
        else:
            self.manager.load_to_data_warehouse(data)

    def run(self):
        # Extract
        data = self.extract()

        for data_dict in data:
            # Load to datalake
            self.load_to_datalake(data_dict)

            # Transform
            data_transform = self.transform(data_dict)

            # Load
            self.load_to_data_warehouse(data_transform)
