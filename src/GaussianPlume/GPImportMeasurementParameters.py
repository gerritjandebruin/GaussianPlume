"""
Import parameter files.

Parameters can be static or dynamic. Static parameters don't change during the measurement, for example a device used during the measurement. A dynamic parameters do change over time. This can for example be the terrain roughness. 

Measurement data is similar to dynamic parameters, in the sense that it changes over time. Dynamic parameters are intended for things that change a few times during a measurement day. Measurement data has a much higher time resolution, for example every second. 


Excel
=====
Static parameters are stored in a sheet named `static parameters' (the sheet names are important). Column A contains the parameter names, column B the parameter values. If a parameter name or value is missing, it is ignored.

This data:

============ =======
Device       TNO XYZ
Operator      
Stack height 5
============ =======

Will be read as:

============ =======
Device       TNO XYZ
Stack height 5
============ =======

Dynamic parameters are stored in a sheet named "dynamic parameters". Column A contains a time stamp, the other columns the parameters. Row 1 contains the parameter names. The idea is that you only need to fill in the value of the parameter that has changed. If a value is missing, it will use the last valid value, if there is none, it will be set to NaN. 

This data:

================ ========= =========
datetime         Roughness Windspeed
================ ========= =========
02/08/2018 7:00            5
02/08/2018 9:40  C         
02/08/2018 10:33           11
02/08/2018 11:22 E          	
02/08/2018 12:25 F         16
================ ========= =========

Will be read as:

================ ========= =========
datetime         Roughness Windspeed
================ ========= =========
02/08/2018 7:00  **NaN**   5
02/08/2018 9:40  C         **5**
02/08/2018 10:33 **C**     11
02/08/2018 11:22 E         **11**	
02/08/2018 12:25 F         16
================ ========= =========

Technical details
=================
Data is treated as numpy-arrays (ndarrays) or as a number (integer, float). Numpy works similar to Matlab. You can multiply two ndarrays of the same size, to get a ndarray with the same size. You can also multiply an ndarray with a number, to get an ndarray with the same size:

* distance (ndarray with size = n) / windspeed (ndarray with size = n) = time (ndarray with size = n)
* distance (number) / windspeed (ndarray with size = n) = time (ndarray with size = n)
* distance (ndarray with size = n) / windspeed (number) = time (ndarray with size = n)
* distance (number) / windspeed (number) = time (number)




"""

import importlib
import pathlib
import numpy
import pandas
import warnings

def import_measurement_parameters_txt(paf):
    """
    
    
    """
    
    parameters = {}
    array = []
    with open(paf, "r") as F:
        for line in F:
            parse_lines_txt(line, parameters)            
    
    print(parameters)



def parse_lines_txt(line, parameters, array):
    """
    
    
    """
    key, value = line.split(":")

    # remove white spaces at start and end of the string
    key = key.strip()
    value = value.strip()
    
    if value == "start":
        pass

    parameters[key] = value
    
    

def import_measurement_parameters_excel(paf, static_parameters = True, dynamic_parameters = True, verbose = 0):
    """
    
    
    Arguments
    ---------
    paf : pathlib.Path
        Path and filename of the Excel file with parameters
    static_parameters : bool (True) or str
        Read the fixed parameters sheet in the Excel file. If this is a string, it will be used as the sheet name.
    dynamic_parameters : bool (True) or str
        Read the dynamic parameters sheet in the Excel file. If this is a string, it will be used as the sheet name.
    
    Returns
    -------
    Pandas dataframe or None
        DataFrame with static parameters. None if static_parameters is False
    Pandas dataframe or None
        DataFrame with dynamic parameters.None if dynamic_parameters is False
    
    Raises
    ------
    ValueError
        If the sheet name is incorrect.
    UserWarning
        If the file is not found at the paf. 
    
    """
    if verbose > 1:
        print("GPImportMeasurementParameters.import_measurement_parameters_excel()")
    if verbose > 2:
        print("    paf (path and filename): {:}".format(paf))
        print("    static_parameters: {:}".format(static_parameters))
        print("    dynamic_parameters: {:}".format(dynamic_parameters))
    
    if paf.exists() == False:
        warnings.warn("GPImportMeasurementParameters.import_measurement_parameters_excel(): parameter file does not exist (at this location): {:}".format(paf))
        return None, None
    
    with open(paf, "rb") as F:
    
        if static_parameters:
            if type(static_parameters) == str:
                sheetname = static_parameters
            else:
                sheetname = "static parameters"
        
            df_static = pandas.read_excel(F, sheetname, index_col = 0, header = None) 
            
            # transpose data and make a new index
            df_static = df_static.transpose()
            df_static = df_static.reset_index(drop = True)
            
            # remove parameters without a value
            for cl in df_static.columns:
                if pandas.isna(df_static.loc[0,cl]): 
                    df_static.drop(cl, axis=1, inplace = True)            
            
        else:
            df_static = None


        if dynamic_parameters:
            if type(dynamic_parameters) == str:
                sheetname = dynamic_parameters
            else:
                sheetname = "dynamic parameters"        
        
            df_dynamic = pandas.read_excel(F, sheetname, header = 0, parse_dates = ["datetime"]) 
            
            # forward fill data
            df_dynamic.fillna(method = "ffill", inplace = True) 
        else:
            df_dynamic = None
          
    return df_static, df_dynamic
            

    
    
    
    

    

    
    