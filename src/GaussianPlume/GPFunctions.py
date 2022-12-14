import importlib
import pathlib

import warnings

import numpy



import GPConstants as GPC

importlib.reload(GPC)

def latlon2dlatdlon(lat, lon, latR, lonR, warn_distance_above_meter = 100000, verbose = 0, **kwargs):
    """
    Calculate the distance in meter in north-south and east-west direction for two coordinates. 
    
    `lat` and `lon` are the coordinates of a point. `latR` and `lonR` are the coordinates of a reference. 
    
    Latitude is the north-south position (positive is north). Longitude the east-west position (positive is east). 
    
    Input can be a number, ndarray or a list. Output is a number or a ndarray. A list is converted to an ndarray. 
    
    Arguments
    ---------
    lat : number, ndarray, list
        Latitude
    lon : number, ndarray, list
        Longitude
    latR : number, ndarray, list
        Latitude of the reference
    lonR : number, ndarray
        Longitude of the reference
    warn_distance_above_meter : number (100000)
        Give a warning when a distance is above this distance (in meters)
        
    Returns
    -------
    dlat : number or ndarray
        If the point is north of the reference, it is positive
    dlon : number or ndarray
        If the point is east of the reference, it is positive
    
    
    """
    verbose = print_vars(function_name = "GPFunctions.latlon2dlatdlon()", function_vars = vars(), verbose = verbose, self_verbose = 0)   
    
    latlon2dxdy_lon_conversion_factor = kwargs.get("latlon2dxdy_lon_conversion_factor", GPC.latlon2dxdy_lon_conversion_factor)
    latlon2dxdy_lat_conversion_factor = kwargs.get("latlon2dxdy_lat_conversion_factor", GPC.latlon2dxdy_lat_conversion_factor)
    
    
    if type(lat) == list:
        lat = numpy.array(lat)
    if type(lon) == list:
        lon = numpy.array(lon)
    if type(latR) == list:
        latR = numpy.array(latR)
    if type(lonR) == list:
        lonR = numpy.array(lonR)        
    
    dlat = numpy.sin((lat - latR) * GPC.deg2rad) * latlon2dxdy_lat_conversion_factor
    dlon = numpy.cos(lat * GPC.deg2rad) * numpy.sin((lon - lonR) * GPC.deg2rad) * latlon2dxdy_lon_conversion_factor 

    dist = numpy.sqrt(dlat**2 + dlon**2)
    idx = numpy.where(dist > warn_distance_above_meter)[0]
    if len(idx) > 0:
        warnings.warn("GPFunctions.latlon2dlatdlon(): distance is above {:} meter for {:d} data points".format(warn_distance_above_meter, len(idx)))
    
    return dlat, dlon 





def dlatdlon2dxdy(dlatS, dlonS, dlatM, dlonM, wind_direction, warn_distance_above_meter = 100000, verbose = 0):
    """
    Calculate dx and dy.     
    
    Arguments
    ---------
    dlatS : number, ndarray, list
        North-south distance between source and reference, where positive means the source is north of the reference
    dlonS : number, ndarray, list
        East-west distance between source and reference, where positive means the source is east of the reference
    dlatM : number, ndarray, list
        North-south distance between measurement and reference, where positive means the measurement is north of the reference
    dlonM : number, ndarray, list
        East-west distance between measurement and reference, where positive means the measurement is east of the reference
    wind_direction : number, ndarray, list
        Direction from which the wind comes, in degrees
    warn_distance_above_meter : number (100000)
        Give a warning when a distance is above this distance (in meters)
    
    """

    verbose = print_vars(function_name = "GPFunctions.dlatdlon2dxdy()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
    
    if type(dlatS) == list:
        dlatS = numpy.array(dlatS)
    if type(dlonS) == list:
        dlonS = numpy.array(dlonS)
    if type(dlatM) == list:
        dlatM = numpy.array(dlatM)
    if type(dlonM) == list:
        dlonM = numpy.array(dlonM)        
    if type(wind_direction) == list:
        wind_direction = numpy.array(wind_direction)

    dx = (dlatS - dlatM) * numpy.cos(wind_direction * GPC.deg2rad) + (dlonS - dlonM) * numpy.sin(wind_direction * GPC.deg2rad)
    dy = (dlatS - dlatM) * numpy.sin(wind_direction * GPC.deg2rad) - (dlonS - dlonM) * numpy.cos(wind_direction * GPC.deg2rad)
    
    dist = numpy.sqrt(dx**2 + dy**2)
    idx = numpy.where(dist > warn_distance_above_meter)[0]
    if len(idx) > 0:
        warnings.warn("GPFunctions.dlatdlon2dxdy(): distance is above {:} meter for {:d} data points".format(warn_distance_above_meter, len(idx)))
    
    return dx, dy


def get_dispersion_constants(dispersion_mode, verbose = 0):
    """
    Select the right dispersion mode.
    
    Arguments
    ---------
    dispersion_mode : string
        The required mode.
        
    Returns
    -------
    dispersion_constants : ndarray
        A table with constants. Rows are the stability classes, columns the factors. 
    
    """
    verbose = print_vars(function_name = "GPFunctions.get_dispersion_constants()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
    
    return GPC.dispersion_constants(dispersion_mode)


def get_molecule_properties(molecule, verbose = 0):
    """

    Get a dictionary with molecule properties. 
    
    Arguments
    ---------
    molecule : string
        Name of the molecule. 
        
    Returns
    -------
    molecule_properties : dict
        Dictionary with molecule properties
    
    """
    verbose = print_vars(function_name = "GPFunctions.get_molecule_properties()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
    
    return GPC.molecule_properties(molecule)


def calculate_tc(dx, wind_speed, verbose = 0):   
    """
    Calculate the travel time in seconds(?)
    TODO: is this correct?
    
    Arguments
    ---------
    dx : number
        Distance between the source and the measurement in meters. 
    wind_speed : number
        Wind speed in m/s
    
    Returns
    -------
    travel_time : number
        Travel time in seconds. 
    
    """
    verbose = print_vars(function_name = "GPFunctions.calculate_tc()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
    
    return dx / (3600 * wind_speed)


def calculate_sigma(dx, z0, tc, dispersion_constants, stability_index, tc_minimum = 0, offset_sigma_z = 0, verbose = 0, **kwargs):
    """
    Calculate the plume width and height at dx. 
    
    
    
    Arguments
    ---------
    dx : number
        Distance between the source and the measurement in meter
    z0 : number
        Source height in meter
    tc : number
        Travel time between source and measurement in seconds
    ca : number
        Some exponent
    cb : number
        Some exponent
    dispersion_constants : ndarray
        Table with dispersion constants
    stability_index : number
        Index 0-5 for stability, where 0 is most stable.
    
    Returns
    -------
    sigma_y, sigma_z : number
        Values for the disk diameter in y and z direction.
    
    """
    verbose = print_vars(function_name = "GPFunctions.calculate_sigma()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
    
    
    
    if numpy.any(dx < 0):
        idx_nan = numpy.where(dx < 0)[0]
        dx[idx_nan] = numpy.nan
        if type(tc) == numpy.ndarray:
            tc[idx_nan] = numpy.nan        
        
    if type(tc) == numpy.ndarray:
        idx = numpy.where(tc < tc_minimum)[0]
        tc[idx] = tc_minimum
    elif tc < tc_minimum:
        tc = tc_minimum
    
    ca = kwargs.get("ca", GPC.sigma_ca)
    cb = kwargs.get("cb", GPC.sigma_cb)
    # print(dispersion_constants[stability_index[0],1])
    sigma_y = dispersion_constants[stability_index,0] * dx**dispersion_constants[stability_index,1] * (z0**0.2) * (tc**0.35)
    sigma_z = dispersion_constants[stability_index,2] * dx**dispersion_constants[stability_index,3] * (10*z0)**(ca * dx**cb) + offset_sigma_z
 
    return sigma_y, sigma_z





def calculate_concentration(qs, wind_speed, sigma_y, sigma_z, dy, zr, hs, hm, molecular_mass, verbose = 0):
    """
    Calculate the concentration
    
    
    Arguments
    ---------
    Qs : number
        Source strength in gram / second
    wind_speed : number
        Wind speed in m/s.
    sigma_y : number
        Plume width in m. 
    sigma_z : number
        Plume height in m. 
    dy : number
        Distance perpendicular. 
    Zr : number
        Height of the measurement in m. 
    Hs : number
        Height of the source in m. 
    Hm : number
        Height of the mixing layer in m. 
    molecular_mass : number
        Molecular mass in g/mol. 
        
    """
    verbose = print_vars(function_name = "GPFunctions.calculate_concentration()", function_vars = vars(), verbose = verbose, self_verbose = 0)  
        
    A = qs / (2 * numpy.pi * wind_speed * sigma_y * sigma_z)
    B = numpy.exp(-dy**2 / (2 * sigma_y**2))
    C = 2 * sigma_z**2
    D = numpy.exp(-(zr - hs)**2 / C)
    E = numpy.exp(-(zr + hs)**2 / C)
    F = numpy.exp(-(zr - (2 * hm - hs))**2 / C)    
    
    conc = GPC.liter_per_mole_air * 1e6 * A * B * (D + E + F) / molecular_mass
    
    # idx = numpy.where(numpy.absolute(dy) >= numpy.absolute(5*dx))[0]
    # conc[idx] = numpy.nan
    
    
    return conc

    # conc = 
        # 22.36 / MMassa 
        # * 10 ^ 6 
        # * Qs / (2 * Pi * U * sigma_Y * sigma_Z) 
        # * Exp(-dy ^ 2 / (2 * sigma_Y ^ 2)) 
        # * (
            # Exp(-(Zr - Hs) ^ 2 / (2 * sigma_Z ^ 2)) 
            # + Exp(-(Zr + Hs) ^ 2 / (2 * sigma_Z ^ 2)) 
            # + Exp(-(Zr - (2 * Hm - Hs)) ^ 2 / (2 * sigma_Z ^ 2))
        # )

def print_vars(function_name, function_vars, verbose, self_verbose = 0):
    """
    Check the verbose level and print the arguments
    
    Arguments
    ---------
    function_name : str
        The name of the function. 
    function_vars : dict
        Call the vars() function.
    verbose : number
        Verbose level of the function.
    self_verbose : number (0)
        Verbose level of the class, if applicable. Defaults to zero.
        
    Returns
    -------
    int 
        The higher of verbose and self_verbose
        
    """
    if self_verbose > verbose:
        verbose = self_verbose
    
    if verbose > 1:
        print(function_name)           
    if verbose > 2:
        for item in function_vars.items():
            if item[0] == "kwargs":
                print("    kwargs:")  
                for k, v in item[1].items():
                    print("        {:} : {:}".format(k, v))             
            else:
                print("    {:} : {:}".format(item[0], item[1]))    
    
    return verbose


def stability_index2class(stability_index, verbose = 0):
    """
    Convert stability index (0-5) to a stability class (A-F).
    
    Arguments
    ---------
    stability_index : int or ndarray/list with int
        The index 0, 1, 2, 3, 4, or 5
    
    Returns
    -------
    str
        A string or an array with strings with the stability class.
    
    """
    verbose = print_vars(function_name = "GPFunctions.stability_index2class()", function_vars = vars(), verbose = verbose, self_verbose = 0)  


    stability_classes = numpy.array(["A", "B", "C", "D", "E", "F"])
    
    if type(stability_index) == int:
        if stability_index not in range(6):
            raise IndexError("stability_index is {:d}, which is out of range, it has to be 0, 1, 2, 3, 4, or 5.".format(stability_index))
    else:
        if numpy.any(stability_index < 0) or numpy.any(stability_index > 5):
            raise IndexError("stability_index is out of range, it has to be 0, 1, 2, 3, 4, or 5.")
    return stability_classes[stability_index]



def stability_class2index(stability_class, verbose = 0):
    """
    Convert stability class (A-F) to a stability index (0-5).
    
    Arguments
    ---------
    stability_class : str or ndarray with str
        The class A, B, C, D, E, F
    
    Returns
    -------
    int or ndarray with int
        An int or an ndarray with int
    
    """

    verbose = print_vars(function_name = "GPFunctions.stability_class2index()", function_vars = vars(), verbose = verbose, self_verbose = 0)  

    stability_classes = numpy.array(["A", "B", "C", "D", "E", "F"])
    
    if type(stability_class) == str:
        idx = numpy.where(stability_class.upper() == stability_classes)[0]
        if len(idx) == 0:
            raise ValueError("stability_class {:s} does not exist".format(stability_class))
    else:
        if type(stability_class) == list:   
            stability_class = numpy.array(stability_class)
        # idx = numpy.zeros(len(stability_class), dtype = int)
        # for s_i, s in enumerate(stability_class):
            # i = numpy.where(s.upper() == stability_classes)[0]
            # if len(i) == 0:
                # raise ValueError("stability_class {:s} does not exist".format(s))            
            # else:
                # idx[s_i] = i

        idx = numpy.zeros(len(stability_class), dtype = int) - 1
        
        for sc_i, sc in enumerate(stability_classes):
            i = numpy.where(stability_class == sc)[0]
            if len(i) > 0:
                idx[i] = sc_i

            i = numpy.where(stability_class == sc.lower())[0]
            if len(i) > 0:
                idx[i] = sc_i                

        if numpy.any(idx == -1):
            idx_invalid = numpy.where(idx == -1)[0]
            
            if len(idx_invalid) < 3:
                s = "Invalid inputs for stability_class:"
                for i, ii in enumerate(idx_invalid):
                    s = "{:s} {:s}".format(s, stability_class[ii])
                raise ValueError(s) 
            else:
                raise ValueError("{:d} invalid inputs for stability_class".format(len(idx_invalid)))            
    
    return idx

def handle_filename_path(filename = None, path = None, verbose = 0):
    """
    Add the paths and filenames of the parameter files. Note that this function does not check if the path exists or whether it makes sense. 
    
    Arguments
    ---------
    filename : 
        A single filename or list with filenames. The filename(s) may contain the path as well. They must contain the extension. The filename(s) can be a string or a pathlib object. 
    path : None
        A path or a list with paths. Defaults to None, which means the path is not needed or the path is included in the filename(s). The path(s) can be a string or a pathlib object. 
    
    Returns
    -------
    list
        A list with paths and filenames. 
    
    
    Notes
    -----
    There are a number of options:
    
    * filename = 'C:/path/filename.ext', path = None
    
        * ['C:/path/filename.ext']
        
    * filename = ['C:/path/filename.ext'], path = None
    
        * ['C:/path/filename.ext']
    
    * filename = 'filename.ext', path = 'C:/path' 
    
        * ['C:/path/filename.ext']
    
    * filename = ['C:/path_1/filename_1.ext', 'C:/path_1/filename_2.ext']
    
        * ['C:/path_1/filename_1.ext', 'C:/path_1/filename_2.ext']
    
    * filename = ['filename_1.ext', 'filename_2.ext'], path = 'C:/path' 

        * ['C:/path/filename_1.ext', 'C:/path/filename_2.ext']
    
    * filename = ['filename_1.ext', 'filename_2.ext'], path = ['C:/path_1', 'C:/path_2'] 

        * ['C:/path_1/filename_1.ext', 'C:/path_2/filename_2.ext']
    
    The following options are invalid:

    * Lengths are not the same
    
        * filename = ['filename_1.ext', 'filename_2.ext', 'filename_3.ext'], path = ['C:/path_1', 'C:/path_2'] 
        * filename = ['filename_1.ext', 'filename_2.ext'], path = ['C:/path_1', 'C:/path_2', 'C:/path_3'] 

         
    
    
    """
    verbose = print_vars(function_name = "GPFunctions.handle_filename_path()", function_vars = vars(), verbose = verbose, self_verbose = 0)
    
    if filename is None and path is None:
        return None
    
    if type(filename) != list:  
        filename = [filename]
    
    for f_i, fn in enumerate(filename):
        if not isinstance(fn, pathlib.Path):
            filename[f_i] = pathlib.Path(fn)
    
    if path is None:
        return filename
    
    if type(path) == list:
        if len(filename) != len(path):
            raise IndexError("Length of filename ({:d}) and path ({:d}) is not the same.".format(len(filename), len(path)))
        else:
            paf = []
            for p_i, p in enumerate(path):
                if not isinstance(p, pathlib.Path):
                    p = pathlib.Path(p)
                paf.append(p.joinpath(filename[p_i]))
                
    else:
        paf = []
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        for f_i, f in enumerate(filename):
            paf.append(path.joinpath(f))
    
    return paf



if __name__ == '__main__': 
    lat = 53.2835083
    lon = 6.30388
    latR = 53.28375
    lonR = 6.3024917
    wind_direction = 0

    latlon2dlatdlon(lat, lon, latR, lonR)