from datetime import datetime
import pandas as pd
import os


class logger:
    def __init__(self, log=None) -> None:
        self.log = log if log else []
    
    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

    @staticmethod
    def _filepath(dir, filename, timestamp=True):
        os.makedirs(dir, exist_ok=True)
        if timestamp:
            timestamp = logger._get_timestamp()
            return f"{dir}{timestamp}{filename}"
        else:
            return f"{dir}{filename}"

    def _to_csv(self, dir, filename, verbose, timestamp):
        df = pd.DataFrame(self.log)
        df.reset_index(drop=True, inplace=True)
        file_path = self._filepath(dir=dir,filename=filename, timestamp=timestamp)
        df.to_csv(file_path, index=False)
        self.log = []
        if verbose:
            print(f"{len(df)} logs saved to {file_path}")


class llm_logger(logger):        
    def __init__(self, log=None) -> None:
        super().__init__(log=log)
        
    def __call__(self, input, output):
        self.log.append({"input": input, "output": output})
    
    def to_csv(self, dir: str='data/logs/llm/', filename: str='llm_log.csv', verbose=True, timestamp=True):
        self._to_csv(dir=dir, filename=filename, verbose=verbose, timestamp=timestamp)


class data_logger(logger):
    def __init__(self, log=None) -> None:
        super().__init__(log=log)
        
    def __call__(self, entry):
        self.log.append(entry)
    
    def to_csv(self, dir: str='data/logs/sources/', filename: str='data_log.csv', verbose=True, timestamp=True):
        self._to_csv(dir=dir, filename=filename, verbose=verbose, timestamp=timestamp)


llmlog = llm_logger()
datalog = data_logger()