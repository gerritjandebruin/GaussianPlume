"""
To calculate the concentration, the following input is required:

* `Qs`: Source strength in gram / second
* `wind_speed`: Wind speed in m/s.
* `dx`: Distance between the source and the measurement in meters. 
* `dy`: Perpendicular distance between source and measurement in meters
* `z0`: Source height in meters
* `Zr`: Height of the measurement in meters
* `Hs`: Height of the source in meters
* `Hm`: Height of the mixing layer in meters 
* `mode`: select dispersion constants (NOGEPA / farm)
* `stability`: Index 0-5 for stability, where 0 is most stable.
* 'molecular_mass`: Molecular mass in g/mol.

Intermediate calculations are done:

* `sigma_y`: Plume width in meters, calculated from dx, z0, Tc, ca, cb, dispersion_constants, stability
* `sigma_z`: Plume height in meters, calculated from dx, z0, Tc, ca, cb, dispersion_constants, stability
* `Tc`: Travel time between source and measurement in seconds, calculated using dx and wind_speed. 

Some are constants

* `molecule`: A dictionary with the molecule formula, a nice (standardized) name, and the molecular mass in g/mol.
* `ca`: Some exponent used to calculate sigma_y and sigma_z
* `cb`: Some exponent used to calculate sigma_y and sigma_z
* `dispersion_constants`: Table with dispersion constants, selected from mode and stability

"""
import importlib
import pathlib

import GPConstants as GPC
import GPFunctions as GPF
import GPImportData as GPID
import PythonTools.ClassTools as CT

importlib.reload(GPC)
importlib.reload(GPF)
importlib.reload(GPID)

class Plume(CT.ClassTools):
    """
    Arguments
    ---------
    Qs : number-like
        Source strength in gram / second
    wind_speed : number-like
        Wind speed in m/s.
    wind_direction : number-like
        Wind direction in degrees.
    dx : number-like
        Distance between the source and the measurement in meters. This can be set itself, but is recalculated when latS, lonS, latM, and lonM are all set. 
    dy : number-like
        Perpendicular distance between source and measurement in meters
    latS : number-like  
        Latitude of the source.
    lonS : number-like  
        Longitude of the source.
    lonS : number-like  
        Longitude of the source.        
    latM : number-like  
        Latitude of the measurement.
    lonM : number-like  
        Longitude of the measurement.   
    latR : number-like  
        Latitude of the reference.
    lonR : number-like  
        Longitude of the reference.           
    z0 : number-like
        Source height in meters
    Zr : number-like
        Height of the measurement in meters
    Hs : number-like
        Height of the source in meters
    Hm : number-like
        Height of the mixing layer in meters 
    mode : number-like
        Select dispersion constants (NOGEPA / farm)
    stability_index : number-like
        Index 0-5 for stability, where 0 is most stable. If both `stability_index` and `stability_class` are given during initialization, `stability_index` is used. 
    stability_class : str-like
        Class A-F for stability, where A is most stable. If both `stability_index` and `stability_class` are given during initialization, `stability_index` is used.            
    molecular_mass : 
        Molecular mass in g/mol.   
    
    """
    def __init__(self, verbose = 0, **kwargs):
        """

     
        
        """
        self.verbose = verbose
        
        GPF.print_vars(function_name = "GPPlume.Plume.__init__()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)

        self.df = kwargs.get("df", None)

        self.parameter_filename = kwargs.get("parameter_filename", None)
        self.parameter_path = kwargs.get("parameter_path", None)
        self.parameter_paf = GPF.handle_filename_path(filename = self.parameter_filename, path = self.parameter_path, verbose = self.verbose)
        
        self.measurement_filename = kwargs.get("measurement_filename", None)
        self.measurement_path = kwargs.get("measurement_path", None)
        self.measurement_paf = GPF.handle_filename_path(filename = self.measurement_filename, path = self.measurement_path, verbose = self.verbose)

        self.dispersion_constants = kwargs.get("dispersion_constants", None)

        self.molecules = kwargs.get("molecules", None)
        self.molecular_properties = kwargs.get("molecules_properties", None)
        self.molecular_mass = kwargs.get("molecular_mass", None)
        self.mode = kwargs.get("mode", None)
        
        # self.qs = kwargs.get("qs", None)
        # self.wind_speed = kwargs.get("wind_speed", None)
        # self.wind_direction = kwargs.get("wind_direction", None)
        # self.latS = kwargs.get("latS", None)
        # self.lonS = kwargs.get("lonS", None)
        # self.latM = kwargs.get("latM", None)
        # self.lonM = kwargs.get("lonM", None)
        # self.dx = kwargs.get("dx", None)
        # self.dy = kwargs.get("dy", None)
        # self.z0 = kwargs.get("z0", None)
        # self.zr = kwargs.get("zr", None)
        # self.hs = kwargs.get("hs", None)
        # self.hm = kwargs.get("hm", None)

        if "stability_index" in kwargs:
            self.stability_index = kwargs["stability_index"]
        elif "stability_class" in kwargs:
            self.stability_class = kwargs["stability_class"]

    @property
    def stability_index(self):
        """
        Index of the stability class. 0 equals class A, 5 equals class F.
        """
        return self._stability_index

    @stability_index.setter
    def stability_index(self, value):
        self._stability_index = value
        self._stability_class = GPF.stability_index2class(value)

    @property
    def stability_class(self):
        """
        Stability class. Class A equals index 0, class F equals index 5. 
        """    
        return self._stability_class

    @stability_class.setter
    def stability_class(self, value):
        self._stability_class = value
        self._stability_index = GPF.stability_class2index(value) 
    



    def import_data(self, verbose = 0, **kwargs):
        """
        Import static and dynamic parameters, and the measurement data.
        
        Arguments
        ---------
        **kwargs : dict, optional
            May include `parameter_paf`, `measurement_paf`, `static_parameters`, `dynamic_parameters`
        
        Notes
        -----
        There are three ways to give `measurement_paf`, i.e. the list with path-and-filenames of the measurement files.
        
        1. As kwarg when calling this function.
        2. As an defined in the PlumeModel object earlier.
        3. As the parameter `measurement_data_path_and_filename` in the static parameters.
        
        
        
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.import_data()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)

        parameter_paf = kwargs.get("parameter_paf", self.parameter_paf)
        measurement_paf = kwargs.get("measurement_paf", self.measurement_paf)
        
        static_parameters = kwargs.get("static_parameters", True)
        dynamic_parameters = kwargs.get("dynamic_parameters", True)

        df_static, df_dynamic = GPID.import_measurement_parameters_excel(parameter_paf, static_parameters = static_parameters, dynamic_parameters = dynamic_parameters, verbose = verbose)

        if measurement_paf is None:
            measurement_paf = [pathlib.Path(df_static.loc[0,"measurement_data_path_and_filename"])]
        
        self.measurement_paf = measurement_paf

        df = GPID.import_measurement_data(measurement_paf, verbose = verbose)

        self.df = GPID.merge_measurement_static_dynamic_df(df, df_static, df_dynamic, verbose = verbose)
        
        for col_name in self.df.columns:
            if col_name in GPC.implemented_molecules:
                if self.molecules is None:
                    self.molecules = [col_name]
                else:
                    self.molecules.append(col_name)


    
    def calculate_concentration_prepare_dxdy(self, verbose = 0):
        """
        Check if `dx` or `dy` exists in the DataFrame, if either does not exist, calculate `dx` and `dy`.
        
        Raises
        ------
        ValueError
            If `dx` or `dy` does not exist, and "latS" or "lonS" or "latM" or "lonM" or "latR" or "lonR" or "wind_direction" do not exist either.
        
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.calculate_concentration_prepare_dxdy()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)
        
        cn = self.df.columns
        if "dx" not in cn or "dy" not in cn:
            if "latS" in cn and "lonS" in cn and "latM" in cn and "lonM" in cn and "latR" in cn and "lonR" in cn and "wind_direction" in cn:
                dlatM, dlonM = GPF.latlon2dlatdlon(self.df.loc[:,"latM"], self.df.loc[:,"lonM"], self.df.loc[:,"latR"], self.df.loc[:,"lonR"], verbose = verbose)
                dlatS, dlonS = GPF.latlon2dlatdlon(self.df.loc[:,"latS"], self.df.loc[:,"lonS"], self.df.loc[:,"latR"], self.df.loc[:,"lonR"], verbose = verbose)
                dx, dy = GPF.dlatdlon2dxdy(dlatS, dlonS, dlatM, dlonM, self.df.loc[:,"wind_direction"], verbose = verbose)
                
                idx = len(self.df.columns)
                self.df.insert(idx, "dy", dy)
                self.df.insert(idx, "dx", dx)
            else:
                print("GPPlumeModel.calculate_concentration_prepare_dxdy(): dx is missing and can not be calculated.")
                raise ValueError


        
    def calculate_concentration_prepare_tc(self, verbose = 0):
        """
        Check if `tc` exists in the DataFrame, if it doesn't, calculate `tc`.
        
        Raises
        ------
        ValueError
            If `tc` does not exist, and "dx" or "wind_direction" do not exist either.        
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.calculate_concentration_prepare_tc()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)
        
        cn = self.df.columns
        if "tc" not in cn:
            if "dx" in cn and "wind_speed" in cn :
                tc = GPF.calculate_Tc(self.df.loc[:,"dx"], self.df.loc[:,"wind_speed"], verbose = verbose)
                idx = len(self.df.columns)
                self.df.insert(idx, "tc", tc)
            else:
                print("GPPlumeModel.calculate_concentration_prepare_tc(): tc is missing and can not be calculated.")
                raise ValueError        


    def calculate_concentration_prepare_dispersion_constants(self, verbose = 0):
        """
        Check if `dispersion_constants` exists in the DataFrame, if it doesn't, import it from `GPConstants`.
        
        Raises
        ------
        ValueError
            If `dispersion_constants` does not exist, and "mode" does not exist either.          
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.calculate_concentration_prepare_dispersion_constants()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)

        if self.dispersion_constants is None:
            if self.mode is not None:
                self.dispersion_constants = GPF.get_dispersion_constants(mode = self.mode, verbose = verbose)
            else:
                print("GPPlumeModel.calculate_concentration_prepare_dispersion_constants(): dispersion_constants and mode can not be set.")
                raise ValueError      

    def calculate_concentration_get_molecular_properties(self, verbose = 0): 
        """
        Check if `molecular_mass` is set. If it doesn't, import it from `GPConstants`.
        
        Raises
        ------
        ValueError
            If `molecular_mass` does not exist, and "molecules" does not exist either.                  
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.calculate_concentration_get_molecular_weights()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)

        if self.molecules is None or len(self.molecules) == 0:
            print("GPPlumeModel.calculate_concentration_get_molecular_mass(): molecules are not known.")
            raise ValueError  
        
        if self.molecular_mass is None:
            self.molecular_properties = []
            self.molecular_mass = []
            for m_i, m in enumerate(self.molecules):
                m_prop = GPF.get_molecule_properties(m, verbose = verbose)
                self.molecular_properties.append(m_prop)
                self.molecular_mass.append(m_prop["molecular_mass"])


    # def calculate_sigma(self):
        # """
        
        # """

        
        # GPF.calculate_sigma(dx = self.df["x"], z0 = self.df["z0"], Tc = self.df["tc"], dispersion_constants = 1, stability = , verbose = 0, **kwargs)


    def calculate_concentration(self, verbose = 0, **kwargs):
        """
        
        
        """
        verbose = GPF.print_vars(function_name = "GPPlumeModel.calculate_concentration()", function_vars = vars(), verbose = verbose, self_verbose = self.verbose)
        
        self.calculate_concentration_prepare_dxdy(verbose = verbose)
        self.calculate_concentration_prepare_tc(self, verbose = verbose)
        self.calculate_concentration_prepare_dispersion_constants(self, verbose = verbose)
        self.calculate_concentration_get_molecular_properties(self, verbose = verbose)


    
    

        
        
        
        
        






