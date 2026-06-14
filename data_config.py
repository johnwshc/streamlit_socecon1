from config import Config
from pathlib import Path
import pandas as pd


class DataConfig:   #  needs to include data type (GDP, Surplus, Taxation, compensation, subsidies).
    """A configuration class for managing the specific US state (SA) associated with this data."""
    ddir = f"{Path(Config.basedir).as_posix()}"
    registered_states = {'ND': {'GDP': f'{ddir}/json/json_data/SAGDP2_ND_1997_2024.json',
                                'EMP': f'{ddir}/json/bundle.json',
                                'TAX-SUBS': f'{ddir}/data/sagdp/SAGDP3_ND_1997_2024.csv',
                                'COMP': f'data/sagdp/SAGDP4_ND_1997_2024.csv',
                                'SUBS': f'data/sagdp/SAGDP5_ND_1997_2024.csv',
                                'TAX': f'data/sagdp/SAGDP6_ND_1997_2024.csv',
                                'SURPLUS': f'data/sagdp/SAGDP7_ND_1997_2024.csv',
                                'REAL_GDP': f'data/sagdp/SAGDP9_ND_1997_2025.csv',
                                },
                         'ALL': {'EMP': f'{ddir}/json/bundle.json'},
                         'WV': {'GDP': f'{ddir}/data/sagdp/SAGDP2_WV_1997_2025.csv',
                                'EMP': f'{ddir}/json/bundle.json',
                                'TAX-SUBS': f'{ddir}/data/sagdp/SAGDP3_WV_1997_2024.csv',
                                'COMP': f'data/sagdp/SAGDP4_WV_1997_2024.csv',
                                'SUBS': f'data/sagdp/SAGDP5_WV_1997_2024.csv',
                                'TAX': f'data/sagdp/SAGDP6_WV_1997_2024.csv',
                                'SURPLUS': f'data/sagdp/SAGDP7_WV_1997_2024.csv',
                                'REAL_GDP': f'data/sagdp/SAGDP9_WV_1997_2025.csv',
                                },

                         'MN': {'GDP': f'{ddir}/data/sagdp/SAGDP2_MN_1997_2025.csv',
                                },
                         }
    labels = {'EMP': 'Employees',
              'GDP': 'Gross Domestic Product',
              'TAX-SUBS': 'Taxes Minus Subsidies',
              'COMP': 'Compensation of Employees',
              'SUBS': 'Subsidies',
              'TAX': 'Taxes',
              'SURPLUS': 'Surplus',
              'REAL_GDP': 'Real GDP'}

    titles = {'EMP': 'Employment by Industry in Thousands',
              'GDP': 'Gross Domestic Product by Industry  in Millions',
              'TAX-SUBS': 'Taxes Minus Subsidies by Industry in Thousands',
              'COMP': 'Employee Compensation by Industry in Thousands',
              'SUBS': 'Subsidies by Industry in Thousands',
              'TAX': 'Taxes by Industry in Thousands',
              'SURPLUS': 'Surplus by Industry in Thousands',
              'REAL_GDP': 'Real GDP by Industry in Millions of 2017 Dollars'}

    @classmethod
    def get_state_gdp_data(cls, sa_name: str = 'ND', doc='GDP') -> pd.DataFrame:

        from emp_bundles import SAEmpGdpMgr
        if sa_name not in DataConfig.registered_states.keys():
            raise ValueError(f"State {sa_name} not registered in EmpConfig.registered_states.")
        if sa_name == 'ND':
            fn = DataConfig.registered_states[f'{sa_name}'][f'{doc}']
            assert Path(fn).exists(), f"File {fn} does not exist."

            if Path(fn).suffix == '.csv':
                df = pd.read_csv(fn)
                df.drop([92, 93, 94, 95], axis=0, inplace=True)
                return df
            elif Path(fn).suffix == '.json':
                df = pd.read_json(fn)
                if doc != 'EMP':
                     df.drop([92, 93, 94, 95], axis=0, inplace=True)
                return df
            else:
                raise ValueError(f"Unsupported file type for state {sa_name} GDP data: {Path(fn).suffix}")
        elif sa_name in SAEmpGdpMgr.states_name_map.keys():
            fn = DataConfig.registered_states[f'{sa_name}'][f'{doc}']
            assert Path(fn).exists(), f"File {fn} does not exist."
            df = pd.read_csv(fn)
            df.drop([92, 93, 94, 95], axis=0, inplace=True)
            return df
        else:
            raise NotImplementedError(f"State {sa_name} GDP data retrieval not implemented.")